# Cocktail API

REST API do zarządzania koktajlami i składnikami. Aplikacja umożliwia tworzenie, wyświetlanie, edytowanie i usuwanie danych, a także filtrowanie i stronicowanie list. Do przechowywania danych używa PostgreSQL.

## Spis treści

- [Technologie](#technologie)
- [Jak działa aplikacja](#jak-działa-aplikacja)
- [Model danych](#model-danych)
- [Uruchomienie lokalne w Windows](#uruchomienie-lokalne-w-windows)
- [Endpointy API](#endpointy-api)
- [Przykładowe żądania](#przykładowe-żądania)
- [Walidacja i zachowanie API](#walidacja-i-zachowanie-api)
- [Testy](#testy)
- [Struktura projektu](#struktura-projektu)

## Technologie

- **Python** — język, w którym napisany jest backend.
- **Django** — framework do budowy aplikacji internetowych.
- **Django REST Framework** — obsługa endpointów REST, walidacji danych i odpowiedzi JSON.
- **PostgreSQL** — relacyjna baza danych.
- **Docker** — uruchamia PostgreSQL w kontenerze, bez instalowania serwera bazy bezpośrednio w Windowsie.
- **psycopg** — sterownik łączący Django z PostgreSQL.

## Jak działa aplikacja

Klient (na przykład przeglądarka, `curl` lub frontend) wysyła żądanie HTTP do endpointu API. Django REST Framework kieruje je do odpowiedniego widoku, serializer sprawdza otrzymane dane, a Django zapisuje lub odczytuje dane z PostgreSQL. Odpowiedź API jest zwracana jako JSON.

Przykładowy przebieg tworzenia koktajlu:

1. Najpierw klient tworzy składniki i otrzymuje ich identyfikatory.
2. W żądaniu tworzącym koktajl wysyła jego nazwę, kategorię, instrukcję oraz identyfikatory składników wraz z ilościami i jednostkami.
3. API sprawdza poprawność danych i zapisuje koktajl oraz pozycje przepisu w bazie.
4. API zwraca utworzony koktajl wraz z pełnymi danymi składników i ich ilościami.

## Model danych

- **Ingredient** — nazwa, opis, informacja, czy składnik jest alkoholowy, oraz opcjonalny URL zdjęcia.
- **Cocktail** — nazwa, kategoria i instrukcja przygotowania.
- **CocktailIngredient** — łączy koktajl ze składnikiem i przechowuje ilość oraz jednostkę, na przykład `50.000 ml`.

Koktajl może zawierać wiele składników, a składnik może być używany w wielu koktajlach. Jest to relacja wiele-do-wielu z dodatkową tabelą `CocktailIngredient`, ponieważ sama relacja musi również przechowywać ilość i jednostkę. Składnika używanego w przepisie nie można usunąć, dopóki jest powiązany z koktajlem.

## Uruchomienie lokalne w Windows

### Wymagania

- Python 3.12 lub nowszy;
- Docker Desktop z działającym silnikiem Docker;
- PowerShell.

### 1. Pobierz projekt i przejdź do folderu

```powershell
git clone https://github.com/kchmiel0wski/cocktail-api.git
Set-Location .\cocktail-api
```

Jeśli projekt jest już pobrany, wystarczy otworzyć jego folder w VS Code i wybrać **Terminal → New Terminal**.

### 2. Utwórz środowisko Pythona i zainstaluj zależności

W terminalu, będąc w folderze projektu, wykonaj:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Środowisko `.venv` przechowuje biblioteki używane przez ten projekt i nie jest częścią repozytorium.

### 3. Utwórz lokalną konfigurację

```powershell
Copy-Item .env.example .env
```

Otwórz plik `.env` w edytorze i ustaw `DB_PASSWORD` na własne, lokalne hasło bazy. Wygeneruj również nowy klucz Django:

```powershell
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Wklej wygenerowaną wartość po `DJANGO_SECRET_KEY=` w `.env`. Pozostałe wartości mogą pozostać bez zmian dla lokalnego uruchomienia.

**Nie publikuj `.env` ani nie wysyłaj go innym osobom.** Plik jest wykluczony z Git przez `.gitignore`; `.env.example` zawiera wyłącznie przykładowe wartości.

### 4. Uruchom PostgreSQL w Dockerze

Upewnij się, że Docker Desktop działa. Poniższe polecenie tworzy kontener i wolumen na dane bazy. Plik `.env` dostarcza PostgreSQL nazwę bazy, użytkownika i ustawione przed chwilą hasło:

```powershell
docker run --name cocktail-postgres --restart unless-stopped --env-file .env -p 5432:5432 -v cocktail_pgdata:/var/lib/postgresql/data -d postgres:17
```

Sprawdź, czy baza przyjmuje połączenia:

```powershell
docker exec cocktail-postgres pg_isready -U cocktail_user -d cocktails
```

Oczekiwany komunikat zawiera `accepting connections`.

Jeśli kontener `cocktail-postgres` już istnieje, nie twórz go ponownie. Uruchom go poleceniem `docker start cocktail-postgres`. Wolumen `cocktail_pgdata` przechowuje dane pomiędzy zatrzymaniami i ponownymi uruchomieniami kontenera.

### 5. Utwórz tabele i uruchom API

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Serwer działa, dopóki terminal z `runserver` pozostaje otwarty. Zatrzymuje się go skrótem **Ctrl+C**. Przy kolejnych uruchomieniach wystarczy uruchomić Docker Desktop, w razie potrzeby wykonać `docker start cocktail-postgres`, a następnie uruchomić `runserver`. `migrate` wykonuje się ponownie, gdy dodano nowe migracje.

API i przeglądalny interfejs Django REST Framework są dostępne pod:

- <http://127.0.0.1:8000/api/>
- <http://127.0.0.1:8000/api/cocktails/>
- <http://127.0.0.1:8000/api/ingredients/>

Domyślnie serwer deweloperski jest dostępny tylko lokalnie i nie publikuje API w internecie.

## Endpointy API

| Metoda | Endpoint | Działanie |
| --- | --- | --- |
| `GET` | `/api/cocktails/` | Lista koktajli |
| `POST` | `/api/cocktails/` | Utworzenie koktajlu |
| `GET` | `/api/cocktails/{id}/` | Szczegóły koktajlu |
| `PUT` | `/api/cocktails/{id}/` | Zastąpienie danych koktajlu i przepisu |
| `PATCH` | `/api/cocktails/{id}/` | Częściowa edycja koktajlu |
| `DELETE` | `/api/cocktails/{id}/` | Usunięcie koktajlu |
| `GET` | `/api/ingredients/` | Lista składników |
| `POST` | `/api/ingredients/` | Utworzenie składnika |
| `GET` | `/api/ingredients/{id}/` | Szczegóły składnika |
| `PUT` | `/api/ingredients/{id}/` | Zastąpienie danych składnika |
| `PATCH` | `/api/ingredients/{id}/` | Częściowa edycja składnika |
| `DELETE` | `/api/ingredients/{id}/` | Usunięcie składnika, jeśli nie jest używany w przepisie |

### Filtrowanie i paginacja

- Koktajle: `name`, `category`.
- Składniki: `name`, `is_alcoholic` (`true` lub `false`).
- Obie listy: `page` (domyślnie 1) i `page_size` (domyślnie 10, maksymalnie 100).

Przykłady:

```text
GET /api/cocktails/?name=mojito&category=Classic
GET /api/ingredients/?is_alcoholic=false&page=1&page_size=20
```

Odpowiedź listy ma pola `count`, `next`, `previous` i `results`.

## Przykładowe żądania

Najpierw utwórz składniki przez `POST /api/ingredients/`. Przykładowe ciało żądania:

```json
{
  "name": "White rum",
  "description": "Light rum used in cocktails.",
  "is_alcoholic": true,
  "image_url": "https://example.com/white-rum.jpg"
}
```

API zwróci identyfikator składnika. Użyj identyfikatorów istniejących składników przy tworzeniu koktajlu:

```json
{
  "name": "Mojito",
  "category": "Classic",
  "instructions": "Muddle the mint, add the other ingredients, and stir.",
  "ingredients": [
    { "ingredient_id": 1, "amount": "50.000", "unit": "ml" },
    { "ingredient_id": 2, "amount": "10.000", "unit": "leaves" }
  ]
}
```

Żądanie wysyła się metodą `POST` na `/api/cocktails/` z nagłówkiem `Content-Type: application/json`. Przeglądalny interfejs pod adresem API pozwala również testować operacje w przeglądarce.

## Walidacja i zachowanie API

- Wymagane pola modelu muszą być podane; `image_url` i opis składnika mogą być puste.
- URL zdjęcia musi być poprawnym adresem URL.
- Ilość składnika musi być większa od zera, jednostka musi być podana, a `ingredient_id` musi wskazywać istniejący składnik.
- Ten sam składnik można podać tylko raz w jednym przepisie.
- Koktajl musi zawierać co najmniej jeden składnik podczas tworzenia lub wysyłania listy składników w aktualizacji.
- `PATCH` koktajlu bez pola `ingredients` nie zmienia przepisu. Jeśli `ingredients` zostanie podane, zastępuje dotychczasowe pozycje przepisu.
- Nieznane filtry, błędne wartości filtrów oraz niepoprawne parametry paginacji zwracają `400 Bad Request`.
- Próba usunięcia składnika używanego w przepisie zwraca `409 Conflict`. Najpierw usuń go z przepisów.
- Nieistniejący identyfikator zasobu zwraca `404 Not Found`.

## Testy

Testy używają tymczasowej bazy SQLite w pamięci, więc nie modyfikują lokalnej bazy PostgreSQL. W PowerShellu, w folderze projektu, wykonaj:

```powershell
$env:DB_ENGINE = "django.db.backends.sqlite3"
$env:DB_NAME = ":memory:"
.\.venv\Scripts\python.exe manage.py test
Remove-Item Env:\DB_ENGINE
Remove-Item Env:\DB_NAME
```

## Struktura projektu

```text
config/                 Konfiguracja Django i główne adresy URL
cocktails/
  migrations/           Zmiany schematu bazy danych
  models.py             Modele koktajlu, składnika i pozycji przepisu
  serializers.py        Walidacja oraz konwersja danych JSON
  views.py              Obsługa żądań API, filtrowanie i CRUD
  pagination.py         Walidowana paginacja list
  urls.py               Endpointy koktajli i składników
  tests.py              Testy API
.env.example            Przykładowa lokalna konfiguracja
requirements.txt        Zależności Pythona
manage.py               Polecenia administracyjne Django
```
