import requests
import pandas as pd
from datetime import datetime
import time
import random
from database import JobDatabase


class JobScraper:
    """Klasa do scrapowania ofert pracy z prawdziwych API."""

    # Definicje poziomów doświadczenia
    EXPERIENCE_LEVELS = {
        'Praktykant/Stażysta': ['intern', 'internship', 'praktykant', 'staż', 'trainee', 'apprentice'],
        'Asystent': ['assistant', 'asystent', 'associate'],
        'Junior': ['junior', 'jr', 'entry', 'entry-level', 'graduate', 'młodszy'],
        'Mid/Regular': ['mid', 'regular', 'middle', 'średni'],
        'Senior': ['senior', 'sr', 'starszy', 'advanced', 'experienced'],
        'Ekspert': ['expert', 'specialist', 'principal', 'staff', 'ekspert', 'specjalista'],
        'Kierownik': ['team lead', 'lead', 'tech lead', 'kierownik'],
        'Manager': ['manager', 'menedżer', 'head of'],
        'Dyrektor': ['director', 'dyrektor', 'vp', 'vice president'],
        'Prezes': ['cto', 'ceo', 'cio', 'chief', 'prezes', 'president', 'c-level']
    }

    # Definicje kategorii stanowisk
    JOB_CATEGORIES = {
        'Backend': ['backend', 'back-end', 'back end', 'server side', 'api developer'],
        'Frontend': ['frontend', 'front-end', 'front end', 'react', 'angular', 'vue', 'web developer'],
        'Full-stack': ['fullstack', 'full-stack', 'full stack'],
        'Mobile': ['mobile', 'android', 'ios', 'react native', 'flutter', 'swift', 'kotlin'],
        'Architecture': ['architect', 'solution architect', 'system architect', 'software architect'],
        'DevOps': ['devops', 'dev ops', 'sre', 'site reliability', 'infrastructure', 'cloud engineer'],
        'Game dev': ['game', 'unity', 'unreal', 'game developer', 'game designer'],
        'Data Analytics & BI': ['data analyst', 'business intelligence', 'bi analyst', 'analytics', 'tableau',
                                'power bi'],
        'Big Data / Data Science': ['data scientist', 'data engineer', 'big data', 'machine learning engineer',
                                    'ml engineer', 'hadoop', 'spark'],
        'Embedded': ['embedded', 'firmware', 'iot', 'hardware'],
        'QA/Testing': ['qa', 'quality assurance', 'tester', 'test', 'automation tester'],
        'Security': ['security', 'cybersecurity', 'infosec', 'information security', 'pentester'],
        'Helpdesk': ['helpdesk', 'help desk', 'support', 'technical support', 'it support'],
        'Product Management': ['product manager', 'product owner', 'po', 'product management'],
        'Project Management': ['project manager', 'pm', 'pmo', 'project management'],
        'Agile': ['scrum master', 'agile coach', 'agile'],
        'UX/UI': ['ux', 'ui', 'user experience', 'user interface', 'designer', 'product designer'],
        'Business Analytics': ['business analyst', 'business analysis', 'analityk biznesowy'],
        'System Analytics': ['system analyst', 'systems analyst', 'analityk systemowy'],
        'SAP & ERP': ['sap', 'erp', 'oracle', 'dynamics'],
        'IT Admin': ['system administrator', 'sysadmin', 'network administrator', 'administrator', 'it admin'],
        'AI/ML': ['artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning', 'neural network'],
        'Inne': []
    }

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        self.companies_cache = {}

    def format_date(self, date_value):
        """Konwertuje różne formaty dat na YYYY-MM-DD"""
        if not date_value:
            return datetime.now().strftime('%Y-%m-%d')

        if isinstance(date_value, str):
            if 'T' in date_value:
                return date_value.split('T')[0]
            if len(date_value) == 10 and date_value.count('-') == 2:
                return date_value
            try:
                timestamp = int(date_value)
                return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            except:
                return datetime.now().strftime('%Y-%m-%d')

        if isinstance(date_value, (int, float)):
            try:
                return datetime.fromtimestamp(date_value).strftime('%Y-%m-%d')
            except:
                return datetime.now().strftime('%Y-%m-%d')

        return datetime.now().strftime('%Y-%m-%d')

    def detect_experience_level(self, title, description=''):
        """Wykrywa poziom doświadczenia"""
        text = (title + ' ' + description).lower()

        for level, keywords in self.EXPERIENCE_LEVELS.items():
            if any(keyword in text for keyword in keywords):
                return level

        return 'Mid/Regular'

    def detect_job_category(self, title, description='', tags=None):
        """Wykrywa kategorię stanowiska"""
        text = (title + ' ' + description).lower()

        if tags:
            text += ' ' + ' '.join([str(tag).lower() for tag in tags])

        for category, keywords in self.JOB_CATEGORIES.items():
            if category == 'Inne':
                continue
            if any(keyword in text for keyword in keywords):
                return category

        return 'Inne'

    def scrape_arbeitnow(self):
        """Pobiera oferty z Arbeitnow API"""
        print("Zbieranie danych z Arbeitnow.com API...")
        jobs = []

        try:
            url = 'https://www.arbeitnow.com/api/job-board-api'
            print(f"  Wysyłam request do: {url}")

            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()

            data = response.json()
            offers_data = data.get('data', [])[:30]

            print(f"  Otrzymano {len(offers_data)} ofert z API")

            for idx, offer in enumerate(offers_data, 1):
                try:
                    title = offer.get('title', 'Brak tytułu')
                    company_name = offer.get('company_name', 'Nie podano')
                    location = offer.get('location', 'Remote')
                    url_offer = offer.get('url', 'https://www.arbeitnow.com')

                    posted_date = self.format_date(offer.get('created_at'))

                    job_types = offer.get('job_types', [])
                    employment_type = job_types[0].capitalize() if job_types else 'Full-time'

                    tags = offer.get('tags', [])
                    description = offer.get('description', '')

                    experience_level = self.detect_experience_level(title, description)
                    category = self.detect_job_category(title, description, tags)

                    if tags:
                        tech_tags = ', '.join(tags[:5])
                        description = f"Technologie: {tech_tags}. " + (description[:200] if description else '')
                    elif description:
                        description = description[:300]
                    else:
                        description = f"Oferta pracy w {company_name}"

                    is_remote = offer.get('remote', False)
                    if is_remote and location.lower() != 'remote':
                        location = f"{location} (Remote)"

                    jobs.append({
                        'title': title,
                        'company': company_name,
                        'location': location,
                        'salary': 'Nie podano',
                        'employment_type': employment_type,
                        'experience_level': experience_level,
                        'category': category,
                        'source': 'Arbeitnow.com',
                        'url': url_offer,
                        'posted_date': posted_date,
                        'description': description
                    })
                except Exception as e:
                    print(f"  ⚠ Błąd oferty #{idx}: {e}")
                    continue

            print(f"  ✓ Przetworzono {len(jobs)} ofert z Arbeitnow")
        except Exception as e:
            print(f"  ✗ Błąd Arbeitnow: {e}")

        time.sleep(random.uniform(1, 2))
        return jobs

    def scrape_remotive(self):
        """Pobiera oferty z Remotive API"""
        print("Zbieranie danych z Remotive.io API...")
        jobs = []

        try:
            url = 'https://remotive.com/api/remote-jobs'
            print(f"  Wysyłam request do: {url}")

            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()

            data = response.json()
            offers = data.get('jobs', [])[:30]

            print(f"  Otrzymano {len(offers)} ofert z Remotive")

            for idx, offer in enumerate(offers, 1):
                try:
                    title = offer.get('title', 'Brak tytułu')
                    company_name = offer.get('company_name', 'Nie podano')
                    location = offer.get('candidate_required_location', 'Worldwide')
                    salary = offer.get('salary', 'Nie podano')

                    job_type = offer.get('job_type', 'full-time')
                    type_mapping = {
                        'full-time': 'Pełny etat',
                        'part-time': 'Część etatu',
                        'contract': 'Kontrakt',
                        'freelance': 'Freelance'
                    }
                    employment_type = type_mapping.get(job_type, 'Pełny etat')

                    url_offer = offer.get('url', 'https://remotive.com')
                    posted_date = self.format_date(offer.get('publication_date'))

                    category = offer.get('category', '')
                    tags = offer.get('tags', [])

                    experience_level = self.detect_experience_level(title, category)
                    job_category = self.detect_job_category(title, category, tags)

                    if tags:
                        description = f"Kategoria: {category}. Technologie: {', '.join(tags[:5])}"
                    elif category:
                        description = f"Kategoria: {category}"
                    else:
                        description = f"Praca zdalna w {company_name}"

                    jobs.append({
                        'title': title,
                        'company': company_name,
                        'location': location,
                        'salary': salary,
                        'employment_type': employment_type,
                        'experience_level': experience_level,
                        'category': job_category,
                        'source': 'Remotive.io',
                        'url': url_offer,
                        'posted_date': posted_date,
                        'description': description
                    })
                except Exception as e:
                    print(f"  ⚠ Błąd oferty #{idx}: {e}")
                    continue

            print(f"  ✓ Przetworzono {len(jobs)} ofert z Remotive")
        except Exception as e:
            print(f"  ✗ Błąd Remotive: {e}")

        time.sleep(random.uniform(1, 2))
        return jobs

    def scrape_remoteok(self):
        """Pobiera oferty z RemoteOK API"""
        print("Zbieranie danych z RemoteOK API...")
        jobs = []

        try:
            url = 'https://remoteok.com/api'
            print(f"  Wysyłam request do: {url}")

            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()

            data = response.json()
            offers = data[1:31] if len(data) > 1 else []

            print(f"  Otrzymano {len(offers)} ofert z RemoteOK")

            for idx, offer in enumerate(offers, 1):
                try:
                    title = offer.get('position', 'Brak tytułu')
                    company_name = offer.get('company', 'Nie podano')
                    location = offer.get('location', 'Worldwide')

                    salary_min = offer.get('salary_min')
                    salary_max = offer.get('salary_max')

                    if salary_min and salary_max:
                        salary = f"${salary_min} - ${salary_max}"
                    elif salary_min:
                        salary = f"od ${salary_min}"
                    else:
                        salary = 'Nie podano'

                    url_offer = offer.get('url', f"https://remoteok.com/remote-jobs/{offer.get('id', '')}")
                    posted_date = self.format_date(offer.get('date'))

                    tags = offer.get('tags', [])
                    description_text = f"Technologie: {', '.join(tags[:5])}" if tags else f"Praca zdalna w {company_name}"

                    experience_level = self.detect_experience_level(title, description_text)
                    category = self.detect_job_category(title, description_text, tags)

                    jobs.append({
                        'title': title,
                        'company': company_name,
                        'location': location,
                        'salary': salary,
                        'employment_type': 'Remote',
                        'experience_level': experience_level,
                        'category': category,
                        'source': 'RemoteOK',
                        'url': url_offer,
                        'posted_date': posted_date,
                        'description': description_text
                    })
                except Exception as e:
                    print(f"  ⚠ Błąd oferty #{idx}: {e}")
                    continue

            print(f"  ✓ Przetworzono {len(jobs)} ofert z RemoteOK")
        except Exception as e:
            print(f"  ✗ Błąd RemoteOK: {e}")

        time.sleep(random.uniform(1, 2))
        return jobs

    def get_landing_company_name(self, company_id):
        """Pobiera nazwę firmy z Landing.jobs"""
        if company_id in self.companies_cache:
            return self.companies_cache[company_id]

        try:
            url = f'https://landing.jobs/api/v1/companies/{company_id}.json'
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                company_data = response.json()
                company_name = company_data.get('name', f'Company #{company_id}')
                self.companies_cache[company_id] = company_name
                return company_name
        except:
            pass

        return f'Tech Company #{company_id}'

    def scrape_landing_jobs(self):
        """Pobiera oferty z Landing.jobs API"""
        print("Zbieranie danych z Landing.jobs API...")
        jobs = []

        try:
            urls_to_try = [
                'https://landing.jobs/api/v1/jobs.json?limit=30',
                'https://landing.jobs/api/v1/offers?limit=30',
                'https://api.landing.jobs/v1/jobs?limit=30'
            ]

            data = None
            for url in urls_to_try:
                try:
                    print(f"  Próba: {url}")
                    response = requests.get(url, headers=self.headers, timeout=20)

                    if response.status_code == 200:
                        data = response.json()
                        print(f"  ✓ Sukces z: {url}")
                        break
                    else:
                        print(f"  ✗ Status {response.status_code}")
                except Exception as e:
                    print(f"  ✗ Błąd: {e}")
                    continue

            if not data:
                print("  ⚠ Wszystkie endpointy Landing.jobs zawiodły")
                return jobs

            if isinstance(data, list):
                offers = data[:30]
            elif isinstance(data, dict):
                offers = (data.get('jobs') or data.get('offers') or
                          data.get('results') or data.get('data') or [])[:30]
            else:
                offers = []

            print(f"  Otrzymano {len(offers)} ofert z Landing.jobs")

            for idx, offer in enumerate(offers, 1):
                try:
                    title = offer.get('title') or offer.get('name') or 'Brak tytułu'

                    company_id = offer.get('company_id')
                    company_name = (offer.get('company_name') or
                                    (offer.get('company', {}).get('name') if isinstance(offer.get('company'),
                                                                                        dict) else None) or
                                    offer.get('companyName') or offer.get('employer'))

                    if not company_name and company_id:
                        company_name = self.get_landing_company_name(company_id)
                    elif not company_name:
                        company_name = 'Tech Company Europe'

                    location_data = offer.get('city') or offer.get('location') or offer.get('locations')
                    if isinstance(location_data, dict):
                        location = location_data.get('name', 'Remote')
                    elif isinstance(location_data, list) and location_data:
                        location = location_data[0].get('name', 'Remote') if isinstance(location_data[0],
                                                                                        dict) else str(location_data[0])
                    elif isinstance(location_data, str):
                        location = location_data
                    else:
                        location = offer.get('country_name', 'Europe')

                    salary_min = offer.get('salary_from') or offer.get('salaryFrom') or offer.get('min_salary')
                    salary_max = offer.get('salary_to') or offer.get('salaryTo') or offer.get('max_salary')
                    currency = offer.get('currency') or offer.get('currency_code', 'EUR')

                    if salary_min and salary_max:
                        salary = f"{salary_min} - {salary_max} {currency}"
                    elif salary_min:
                        salary = f"od {salary_min} {currency}"
                    else:
                        salary = 'Nie podano'

                    url_offer = (offer.get('url') or offer.get('link') or
                                 f"https://landing.jobs/jobs/{offer.get('id', '')}" if offer.get('id') else
                                 'https://landing.jobs')

                    date_value = (offer.get('published_at') or offer.get('created_at') or
                                  offer.get('date') or offer.get('posted_at'))
                    posted_date = self.format_date(date_value)

                    contract_type = offer.get('contract_type') or offer.get('type') or offer.get('employment_type')
                    if contract_type:
                        type_mapping = {
                            'permanent': 'Umowa o pracę',
                            'contract': 'Kontrakt',
                            'freelance': 'Freelance',
                            'full-time': 'Pełny etat',
                            'part-time': 'Część etatu'
                        }
                        employment_type = type_mapping.get(str(contract_type).lower(), str(contract_type).capitalize())
                    else:
                        employment_type = 'Pełny etat'

                    description = (offer.get('description') or offer.get('summary') or
                                   offer.get('about') or f"Oferta pracy w {company_name}")
                    if len(description) > 300:
                        description = description[:300]

                    experience_level = self.detect_experience_level(title, description)
                    category = self.detect_job_category(title, description)

                    jobs.append({
                        'title': title,
                        'company': company_name,
                        'location': location,
                        'salary': salary,
                        'employment_type': employment_type,
                        'experience_level': experience_level,
                        'category': category,
                        'source': 'Landing.jobs',
                        'url': url_offer,
                        'posted_date': posted_date,
                        'description': description
                    })
                except Exception as e:
                    print(f"  ⚠ Błąd oferty #{idx}: {e}")
                    continue

            print(f"  ✓ Przetworzono {len(jobs)} ofert z Landing.jobs")
        except Exception as e:
            print(f"  ✗ Błąd Landing.jobs: {e}")

        time.sleep(random.uniform(1, 2))
        return jobs

    def scrape_all(self):
        """Zbiera dane ze wszystkich źródeł"""
        all_jobs = []

        print("\n" + "=" * 70)
        print("  ROZPOCZYNAM POBIERANIE OFERT Z 4 DZIAŁAJĄCYCH PORTALI")
        print("  Wszystkie oferty IT")
        print("  Po 30 ofert z każdego portalu = maksymalnie 120 ofert")
        print("=" * 70 + "\n")

        all_jobs.extend(self.scrape_arbeitnow())
        all_jobs.extend(self.scrape_remotive())
        all_jobs.extend(self.scrape_remoteok())
        all_jobs.extend(self.scrape_landing_jobs())

        print("\n" + "=" * 70)
        if all_jobs:
            print(f"✓ SUKCES! Zebrano {len(all_jobs)} ofert z internetu")

            sources = {}
            for job in all_jobs:
                source = job['source']
                sources[source] = sources.get(source, 0) + 1

            print("\nOferty według źródła:")
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {source}: {count} ofert")

            print("\nPrzykładowe oferty (pierwsze 3):")
            for i, job in enumerate(all_jobs[:3], 1):
                print(f"\n  {i}. {job['title']}")
                print(f"     Firma: {job['company']}")
                print(f"     Lokalizacja: {job['location']}")
                print(f"     Wynagrodzenie: {job['salary']}")
                print(f"     Typ umowy: {job['employment_type']}")
                print(f"     Źródło: {job['source']}")
        else:
            print("⚠ UWAGA: Nie udało się pobrać żadnych ofert")

        print("=" * 70 + "\n")

        if all_jobs:
            df = pd.DataFrame(all_jobs)
            df = df.drop_duplicates(subset=['title', 'company'], keep='first')
            return df
        else:
            return pd.DataFrame(columns=[
                'title', 'company', 'location', 'salary', 'employment_type',
                'experience_level', 'category', 'source', 'url', 'posted_date', 'description'
            ])


