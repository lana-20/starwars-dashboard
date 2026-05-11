---
name: starwars-dashboard
description: Scrape Star Wars data from two sources — swapi.tech REST API and the Star Wars Databank (starwars.com/databank) using vibium browser automation — then generate an interactive Plotly dashboard and cross-source character comparisons.
---

# Star Wars Dashboard

Scrapes Star Wars data from two sources and renders interactive visualizations with a dark Star Wars theme.

## Data sources

| Source | Method | What's available |
|---|---|---|
| [swapi.tech](https://swapi.tech) | REST API (`curl` + Python) | 82 people, 60 planets, 36 starships, 6 films, 37 species, 39 vehicles — structured numeric data |
| [Star Wars Databank](https://www.starwars.com/databank) | vibium browser automation | 2,515 entries across characters, locations, creatures, droids, vehicles, weapons, species, organizations — rich fields: height, gender, species, affiliations, weapons, appearances, history, quotes |

## Databank entry fields

**Characters:** height · gender · species · affiliations · locations · weapons · vehicles · appearances · history · quotes

**Locations:** climate · terrain · species · creatures · droids · vehicles · sub-locations · history · quotes

## Steps

### 1. Scrape swapi.tech (REST API)

```bash
curl -s "https://swapi.tech/api/films"                    -o /tmp/swapi_films.json
curl -s "https://swapi.tech/api/people?page=1&limit=82"   -o /tmp/swapi_people.json
curl -s "https://swapi.tech/api/planets?page=1&limit=60"  -o /tmp/swapi_planets.json
curl -s "https://swapi.tech/api/starships?page=1&limit=40" -o /tmp/swapi_starships.json
curl -s "https://swapi.tech/api/species?page=1&limit=40"  -o /tmp/swapi_species.json
curl -s "https://swapi.tech/api/vehicles?page=1&limit=40" -o /tmp/swapi_vehicles.json
```

Fetch detail records with `swapi_viz.py` (disables SSL verification — needed on macOS Python 3.13+):

```bash
pip3 install plotly pandas --quiet
python3 swapi_viz.py
```

### 2. Scrape the Databank (vibium)

```bash
V=/usr/local/lib/node_modules/vibium/node_modules/@vibium/darwin-x64/bin/vibium
$V go https://www.starwars.com/databank/<slug>
$V text
```

Databank slugs match character names: `grogu`, `luke-skywalker`, `tatooine`, `darth-vader`, etc.

Index page at `https://www.starwars.com/databank` lists all 2,515 entries with category counts.

### 3. Generate the dashboard

```bash
python3 swapi_viz.py
open /tmp/swapi_dashboard.html
```

## Dashboard panels (swapi.tech data)

1. **Characters per Film** — coloured bar, prequel trilogy peaks at 40
2. **Planet Population (top 12)** — log-scale bar, Coruscant dominates
3. **Height vs Mass scatter** — Jabba the Hutt outlier at 1,358 kg
4. **Starship Length Distribution** — Death Star at 120,000 m
5. **Surface Water % by Climate** — box plot by climate type
6. **Film Content Breakdown** — stacked bar: planets + starships + vehicles per episode

## Cross-source comparisons

See `yoda_vs_grogu.html` — Yoda (swapi.tech) vs Grogu (Databank) side-by-side:
stat cards · height bar chart · age timeline · affiliations badges

## Notes

- `index.html` is the live dashboard served via GitHub Pages at https://lana-20.github.io/starwars-dashboard/
- SSL: disable cert verification on macOS Python 3.13+ (`ssl.CERT_NONE`)
- The API occasionally returns fewer records than `total_records` — re-run if counts look low
