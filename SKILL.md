---
name: swapi-dashboard
description: Scrape the Star Wars API (swapi.tech) and generate an interactive Plotly dashboard. Fetches all 6 endpoints (people, planets, films, starships, species, vehicles), pulls detail records, and produces a dark-themed 6-panel HTML dashboard.
---

# SWAPI Dashboard

Scrape https://swapi.tech/ and render an interactive Plotly dashboard with a Star Wars dark theme.

## What gets scraped

| Endpoint | Records |
|---|---|
| `/api/films` | 6 films |
| `/api/people` | 82 characters |
| `/api/planets` | 60 planets |
| `/api/starships` | 36 starships |
| `/api/species` | 37 species |
| `/api/vehicles` | 39 vehicles |

## Steps

### 1. Fetch list endpoints

```bash
curl -s "https://swapi.tech/api/films"                    -o /tmp/swapi_films.json
curl -s "https://swapi.tech/api/people?page=1&limit=82"   -o /tmp/swapi_people.json
curl -s "https://swapi.tech/api/planets?page=1&limit=60"  -o /tmp/swapi_planets.json
curl -s "https://swapi.tech/api/starships?page=1&limit=40" -o /tmp/swapi_starships.json
curl -s "https://swapi.tech/api/species?page=1&limit=40"  -o /tmp/swapi_species.json
curl -s "https://swapi.tech/api/vehicles?page=1&limit=40" -o /tmp/swapi_vehicles.json
```

### 2. Fetch detail records

Use the Python script `swapi_viz.py` (included) which:
- Disables SSL verification (swapi.tech cert chain issue on macOS)
- Fetches `/api/people/{1..82}`, `/api/planets/{1..60}`, `/api/starships/{uid}` for each listed ship
- Saves `/tmp/people_detail.json`, `/tmp/planets_detail.json`, `/tmp/starships_detail.json`

```bash
pip3 install plotly pandas --quiet
python3 swapi_viz.py
```

### 3. Output

Produces `/tmp/swapi_dashboard.html` — a self-contained interactive HTML file (no server needed, opens in browser).

```bash
open /tmp/swapi_dashboard.html
```

## Dashboard panels

1. **Characters per Film** — coloured bar chart, prequel trilogy peaks at 40
2. **Planet Population (top 12)** — log-scale bar, Coruscant dominates
3. **Height vs Mass scatter** — Jabba the Hutt is the obvious outlier (1,358 kg)
4. **Starship Length Distribution** — Death Star at 120,000 m dwarfs everything
5. **Surface Water % by Climate** — box plot grouped by climate type
6. **Film Content Breakdown** — stacked bar: planets + starships + vehicles per episode

## Notes

- The API occasionally returns fewer records than `total_records` suggests — re-run if counts look low.
- `swapi_dashboard.html` in this repo is a pre-built snapshot from the last scrape.
- SSL: pass `context=ssl._create_unverified_context()` or disable cert verification on macOS Python 3.13+.
