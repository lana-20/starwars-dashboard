import json, plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter
import pandas as pd

people    = json.load(open("/tmp/people_detail.json"))
planets   = json.load(open("/tmp/planets_detail.json"))
starships = json.load(open("/tmp/starships_detail.json"))
films_raw = json.load(open("/tmp/swapi_films.json"))
databank  = json.load(open("/tmp/databank_structured.json"))

# ── helpers ──────────────────────────────────────────────────────────────────
def to_num(v):
    try:
        return float(str(v).replace(",",""))
    except:
        return None

# ── swapi data prep ───────────────────────────────────────────────────────────
df_p = pd.DataFrame(people)
df_p["height_n"] = df_p["height"].apply(to_num)
df_p["mass_n"]   = df_p["mass"].apply(to_num)
df_p = df_p.dropna(subset=["height_n","mass_n"])

df_pl = pd.DataFrame(planets)
df_pl["pop_n"]   = df_pl["population"].apply(to_num)
df_pl["water_n"] = df_pl["surface_water"].apply(to_num)
df_pl_pop = df_pl.dropna(subset=["pop_n"]).sort_values("pop_n", ascending=False).head(12)

df_s = pd.DataFrame(starships)
df_s["length_n"] = df_s["length"].apply(lambda v: to_num(str(v).replace(",","")))

films = []
for f in films_raw["result"]:
    p = f["properties"]
    films.append({
        "title": f"Ep {p['episode_id']}: {p['title'][:20]}",
        "ep": p["episode_id"],
        "characters": len(p["characters"]),
        "planets": len(p["planets"]),
        "starships": len(p["starships"]),
        "vehicles": len(p["vehicles"]),
    })
df_f = pd.DataFrame(films).sort_values("ep")

# ── databank data prep ────────────────────────────────────────────────────────
db_chars = [d for d in databank if d.get("name") and d.get("Appearances")]
db_chars_sorted = sorted(db_chars, key=lambda d: len(d["Appearances"]), reverse=True)

faction_counter = Counter()
for d in databank:
    for aff in d.get("Affiliations", []):
        faction_counter[aff] += 1
factions = [(f, c) for f, c in faction_counter.most_common(12) if c > 0]
faction_names = [f[0] for f in factions]
faction_counts = [f[1] for f in factions]

# ── figure: 4×2 grid (6 swapi + 2 databank panels) ───────────────────────────
SW_COLORS = ["#FFE81F","#FF6B35","#A8DADC","#457B9D","#E63946","#2D6A4F","#B5838D","#6D6875"]

fig = make_subplots(
    rows=4, cols=2,
    subplot_titles=[
        "Characters per Film (swapi.tech)",
        "Planet Population — top 12 (swapi.tech)",
        "Height vs Mass (swapi.tech)",
        "Starship Length Distribution (swapi.tech)",
        "Surface Water % by Climate (swapi.tech)",
        "Film Content Breakdown (swapi.tech)",
        "Appearances by Character — Databank (starwars.com)",
        "Faction Membership — Databank (starwars.com)",
    ],
    horizontal_spacing=0.12,
    vertical_spacing=0.12,
)

# 1 — characters per film
fig.add_trace(go.Bar(
    x=df_f["title"], y=df_f["characters"],
    marker_color=SW_COLORS[:len(df_f)],
    text=df_f["characters"], textposition="outside",
    showlegend=False,
), row=1, col=1)

# 2 — planet population
fig.add_trace(go.Bar(
    x=df_pl_pop["name"], y=df_pl_pop["pop_n"],
    marker=dict(color=df_pl_pop["pop_n"], colorscale="Plasma", showscale=False),
    text=[f"{v/1e9:.1f}B" if v>=1e9 else f"{v/1e6:.0f}M" if v>=1e6 else str(int(v))
          for v in df_pl_pop["pop_n"]],
    textposition="outside", showlegend=False,
), row=1, col=2)

# 3 — height vs mass scatter
fig.add_trace(go.Scatter(
    x=df_p["height_n"], y=df_p["mass_n"],
    mode="markers+text", text=df_p["name"],
    textposition="top center", textfont=dict(size=8),
    marker=dict(size=10, color=df_p["height_n"], colorscale="Viridis",
                showscale=False, line=dict(width=1, color="white")),
    showlegend=False,
    hovertemplate="<b>%{text}</b><br>Height: %{x} cm<br>Mass: %{y} kg<extra></extra>",
), row=2, col=1)

