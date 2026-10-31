# Cocktail API

REST API built with Django REST Framework and PostgreSQL. Cocktails have a many-to-many relationship with ingredients through a recipe model that stores each ingredient's amount and unit.

## Setup on Windows

Run these commands from the parent folder that contains `.venv` and `cocktail-api`:

```powershell
Copy-Item .\cocktail-api\.env.example .\cocktail-api\.env
```

Edit `cocktail-api\.env` and set `DB_PASSWORD` to the password for the PostgreSQL user. Keep `.env` private; it is ignored by Git.

Install dependencies and prepare the database:

```powershell
Set-Location .\cocktail-api
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`. The browsable Django REST Framework interface can be opened in a browser.

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET, POST | `/api/cocktails/` | List cocktails or create one |
| GET, PUT, PATCH, DELETE | `/api/cocktails/{id}/` | Read, replace, edit, or delete a cocktail |
| GET, POST | `/api/ingredients/` | List ingredients or create one |
| GET, PUT, PATCH, DELETE | `/api/ingredients/{id}/` | Read, replace, edit, or delete an ingredient |

Cocktail lists accept `name` and `category` filters. Ingredient lists accept `name` and `is_alcoholic=true|false`. Both lists accept `page` and `page_size` (maximum 100). Responses use the shape `count`, `next`, `previous`, and `results`.

Unknown filters and invalid filter or pagination values return HTTP 400. Cocktail ingredients require a positive amount, a unit, and a valid ingredient ID; duplicate ingredients in one recipe are rejected. Sending `ingredients` in a cocktail update replaces the recipe; omitting it in a PATCH leaves the recipe unchanged.
An ingredient used by a cocktail cannot be deleted until it is removed from every recipe; that request returns HTTP 409.

Example cocktail request:

```json
{
  "name": "Mojito",
  "category": "Classic",
  "instructions": "Muddle the mint, add the other ingredients, and stir.",
  "ingredients": [
    { "ingredient_id": 1, "amount": "50.000", "unit": "ml" },
    { "ingredient_id": 2, "amount": "20.000", "unit": "ml" }
  ]
}
```

Example ingredient request:

```json
{
  "name": "White rum",
  "description": "Light rum used in cocktails.",
  "is_alcoholic": true,
  "image_url": "https://example.com/white-rum.jpg"
}
```

## Tests

Tests can be run with SQLite, without changing the PostgreSQL configuration in `.env`:

```powershell
$env:DB_ENGINE = "django.db.backends.sqlite3"
$env:DB_NAME = ":memory:"
..\.venv\Scripts\python.exe manage.py test
Remove-Item Env:\DB_ENGINE
Remove-Item Env:\DB_NAME
```
