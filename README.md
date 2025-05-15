# NextListen
Aplikacja umożliwiająca jooużytkownikowi odkrywanie nowej muzyki poprzez rekomendacje oparte na jego historii słuchania w Spotify, poziomie eksperymentalności, gatunku muzyki oraz interakcji z systemem rekomendacji.

<a href="https://www.notion.so/NextListen-1ea5d256e98f80459af9c8f0930128ee" target="_blank">Notion</a>

# Konfiguracja projektu

## Instalacja
1. Pull
2. w backend (cd /backend )
3. konsola → pip install -r requirements-dev.txt
4. powrót do folderu głównego - cd ../
5. pre-commit install

### Backend (Python)
Zainstaluj zależności:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate     # Windows
   pip install -r requirements-dev.txt
   ```

# Formatowanie kodu (automatyczne)
1. Plik .pre-commit-config.yaml kofiguruje narzędzia sprawdzające i fomratujące kod
2. W plikach danych narzędzi możemy znaleźć ustawione konfiguracje dla danych środowisk/języków
3. Black - format w pyrhonie; Flake8 - błędy formatu w pytonie; ESLint - sprawdza błędy w JavaScript; Prettier - formatuje JavaScript, CSS, JSON.
4. !!! PLIK .editorconfig W VS CODE DZIAŁA TYLKO Z ROZSZERZENIEM "EditorConfig for VS code" !!! - plik ten zmienia ustawienia edytora
