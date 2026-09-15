from flask import Flask, render_template, request, jsonify
from database import JobDatabase
import pandas as pd

app = Flask(__name__)
db = JobDatabase()


@app.route('/')
def index():
    """Strona główna aplikacji."""
    stats = db.get_statistics()
    return render_template('index.html', stats=stats)


@app.route('/offers')
def offers():
    """Strona z listą ofert pracy z możliwością filtrowania."""
    # Pobranie parametrów filtrowania z URL
    keyword = request.args.get('keyword', '').strip()
    location = request.args.get('location', '').strip()
    source = request.args.get('source', '').strip()
    experience_level = request.args.get('experience', '').strip()
    category = request.args.get('category', '').strip()

    # Filtrowanie ofert
    if keyword or location or source or experience_level or category:
        df = db.filter_jobs(
            keyword=keyword if keyword else None,
            location=location if location else None,
            source=source if source else None,
            experience_level=experience_level if experience_level else None,
            category=category if category else None
        )
    else:
        df = db.get_all_jobs()

    # Konwersja DataFrame do listy słowników
    jobs = df.to_dict('records') if not df.empty else []

    # Pobranie unikalnych wartości dla filtrów
    all_jobs_df = db.get_all_jobs()
    sources = sorted(all_jobs_df['source'].unique().tolist()) if not all_jobs_df.empty else []
    locations = sorted(all_jobs_df['location'].unique().tolist()) if not all_jobs_df.empty else []

    # Poziomy doświadczenia - pełna lista
    experience_levels = [
        'Praktykant/Stażysta', 'Asystent', 'Junior', 'Mid/Regular', 'Senior',
        'Ekspert', 'Kierownik', 'Manager', 'Dyrektor', 'Prezes'
    ]

    # Kategorie stanowisk - pełna lista
    categories = [
        'Backend', 'Frontend', 'Full-stack', 'Mobile', 'Architecture', 'DevOps',
        'Game dev', 'Data Analytics & BI', 'Big Data / Data Science', 'Embedded',
        'QA/Testing', 'Security', 'Helpdesk', 'Product Management', 'Project Management',
        'Agile', 'UX/UI', 'Business Analytics', 'System Analytics', 'SAP & ERP',
        'IT Admin', 'AI/ML', 'Inne'
    ]

    return render_template('offers.html',
                           jobs=jobs,
                           sources=sources,
                           locations=locations,
                           experience_levels=experience_levels,
                           categories=categories,
                           filters={
                               'keyword': keyword,
                               'location': location,
                               'source': source,
                               'experience': experience_level,
                               'category': category
                           })


@app.route('/statistics')
def statistics():
    """Strona ze statystykami ofert pracy."""
    stats = db.get_statistics()
    return render_template('statistics.html', stats=stats)


@app.route('/api/jobs')
def api_jobs():
    """API endpoint zwracający oferty w formacie JSON."""
    keyword = request.args.get('keyword')
    location = request.args.get('location')
    source = request.args.get('source')
    experience_level = request.args.get('experience')
    category = request.args.get('category')

    df = db.filter_jobs(
        keyword=keyword,
        location=location,
        source=source,
        experience_level=experience_level,
        category=category
    )

    return jsonify({
        'count': len(df),
        'jobs': df.to_dict('records')
    })


@app.route('/api/statistics')
def api_statistics():
    """API endpoint zwracający statystyki w formacie JSON."""
    stats = db.get_statistics()
    return jsonify(stats)


@app.template_filter('format_salary')
def format_salary(salary):
    """Filtr do formatowania wynagrodzenia."""
    if pd.isna(salary) or salary == '' or salary is None:
        return 'Nie podano'
    return str(salary)


@app.template_filter('truncate_text')
def truncate_text(text, length=150):
    """Filtr do skracania długiego tekstu."""
    if pd.isna(text) or text is None:
        return ''
    text = str(text)
    if len(text) <= length:
        return text
    return text[:length] + '...'


if __name__ == '__main__':
    print("=== System Robota.tej - Aplikacja Webowa ===")
    print("Uruchamianie serwera Flask...")
    print("Aplikacja dostępna pod adresem: http://127.0.0.1:5000")
    print("\nDostępne endpointy:")
    print("  - / (strona główna)")
    print("  - /offers (lista ofert z filtrowaniem)")
    print("  - /statistics (statystyki)")
    print("  - /api/jobs (API JSON)")
    print("  - /api/statistics (API JSON statystyki)")
    print("\nAby zatrzymać serwer, naciśnij Ctrl+C")

    app.run(debug=True, host='0.0.0.0', port=5000)