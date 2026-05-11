# starwars-dashboard

Scrapes Star Wars data from two sources — the [swapi.tech](https://swapi.tech/) REST API and the [Star Wars Databank](https://www.starwars.com/databank) — using the **vibium browser automation CLI**, then generates a dark-themed interactive Plotly dashboard and cross-source character comparisons.

**Live dashboard:** https://lana-20.github.io/starwars-dashboard/

![SWAPI Dashboard](swapi_dashboard.png)

## Data sources

| Source | Method | Coverage |
|---|---|---|
| swapi.tech | REST API + Python | 82 people, 60 planets, 36 starships, 6 films, 37 species, 39 vehicles |
| Star Wars Databank | vibium browser automation | 2,515 entries — characters, locations, creatures, droids, vehicles, weapons, species, organizations |

## What it does

1. Uses **vibium** (`/vibe-check`) to navigate and scrape starwars.com/databank
2. Fetches all 6 swapi.tech resource types via `curl` + Python
3. Pulls detail records for every entry (82 people, 60 planets, 36 starships)
4. Renders a self-contained interactive HTML dashboard with Plotly
5. Builds cross-source character comparison vizzes (see Yoda vs Grogu below)

## Dashboard panels

| Panel | Description |
|---|---|
| Characters per Film | Prequel trilogy peaks at 40 characters vs 16–20 in the originals |
| Planet Population | Log-scale bar — Coruscant dominates at 1 trillion |
| Height vs Mass | Scatter plot — Jabba the Hutt is the obvious outlier at 1,358 kg |
| Starship Length | Death Star at 120,000 m dwarfs the entire fleet |
| Surface Water % by Climate | Box plot grouped by climate type |
| Film Content Breakdown | Stacked bar: planets + starships + vehicles per episode |

## Yoda vs Grogu

Cross-source comparison — Yoda from swapi.tech, Grogu scraped from the Star Wars Databank using vibium.

**Grogu — Star Wars Databank**

![Grogu Databank](grogu_databank.png)

**Yoda vs Grogu comparison**

![Yoda vs Grogu](yoda_vs_grogu.png)

## Files

| File | Description |
|---|---|
| `SKILL.md` | Skill definition and step-by-step instructions |
| `swapi_viz.py` | Scrape + Plotly script |
| `index.html` | Live interactive dashboard (served via GitHub Pages) |
| `yoda_vs_grogu.html` | Yoda vs Grogu static comparison viz |

## Usage

```bash
pip3 install plotly pandas
python3 swapi_viz.py
open /tmp/swapi_dashboard.html
```

Or invoke as a Claude Code skill: `/starwars-dashboard`