def main():
    """Główna funkcja uruchamiająca scraper."""
    print("\n" + "=" * 70)
    print("  SYSTEM ROBOTA.TEJ - AGREGACJA OFERT PRACY")
    print("  Pobieranie prawdziwych ofert z międzynarodowych portali")
    print("=" * 70 + "\n")

    scraper = JobScraper()
    db = JobDatabase()

    clear = input("Czy wyczyścić bazę danych przed dodaniem nowych ofert? (t/n): ")
    if clear.lower() == 't':
        db.clear_database()
        print("✓ Baza danych wyczyszczona.\n")

    df = scraper.scrape_all()

    if not df.empty:
        print("Zapisywanie ofert do bazy danych...")
        db.save_jobs(df)
        print("✓ Dane zapisane pomyślnie!\n")

        print("=" * 70)
        print("  PODSUMOWANIE")
        print("=" * 70)
        stats = db.get_statistics()
        print(f"Łączna liczba ofert w bazie: {stats['total_jobs']}")

        print("\nOferty według źródła:")
        for item in stats['by_source']:
            print(f"  ✓ {item['source']}: {item['count']} ofert")

        print("\nTop 5 lokalizacji:")
        for item in stats['by_location'][:5]:
            print(f"  • {item['location']}: {item['count']} ofert")

        print("\n" + "=" * 70)
        print("✅ GOTOWE! Uruchom aplikację webową: python app.py")
        print("=" * 70 + "\n")
    else:
        print("\n" + "=" * 70)
        print("⚠ BRAK DANYCH")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    main()