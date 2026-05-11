import json, plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

people   = json.load(open("/tmp/people_detail.json"))
planets  = json.load(open("/tmp/planets_detail.json"))
starships = json.load(open("/tmp/starships_detail.json"))
films_raw = json.load(open("/tmp/swapi_films.json"))

# ── helpers ──────────────────────────────────────────────────────────────────
def to_num(v):
    try:
        return float(str(v).replace(",",""))
    except:
        return None

# ── data prep ─────────────────────────────────────────────────────────────────
df_p = pd.DataFrame(people)
df_p["height_n"] = df_p["height"].apply(to_num)
df_p["mass_n"]   = df_p["mass"].apply(to_num)
df_p = df_p.dropna(subset=["height_n","mass_n"])

df_pl = pd.DataFrame(planets)
df_pl["pop_n"]      = df_pl["population"].apply(to_num)
df_pl["diam_n"]     = df_pl["diameter"].apply(to_num)
df_pl["water_n"]    = df_pl["surface_water"].apply(to_num)
df_pl_pop = df_pl.dropna(subset=["pop_n"]).sort_values("pop_n", ascending=False).head(12)

df_s = pd.DataFrame(starships)
df_s["length_n"] = df_s["length"].apply(lambda v: to_num(str(v).replace(",","")))
df_s["cost_n"]   = df_s["cost"].apply(to_num)
df_s["MGLT_n"]   = df_s["MGLT"].apply(to_num)
df_s["hyp_n"]    = df_s["hyperdrive"].apply(to_num)

# films: characters per episode
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
        "year": p["release_date"][:4],
    })
df_f = pd.DataFrame(films).sort_values("ep")

# ── figure: 2×3 grid ─────────────────────────────────────────────────────────
SW_COLORS = ["#FFE81F","#FF6B35","#A8DADC","#457B9D","#E63946","#2D6A4F","#B5838D","#6D6875"]

fig = make_subplots(
    rows=2, cols=3,
    subplot_titles=[
        "Characters per Film",
        "Planet Population (top 12)",
        "Height vs Mass — Characters",
        "Starship Length Distribution",
        "Surface Water % by Climate",
        "Film Content Breakdown",
    ],
    horizontal_spacing=0.10,
    vertical_spacing=0.18,
)

# 1 — characters per film (bar)
fig.add_trace(go.Bar(
    x=df_f["title"], y=df_f["characters"],
    marker_color=SW_COLORS[:len(df_f)],
    text=df_f["characters"], textposition="outside",
    showlegend=False,
), row=1, col=1)

# 2 — planet population log bar
fig.add_trace(go.Bar(
    x=df_pl_pop["name"],
    y=df_pl_pop["pop_n"],
    marker=dict(color=df_pl_pop["pop_n"], colorscale="Plasma", showscale=False),
    text=[f"{v/1e9:.1f}B" if v>=1e9 else f"{v/1e6:.0f}M" if v>=1e6 else str(int(v))
          for v in df_pl_pop["pop_n"]],
    textposition="outside",
    showlegend=False,
), row=1, col=2)

# 3 — height vs mass scatter
fig.add_trace(go.Scatter(
    x=df_p["height_n"], y=df_p["mass_n"],
    mode="markers+text",
    text=df_p["name"],
    textposition="top center",
    textfont=dict(size=8),
    marker=dict(
        size=10,
        color=df_p["height_n"],
        colorscale="Viridis",
        showscale=False,
        line=dict(width=1, color="white"),
    ),
    showlegend=False,
    hovertemplate="<b>%{text}</b><br>Height: %{x} cm<br>Mass: %{y} kg<extra></extra>",
), row=1, col=3)

# 4 — starship length (horizontal bar, top 15)
df_sl = df_s.dropna(subset=["length_n"]).sort_values("length_n", ascending=True).tail(15)
fig.add_trace(go.Bar(
    y=df_sl["name"], x=df_sl["length_n"],
    orientation="h",
    marker=dict(color=df_sl["length_n"], colorscale="Reds", showscale=False),
    text=[f"{v:,.0f}m" for v in df_sl["length_n"]],
    textposition="outside",
    showlegend=False,
), row=2, col=1)

# 5 — surface water % by climate (box/strip)
df_wc = df_pl.dropna(subset=["water_n"])
df_wc = df_wc[df_wc["climate"] != "unknown"]
df_wc["climate_short"] = df_wc["climate"].str.split(",").str[0].str.strip()
climate_counts = df_wc["climate_short"].value_counts()
top_climates = climate_counts[climate_counts >= 2].index.tolist()
df_wc2 = df_wc[df_wc["climate_short"].isin(top_climates)]

for i, climate in enumerate(df_wc2["climate_short"].unique()):
    sub = df_wc2[df_wc2["climate_short"] == climate]
    fig.add_trace(go.Box(
        y=sub["water_n"], name=climate,
        marker_color=SW_COLORS[i % len(SW_COLORS)],
        boxpoints="all", jitter=0.4, pointpos=0,
    ), row=2, col=2)

# 6 — stacked bar: planets, starships, vehicles per film
fig.add_trace(go.Bar(
    name="Planets",
    x=df_f["title"], y=df_f["planets"],
    marker_color="#FFE81F",
), row=2, col=3)
fig.add_trace(go.Bar(
    name="Starships",
    x=df_f["title"], y=df_f["starships"],
    marker_color="#FF6B35",
), row=2, col=3)
fig.add_trace(go.Bar(
    name="Vehicles",
    x=df_f["title"], y=df_f["vehicles"],
    marker_color="#A8DADC",
), row=2, col=3)

fig.update_layout(
    barmode="stack",
    title=dict(
        text="Star Wars Universe — Data Scraped from swapi.tech",
        font=dict(size=22, color="#FFE81F"),
        x=0.5,
    ),
    paper_bgcolor="#0d0d0d",
    plot_bgcolor="#1a1a2e",
    font=dict(color="#e0e0e0", family="Courier New"),
    height=900,
    showlegend=True,
    legend=dict(
        x=0.75, y=0.05,
        bgcolor="rgba(0,0,0,0.5)",
        bordercolor="#FFE81F",
        borderwidth=1,
    ),
)

# axis styling
for i in range(1, 7):
    row, col = divmod(i-1, 3)
    fig.update_xaxes(
        gridcolor="#333355", zeroline=False,
        tickfont=dict(size=9), row=row+1, col=col+1,
    )
    fig.update_yaxes(
        gridcolor="#333355", zeroline=False,
        tickfont=dict(size=9), row=row+1, col=col+1,
    )

# log scale for population
fig.update_yaxes(type="log", row=1, col=2)

out = "/tmp/swapi_dashboard.html"
fig.write_html(out)
print(f"Saved to {out}")
