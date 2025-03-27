import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from jinja2 import Template
from datetime import datetime
import json

class PageAudit(BaseModel):
    url: str
    has_schema: bool
    has_json_ld: bool
    headings_structure: Dict[str, int]
    faq_sections: List[str]
    recommendations: List[str]
    content_analysis: Dict[str, Any]
    suggested_fixes: List[Dict[str, Any]]
    schema_analysis: Dict[str, Any]

class LLMAuditor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Definicje typów schema.org i ich wymaganych pól
        self.schema_types = {
            'Article': {
                'required': ['headline', 'author', 'datePublished'],
                'recommended': ['description', 'image', 'publisher']
            },
            'Product': {
                'required': ['name', 'description', 'offers'],
                'recommended': ['image', 'brand', 'review']
            },
            'Organization': {
                'required': ['name', 'url'],
                'recommended': ['logo', 'contactPoint', 'address']
            },
            'WebPage': {
                'required': ['name', 'description'],
                'recommended': ['publisher', 'dateModified']
            },
            'FAQPage': {
                'required': ['mainEntity'],
                'recommended': ['description']
            }
        }

    def analyze_schema(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Szczegółowa analiza danych strukturalnych schema.org."""
        schema_data = {
            'has_schema': False,
            'has_json_ld': False,
            'found_types': [],
            'missing_required': [],
            'recommendations': []
        }

        # Sprawdzanie JSON-LD
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        if json_ld_scripts:
            schema_data['has_json_ld'] = True
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        schema_type = data.get('@type')
                        if schema_type:
                            schema_data['found_types'].append(schema_type)
                            # Sprawdzanie wymaganych pól
                            if schema_type in self.schema_types:
                                for required in self.schema_types[schema_type]['required']:
                                    if required not in data:
                                        schema_data['missing_required'].append({
                                            'type': schema_type,
                                            'field': required
                                        })
                except:
                    continue

        # Sprawdzanie mikrodanych
        microdata = soup.find_all(attrs={"itemtype": True})
        if microdata:
            schema_data['has_schema'] = True
            for item in microdata:
                itemtype = item.get('itemtype', '').split('/')[-1]
                if itemtype:
                    schema_data['found_types'].append(itemtype)
                    # Sprawdzanie wymaganych pól
                    if itemtype in self.schema_types:
                        for required in self.schema_types[itemtype]['required']:
                            if not item.find(attrs={"itemprop": required}):
                                schema_data['missing_required'].append({
                                    'type': itemtype,
                                    'field': required
                                })

        # Generowanie rekomendacji
        if not schema_data['has_schema'] and not schema_data['has_json_ld']:
            schema_data['recommendations'].append({
                'type': 'basic',
                'description': 'Dodaj podstawowe dane strukturalne schema.org',
                'code': '''
<script type="application/ld+json">
{
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "Tytuł strony",
    "description": "Opis strony",
    "publisher": {
        "@type": "Organization",
        "name": "Nazwa organizacji",
        "logo": {
            "@type": "ImageObject",
            "url": "URL logo"
        }
    },
    "dateModified": "2024-01-01"
}
</script>
'''
            })

        # Rekomendacje dla brakujących wymaganych pól
        for missing in schema_data['missing_required']:
            schema_type = missing['type']
            field = missing['field']
            if schema_type in self.schema_types:
                example = self.get_schema_example(schema_type, field)
                if example:
                    schema_data['recommendations'].append({
                        'type': 'missing_field',
                        'description': f'Dodaj wymagane pole "{field}" dla typu {schema_type}',
                        'code': example
                    })

        return schema_data

    def get_schema_example(self, schema_type: str, field: str) -> str:
        """Generuje przykładowy kod dla danego pola schema.org."""
        examples = {
            'Article': {
                'headline': '{"@type": "Article", "headline": "Tytuł artykułu"}',
                'author': '{"@type": "Article", "author": {"@type": "Person", "name": "Imię Nazwisko"}}',
                'datePublished': '{"@type": "Article", "datePublished": "2024-01-01"}'
            },
            'Product': {
                'name': '{"@type": "Product", "name": "Nazwa produktu"}',
                'description': '{"@type": "Product", "description": "Szczegółowy opis produktu"}',
                'offers': '{"@type": "Product", "offers": {"@type": "Offer", "price": "99.99", "priceCurrency": "PLN"}}'
            },
            'Organization': {
                'name': '{"@type": "Organization", "name": "Nazwa organizacji"}',
                'url': '{"@type": "Organization", "url": "https://www.example.com"}'
            },
            'WebPage': {
                'name': '{"@type": "WebPage", "name": "Tytuł strony"}',
                'description': '{"@type": "WebPage", "description": "Opis strony"}'
            },
            'FAQPage': {
                'mainEntity': '''
{
    "@type": "FAQPage",
    "mainEntity": [{
        "@type": "Question",
        "name": "Pytanie?",
        "acceptedAnswer": {
            "@type": "Answer",
            "text": "Odpowiedź."
        }
    }]
}
'''
            }
        }
        return examples.get(schema_type, {}).get(field, '')

    def analyze_page(self, url: str) -> PageAudit:
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Analiza struktury nagłówków
            headings = {
                'h1': len(soup.find_all('h1')),
                'h2': len(soup.find_all('h2')),
                'h3': len(soup.find_all('h3'))
            }
            
            # Szczegółowa analiza schema.org
            schema_analysis = self.analyze_schema(soup)
            
            # Wyszukiwanie sekcji FAQ
            faq_sections = []
            for section in soup.find_all(['div', 'section']):
                if 'faq' in section.get('class', []) or 'faq' in section.get('id', '').lower():
                    faq_sections.append(section.get_text(strip=True))
            
            # Analiza treści
            content_analysis = {
                'paragraphs': len(soup.find_all('p')),
                'lists': len(soup.find_all(['ul', 'ol'])),
                'images': len(soup.find_all('img')),
                'links': len(soup.find_all('a')),
                'word_count': len(soup.get_text().split())
            }
            
            # Generowanie rekomendacji
            recommendations = []
            if headings['h1'] == 0:
                recommendations.append("Dodaj nagłówek H1")
            elif headings['h1'] > 1:
                recommendations.append("Upewnij się, że masz tylko jeden nagłówek H1 na stronie")
            
            if headings['h2'] == 0:
                recommendations.append("Dodaj nagłówki H2 do lepszej strukturyzacji treści")
            
            if not schema_analysis['has_schema'] and not schema_analysis['has_json_ld']:
                recommendations.append("Dodaj dane strukturalne schema.org")
            
            if content_analysis['paragraphs'] < 3:
                recommendations.append("Rozbuduj treść strony - dodaj więcej paragrafów")
            
            if content_analysis['lists'] == 0:
                recommendations.append("Dodaj listy wypunktowane lub numerowane dla lepszej czytelności")
            
            if content_analysis['images'] == 0:
                recommendations.append("Dodaj obrazy do wizualnego wzbogacenia treści")
            
            if content_analysis['word_count'] < 300:
                recommendations.append("Rozbuduj treść - strona powinna zawierać minimum 300 słów")
            
            if not faq_sections:
                recommendations.append("Dodaj sekcję FAQ z najczęściej zadawanymi pytaniami")
            
            if content_analysis['links'] < 3:
                recommendations.append("Dodaj więcej linków wewnętrznych do powiązanych treści")
            
            # Generowanie poprawek
            suggested_fixes = schema_analysis['recommendations']
            
            return PageAudit(
                url=url,
                has_schema=schema_analysis['has_schema'],
                has_json_ld=schema_analysis['has_json_ld'],
                headings_structure=headings,
                faq_sections=faq_sections,
                recommendations=recommendations,
                content_analysis=content_analysis,
                suggested_fixes=suggested_fixes,
                schema_analysis=schema_analysis
            )
            
        except Exception as e:
            print(f"Błąd podczas analizy strony {url}: {str(e)}")
            return None

    def generate_html_report(self, audit: PageAudit, output_file: str):
        """Generowanie raportu HTML."""
        template = Template('''
<!DOCTYPE html>
<html>
<head>
    <title>Raport audytu LLM - {{ audit.url }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; }
        h3 { color: #2980b9; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f5f5f5; }
        .recommendation { margin: 10px 0; }
        .fix { background-color: #f8f9fa; padding: 10px; margin: 10px 0; }
        .schema-type { color: #2c3e50; font-weight: bold; }
        .missing-field { color: #e74c3c; }
        .required-field { color: #c0392b; font-weight: bold; }
        .recommended-field { color: #27ae60; }
        .field-description { color: #7f8c8d; font-size: 0.9em; }
        .status-missing { background-color: #fde8e8; }
        .status-present { background-color: #e8f5e9; }
        .schema-details { margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
        .field-info { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>Raport audytu LLM dla {{ audit.url }}</h1>
    
    <h2>Podstawowe informacje</h2>
    <table>
        <tr>
            <th>Schema.org</th>
            <td>{{ "Tak" if audit.has_schema else "Nie" }}</td>
        </tr>
        <tr>
            <th>JSON-LD</th>
            <td>{{ "Tak" if audit.has_json_ld else "Nie" }}</td>
        </tr>
        <tr>
            <th>Liczba słów</th>
            <td>{{ audit.content_analysis.word_count }}</td>
        </tr>
    </table>
    
    <h2>Analiza Schema.org</h2>
    {% if audit.schema_analysis.found_types %}
    <h3>Znalezione typy danych:</h3>
    <ul>
    {% for type in audit.schema_analysis.found_types %}
        <li class="schema-type">{{ type }}</li>
    {% endfor %}
    </ul>
    {% endif %}
    
    <h3>Wymagane pola dla każdego typu:</h3>
    <table>
        <tr>
            <th>Typ</th>
            <th>Pole</th>
            <th>Status</th>
            <th>Opis</th>
        </tr>
        {% for type in audit.schema_analysis.found_types %}
            {% if type in auditor.schema_types %}
                {% for required in auditor.schema_types[type].required %}
                <tr class="{{ 'status-missing' if {'type': type, 'field': required} in audit.schema_analysis.missing_required else 'status-present' }}">
                    <td>{{ type }}</td>
                    <td class="required-field">{{ required }}</td>
                    <td>{{ 'Brakuje' if {'type': type, 'field': required} in audit.schema_analysis.missing_required else 'Obecne' }}</td>
                    <td class="field-description">{{ auditor.get_field_description(type, required) }}</td>
                </tr>
                {% endfor %}
                {% for recommended in auditor.schema_types[type].recommended %}
                <tr>
                    <td>{{ type }}</td>
                    <td class="recommended-field">{{ recommended }}</td>
                    <td>Zalecane</td>
                    <td class="field-description">{{ auditor.get_field_description(type, recommended) }}</td>
                </tr>
                {% endfor %}
            {% endif %}
        {% endfor %}
    </table>
    
    {% if audit.schema_analysis.missing_required %}
    <h3>Brakujące wymagane pola:</h3>
    <ul>
    {% for missing in audit.schema_analysis.missing_required %}
        <li class="missing-field">{{ missing.type }} - {{ missing.field }}</li>
    {% endfor %}
    </ul>
    {% endif %}
    
    <h2>Rekomendacje</h2>
    {% for rec in audit.recommendations %}
    <div class="recommendation">• {{ rec }}</div>
    {% endfor %}
    
    <h2>Sugerowane poprawki</h2>
    {% for fix in audit.suggested_fixes %}
    <div class="fix">
        <h3>{{ fix.type }}</h3>
        <p>{{ fix.description }}</p>
        <pre><code>{{ fix.code }}</code></pre>
    </div>
    {% endfor %}
</body>
</html>
''')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template.render(audit=audit, auditor=self))

    def get_field_description(self, schema_type: str, field: str) -> str:
        """Zwraca opis pola schema.org."""
        descriptions = {
            'Article': {
                'headline': 'Główny tytuł artykułu',
                'author': 'Autor artykułu (osoba lub organizacja)',
                'datePublished': 'Data publikacji artykułu',
                'description': 'Krótki opis artykułu',
                'image': 'Główny obraz artykułu',
                'publisher': 'Wydawca artykułu'
            },
            'Product': {
                'name': 'Nazwa produktu',
                'description': 'Szczegółowy opis produktu',
                'offers': 'Informacje o ofercie (cena, dostępność)',
                'image': 'Zdjęcie produktu',
                'brand': 'Marka produktu',
                'review': 'Recenzje produktu'
            },
            'Organization': {
                'name': 'Nazwa organizacji',
                'url': 'Strona główna organizacji',
                'logo': 'Logo organizacji',
                'contactPoint': 'Informacje kontaktowe',
                'address': 'Adres organizacji'
            },
            'WebPage': {
                'name': 'Tytuł strony',
                'description': 'Opis zawartości strony',
                'publisher': 'Wydawca strony',
                'dateModified': 'Data ostatniej modyfikacji'
            },
            'FAQPage': {
                'mainEntity': 'Lista pytań i odpowiedzi',
                'description': 'Ogólny opis sekcji FAQ'
            }
        }
        return descriptions.get(schema_type, {}).get(field, 'Brak opisu')

def main():
    auditor = LLMAuditor()
    url = input("Podaj URL strony do analizy: ")
    result = auditor.analyze_page(url)
    
    if result:
        print("\nRaport z analizy:")
        print(f"URL: {result.url}")
        print(f"Schema.org: {'Tak' if result.has_schema else 'Nie'}")
        print(f"JSON-LD: {'Tak' if result.has_json_ld else 'Nie'}")
        
        if result.schema_analysis['found_types']:
            print("\nZnalezione typy danych Schema.org:")
            for type in result.schema_analysis['found_types']:
                print(f"- {type}")
        
        if result.schema_analysis['missing_required']:
            print("\nBrakujące wymagane pola:")
            for missing in result.schema_analysis['missing_required']:
                print(f"- {missing['type']}: {missing['field']}")
        
        print("\nStruktura nagłówków:")
        for heading, count in result.headings_structure.items():
            print(f"{heading}: {count}")
        print("\nAnaliza treści:")
        print(f"Liczba paragrafów: {result.content_analysis['paragraphs']}")
        print(f"Liczba list: {result.content_analysis['lists']}")
        print(f"Liczba obrazów: {result.content_analysis['images']}")
        print(f"Liczba linków: {result.content_analysis['links']}")
        print(f"Liczba słów: {result.content_analysis['word_count']}")
        print("\nRekomendacje:")
        for rec in result.recommendations:
            print(f"- {rec}")
        
        # Generowanie raportu
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = f"raport_{timestamp}.html"
        
        auditor.generate_html_report(result, html_file)
        print(f"\nRaport został wygenerowany: {html_file}")

if __name__ == "__main__":
    main() 