# 4 — starship length
df_sl = df_s.dropna(subset=["length_n"]).sort_values("length_n", ascending=True).tail(15)
fig.add_trace(go.Bar(
    y=df_sl["name"], x=df_sl["length_n"], orientation="h",
    marker=dict(color=df_sl["length_n"], colorscale="Reds", showscale=False),
    text=[f"{v:,.0f}m" for v in df_sl["length_n"]],
    textposition="outside", showlegend=False,
), row=2, col=2)

# 5 — surface water by climate
df_wc = df_pl.dropna(subset=["water_n"])
df_wc = df_wc[df_wc["climate"] != "unknown"].copy()
df_wc["climate_short"] = df_wc["climate"].str.split(",").str[0].str.strip()
top_climates = df_wc["climate_short"].value_counts()
top_climates = top_climates[top_climates >= 2].index.tolist()
df_wc2 = df_wc[df_wc["climate_short"].isin(top_climates)]
for i, climate in enumerate(df_wc2["climate_short"].unique()):
    sub = df_wc2[df_wc2["climate_short"] == climate]
    fig.add_trace(go.Box(
        y=sub["water_n"], name=climate,
        marker_color=SW_COLORS[i % len(SW_COLORS)],
        boxpoints="all", jitter=0.4, pointpos=0,
    ), row=3, col=1)

# 6 — film content breakdown
fig.add_trace(go.Bar(name="Planets",   x=df_f["title"], y=df_f["planets"],   marker_color="#FFE81F"), row=3, col=2)
fig.add_trace(go.Bar(name="Starships", x=df_f["title"], y=df_f["starships"], marker_color="#FF6B35"), row=3, col=2)
fig.add_trace(go.Bar(name="Vehicles",  x=df_f["title"], y=df_f["vehicles"],  marker_color="#A8DADC"), row=3, col=2)

# 7 — appearances by character (Databank)
names_app = [d["name"][:22] for d in db_chars_sorted]
counts_app = [len(d["Appearances"]) for d in db_chars_sorted]
colors_app = ["#FFE81F" if c >= 15 else "#FF6B35" if c >= 10 else "#A8DADC" for c in counts_app]
fig.add_trace(go.Bar(
    y=names_app, x=counts_app, orientation="h",
    marker_color=colors_app,
    text=counts_app, textposition="outside",
    showlegend=False,
    hovertemplate="<b>%{y}</b><br>Appearances: %{x}<extra></extra>",
), row=4, col=1)

# 8 — faction membership (Databank)
faction_colors = ["#FFE81F","#E63946","#A8DADC","#457B9D","#FF6B35","#2D6A4F",
                  "#B5838D","#6D6875","#FFE81F","#FF6B35","#A8DADC","#457B9D"]
fig.add_trace(go.Bar(
    x=faction_names, y=faction_counts,
    marker_color=faction_colors[:len(faction_names)],
    text=faction_counts, textposition="outside",
    showlegend=False,
    hovertemplate="<b>%{x}</b><br>Members: %{y}<extra></extra>",
), row=4, col=2)

fig.update_layout(
    barmode="stack",
    title=dict(
        text="Star Wars Universe — swapi.tech + Star Wars Databank",
        font=dict(size=22, color="#FFE81F"),
        x=0.5,
    ),
    paper_bgcolor="#0d0d0d",
    plot_bgcolor="#1a1a2e",
    font=dict(color="#e0e0e0", family="Courier New"),
    height=1600,
    showlegend=True,
    legend=dict(
        x=0.88, y=0.38,
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="#FFE81F",
        borderwidth=1,
    ),
)

for r in range(1, 5):
    for c in range(1, 3):
        fig.update_xaxes(gridcolor="#333355", zeroline=False, tickfont=dict(size=9), row=r, col=c)
        fig.update_yaxes(gridcolor="#333355", zeroline=False, tickfont=dict(size=9), row=r, col=c)

fig.update_yaxes(type="log", row=1, col=2)

out = "/tmp/swapi_dashboard.html"
fig.write_html(out)
print(f"Saved to {out}")
