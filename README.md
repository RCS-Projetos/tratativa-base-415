# tratativa-de-bases-ssw

Flask app → scrape SSW (report 415) → manage commissions.

## Tech

* Flask (web)
* SQLite (DB)
* Playwright (scrape)
* Pandas (Excel/CSV parse)

## Features

* Auth → login/logout.
* Import Vendedores (Excel/CSV).
* Scrape SSW (req 415) → Playwright automation.
* Save Comissões → SQLite DB.
* Export Vendedores/Comissões (Excel).

## Setup

```bash
uv sync
```

## Run Local

```bash
uv run main.py
```

App start → port `5000`. Local secret in `main.py`.
