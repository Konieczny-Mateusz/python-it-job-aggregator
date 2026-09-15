# python-it-job-aggregator
Automated ETL pipeline, web scraper, and Flask-based web application for aggregating, cleaning, and categorizing IT job offers from multiple international APIs.

## Gdzie kryją się najlepsze oferty IT? Zautomatyzowana agregacja danych
Projekt "Robota.tej" to kompleksowy system analityczno-aplikacyjny napisany w Pythonie. Jego głównym celem jest automatyczne pobieranie nieustrukturyzowanych danych o ofertach pracy z wielu rozproszonych źródeł (API), ich standaryzacja, kategoryzacja na podstawie słów kluczowych oraz udostępnienie użytkownikowi końcowemu poprzez czytelny interfejs webowy i własne REST API.

System eliminuje problem przeglądania kilkunastu portali z ogłoszeniami, centralizując dane w jednej, łatwej do przeszukiwania relacyjnej bazie danych.

---

## Cel projektu

**Główny cel biznesowy i technologiczny:**
Zbudowanie stabilnego procesu ETL (Extract, Transform, Load), który przetwarza surowe dane z zewnętrznych API w ustrukturyzowaną bazę wiedzy o rynku pracy IT, a następnie serwuje te dane za pomocą aplikacji webowej.

**Kluczowe wyzwania:**
* Jak zintegrować dane o zróżnicowanej strukturze pochodzące z 4 niezależnych platform?
* W jaki sposób automatycznie wykrywać poziom doświadczenia (od Stażysty do C-Level) oraz kategorię IT (Backend, Frontend, AI/ML itp.) na podstawie nieustrukturyzowanego tekstu opinii i tagów?
* Jak wyeliminować powielające się ogłoszenia (duplikaty) publikowane na różnych portalach?
* Jak zaprojektować REST API, aby udostępniać zebrane statystyki i oferty aplikacjom trzecim?

---

## Zakres analizy i źródła danych
System automatycznie odpytuje i przetwarza dane z 4 międzynarodowych portali pracy zdalnej i europejskiej:
* **Arbeitnow.com API**
* **Remotive.io API**
* **RemoteOK API**
* **Landing.jobs API**

Dane są ujednolicane do wspólnego modelu zawierającego m.in.: Tytuł, Firmę, Lokalizację, Wynagrodzenie, Typ umowy, Kategorię IT oraz Poziom Doświadczenia.

---

## Architektura Systemu i Kluczowy Kod

### 1. Ekstrakcja danych (Data Extraction)
Silnik scrapera (`scraper.py`) iteruje po zdefiniowanych endpointach, stosując odpowiednie nagłówki i obsługując błędy połączeń. Dane są pobierane w formacie JSON, a skrypt dba o to, by błąd parsowania jednej oferty nie przerywał całego procesu.

```python
response = requests.get(url, headers=self.headers, timeout=20)
response.raise_for_status()
data = response.json()
```

### 2. Transformacja i Kategoryzacja (NLP & Data Transformation)

Ponieważ zewnętrzne API często nie podają wprost, jakiego poziomu doświadczenia wymaga oferta, skrypt posiada własny silnik mapujący. Analizuje on tytuł, opis i tagi pod kątem występowania specyficznych słów kluczowych (np. "junior", "lead", "sre") przypisując ofertę do jednego ze standardowych koszyków.

```python
def detect_experience_level(self, title, description=''):
    text = (title + ' ' + description).lower()
    for level, keywords in self.EXPERIENCE_LEVELS.items():
        if any(keyword in text for keyword in keywords):
            return level
    return 'Mid/Regular'
```

Dodatkowo proces transformacji normalizuje formaty dat (np. znaczniki czasu Unix) do formatu YYYY-MM-DD oraz ujednolica zapisy lokalizacji. Zestaw jest filtrowany pod kątem duplikatów przy użyciu biblioteki pandas.

### 3. Ładowanie i Zarządzanie Bazą Danych (Data Loading)

Przetworzone dane jako DataFrame (pandas) trafiają do relacyjnej bazy SQLite. Klasa JobDatabase automatycznie inicjalizuje schemat bazy, dodając brakujące kolumny i zapisując nowe rekordy.

### 4. Prezentacja i REST API (Flask Web App)

Frontend oparty na mikroframeworku Flask serwuje zebrane dane z możliwością zaawansowanego filtrowania po słowach kluczowych, lokalizacji, poziomie czy technologii. Aplikacja udostępnia również publiczne endpointy JSON /api/jobs oraz /api/statistics tworząc własne API (Backend-as-a-Service).

## Funkcjonalności Aplikacji (Data Storytelling)

- Rozpoznawanie technologii: System jest "świadomy" 22 kluczowych kategorii IT (od Embedded, przez DevOps, po Product Management). Pozwala to na śledzenie, na jakie specjalizacje jest aktualnie największy popyt.
- Statystyki Rynku Pracy: Aplikacja automatycznie generuje podsumowania analityczne – m.in. top 10 najpopularniejszych lokalizacji, czy podział ofert ze względu na źródło i poziom doświadczenia, wykonując agregacje bezpośrednio w języku SQL.
- Bezpieczeństwo Środowiska: W repozytorium znajduje się moduł reset_database_py.py, który w bezpieczny sposób nadzoruje resetowanie bazy w środowisku produkcyjnym/testowym.

## Technologie i Umiejętności

### Technologie

- Język: Python 3.x
- Data Processing: pandas
- Web Scraping & API: requests
- Backend & Routing: Flask
- Baza Danych: SQLite (SQL)
- Web Design: HTML/CSS + Szablony Jinja2

### Umiejętności zaprezentowane w projekcie

- Projektowanie i implementacja procesów ETL (Extract, Transform, Load).
- Komunikacja z zewnętrznymi interfejsami API oraz obsługa formatu JSON.
- Czyszczenie danych i standaryzacja tekstu (kategoryzacja oparta o słowniki).
- Budowa i zarządzanie relacyjnymi bazami danych (SQL).
- Projektowanie architektury klient-serwer przy użyciu frameworka Flask.

## Struktura repozytorium

```text
python-it-job-aggregator/
├── README.md
├── .gitignore
│
└── src/
    ├── app.py                      # Główny plik serwera Flask i API
    ├── database.py                 # Klasa zarządzająca bazą danych SQLite
    ├── scraper.py                  # Silnik ETL (skrypt pobierający dane z API)
    ├── reset_database_py.py        # Narzędzie administracyjne do bazy
    │
    ├── static/                     # Folder z plikami styli
    │   └── style.css
    │
    └── templates/                  # Folder z widokami HTML
        ├── index.html
        ├── offers.html
        └── statistics.html
```

### Projekt i wykonanie

Projekt zbudowany jako element portfolio prezentujący praktyczne umiejętności inżynierii danych, automatyzacji (Python) oraz podstaw tworzenia backendu aplikacji internetowych.

**Mateusz**  
*Aspiring Data Analyst | Power BI | SQL | Python | Excel | R*
