# LLM Website Auditor

Narzędzie do audytu i optymalizacji stron internetowych pod kątem wyszukiwarek opartych na modelach językowych (LLM).

## 🚀 Funkcje

- Analiza struktury strony (nagłówki, sekcje, treść)
- Sprawdzanie implementacji Schema.org
- Analiza treści i metryk strony
- Generowanie szczegółowych raportów HTML
- Rekomendacje optymalizacji
- Przykładowe implementacje Schema.org

## 📋 Wymagania

- Python 3.8+
- Zainstalowane zależności z pliku `requirements.txt`

## 🛠️ Instalacja

### Metoda 1: Pobieranie bezpośrednie

1. Pobierz pliki projektu:
   - Pobierz plik `llm_auditor.py`
   - Pobierz plik `requirements.txt`
   - Pobierz plik `README.md`

2. Utwórz nowy folder dla projektu i umieść w nim pobrane pliki

3. Otwórz terminal w folderze projektu i zainstaluj zależności:
```bash
pip install -r requirements.txt
```

### Metoda 2: Przez Git (opcjonalnie)

1. Zainstaluj Git ze strony: https://git-scm.com/download/win

2. Otwórz PowerShell lub Command Prompt i wykonaj:
```bash
git clone https://github.com/szymon-podstawski/seo_llm_audit.git
cd seo_llm_audit
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## 💻 Użycie

1. Uruchom skrypt:
```bash
python llm_auditor.py
```

2. Podaj URL strony do analizy gdy zostaniesz o to poproszony.

3. Poczekaj na wygenerowanie raportu.

## 📊 Raport

Raport zawiera:
- Podstawowe informacje o stronie
- Analizę implementacji Schema.org
- Wymagane i zalecane pola dla każdego typu danych
- Rekomendacje optymalizacji
- Sugerowane poprawki z przykładowym kodem

## 🔍 Przykładowa analiza Schema.org

Narzędzie sprawdza następujące typy danych:
- Article (Artykuł)
- Product (Produkt)
- Organization (Organizacja)
- WebPage (Strona internetowa)
- FAQPage (Sekcja FAQ)

## 🤝 Współpraca

Zapraszamy do współpracy! Jeśli chcesz dodać nowe funkcje lub poprawić istniejące:

1. Fork repozytorium
2. Utwórz nowy branch (`git checkout -b feature/nowa-funkcja`)
3. Zatwierdź zmiany (`git commit -am 'Dodano nową funkcję'`)
4. Wypchnij zmiany (`git push origin feature/nowa-funkcja`)
5. Utwórz Pull Request

## 📝 Licencja

Ten projekt jest licencjonowany na warunkach licencji MIT - zobacz plik [LICENSE](LICENSE) dla szczegółów.

## 📞 Kontakt

Jeśli masz pytania lub sugestie, utwórz issue w repozytorium GitHub. 