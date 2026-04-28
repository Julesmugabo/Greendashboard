import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from data_loader import load_data

# ─────────────────────────────────────────
# Colour palette  (dark green + gold/amber)
# ─────────────────────────────────────────
C = {
    "bg_dark":      "#0a1f0e",
    "bg_card":      "#0f2d14",
    "bg_card2":     "#122e17",
    "green_dark":   "#1a4d25",
    "green_mid":    "#2e7d32",
    "green_light":  "#4caf50",
    "green_pale":   "#a5d6a7",
    "gold":         "#f9a825",
    "gold_light":   "#ffd54f",
    "gold_pale":    "#fff9c4",
    "text_main":    "#e8f5e9",
    "text_muted":   "#81c784",
    "text_gold":    "#ffd54f",
    "border":       "#2e7d32",
    "red":          "#ef5350",
    "red_soft":     "#ff8a65",
    "white":        "#ffffff",
}

PALETTE = [C["green_light"], C["gold"], C["green_pale"], C["gold_light"],
           C["green_mid"], C["red_soft"], "#80cbc4", "#ffb74d", "#aed581"]

# ─────────────────────────────────────────
# Load data
# ─────────────────────────────────────────
df_proj, df_exp, df_acc = load_data()

# ─────────────────────────────────────────
# App bootstrap
# ─────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "GreenStars Financial Dashboard 2026"
server = app.server

# ─────────────────────────────────────────
# Helper: card style
# ─────────────────────────────────────────
def card_style(extra=None):
    s = {
        "backgroundColor": C["bg_card"],
        "border": f"1px solid {C['border']}",
        "borderRadius": "10px",
        "padding": "16px",
        "height": "100%",
    }
    if extra:
        s.update(extra)
    return s


def section_title(text, color=None):
    return html.Div(
        text,
        style={
            "color": color or C["gold"],
            "fontWeight": "700",
            "fontSize": "12px",
            "letterSpacing": "1.5px",
            "textTransform": "uppercase",
            "marginBottom": "8px",
        },
    )


def fmt_rwf(n):
    if n >= 1_000_000_000:
        return f"RWF {n/1_000_000_000:.2f}B"
    if n >= 1_000_000:
        return f"RWF {n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"RWF {n/1_000:.0f}K"
    return f"RWF {n:,.0f}"


# ─────────────────────────────────────────
# KPI Card factory
# ─────────────────────────────────────────
def kpi_card(card_id, icon, label, value, sub="", accent=None, clickable=False):
    border_color = accent or C["green_light"]
    cursor = "pointer" if clickable else "default"
    return html.Div(
        id=card_id,
        n_clicks=0,
        style={
            "backgroundColor": C["bg_card"],
            "border": f"2px solid {border_color}",
            "borderRadius": "12px",
            "padding": "14px 16px",
            "cursor": cursor,
            "transition": "all 0.2s ease",
            "position": "relative",
            "overflow": "hidden",
        },
        children=[
            html.Div(
                style={
                    "position": "absolute", "top": 0, "left": 0,
                    "width": "4px", "height": "100%",
                    "backgroundColor": border_color,
                    "borderRadius": "12px 0 0 12px",
                },
            ),
            html.Div(
                [
                    html.Span(icon, style={"fontSize": "22px", "marginRight": "8px"}),
                    html.Span(label, style={
                        "color": C["text_muted"], "fontSize": "11px",
                        "letterSpacing": "1px", "textTransform": "uppercase", "fontWeight": "600"
                    }),
                ],
                style={"display": "flex", "alignItems": "center", "marginBottom": "6px"},
            ),
            html.Div(value, style={
                "color": C["text_main"], "fontSize": "22px",
                "fontWeight": "800", "lineHeight": "1.1",
            }),
            html.Div(sub, style={"color": C["text_muted"], "fontSize": "11px", "marginTop": "4px"}),
        ],
    )


# ─────────────────────────────────────────
# Compute top-level KPIs
# ─────────────────────────────────────────
total_budget = df_proj[df_proj["Category"] != "General"]["Total Budget"].sum()
total_expenses = df_exp["Amount (RWF)"].sum()
total_income = df_proj["Total Income"].sum()
project_expenses = df_exp[df_exp["Project_ID"] != "GNRL"]["Amount (RWF)"].sum()
overhead_expenses = df_exp[df_exp["Project_ID"] == "GNRL"]["Amount (RWF)"].sum()
net_position = total_income - total_expenses
active_projects = len(df_proj[df_proj["Category"] == "Project"])
cb_projects = len(df_proj[df_proj["Category"] == "Capacity Building"])
budget_util = total_expenses / total_budget * 100 if total_budget else 0
avg_monthly_burn = df_exp.groupby("Date")["Amount (RWF)"].sum().mean()

months = sorted(df_exp["Date"].unique())

# ─────────────────────────────────────────
# Layout
# ─────────────────────────────────────────
app.layout = html.Div(
    style={"backgroundColor": C["bg_dark"], "minHeight": "100vh", "fontFamily": "'Segoe UI', sans-serif", "padding": "0"},
    children=[
        # ── HEADER ──────────────────────────────────────────
        html.Div(
            style={
                "backgroundColor": C["green_dark"],
                "borderBottom": f"2px solid {C['gold']}",
                "padding": "14px 28px",
                "display": "flex", "justifyContent": "space-between", "alignItems": "center",
            },
            children=[
                html.Div([
                    html.Img(src="/asset/logo.png", style={"height": "60px", "marginRight": "20px"}),
                    html.Span("GreenStars Financial Dashboard", style={
                        "color": C["text_main"], "fontWeight": "800",
                        "fontSize": "22px", "letterSpacing": "0.5px",
                    }),
                    html.Span(" · 2026", style={"color": C["gold"], "fontWeight": "400", "fontSize": "18px"}),
                ]),
                html.Div([
                    html.Span("Fiscal Year 2026  |  ", style={"color": C["text_muted"], "fontSize": "12px"}),
                    html.Span("Jan – Apr  (Q1–Q2)", style={"color": C["gold_light"], "fontSize": "12px", "fontWeight": "600"}),
                ]),
            ],
        ),

        # ── FILTERS BAR ─────────────────────────────────────
        html.Div(
            style={
                "backgroundColor": C["bg_card2"],
                "borderBottom": f"1px solid {C['border']}",
                "padding": "10px 24px",
                "display": "flex", "flexWrap": "wrap", "gap": "20px", "alignItems": "center",
            },
            children=[
                html.Div([
                    html.Label("📅 Month", style={"color": C["text_muted"], "fontSize": "11px", "display": "block", "marginBottom": "3px"}),
                    dcc.Dropdown(
                        id="filter-month",
                        options=[{"label": "All Months", "value": "ALL"}] +
                                [{"label": m, "value": m} for m in months],
                        value="ALL",
                        clearable=False,
                        style={"width": "160px", "backgroundColor": C["bg_card"], "color": C["text_main"]},
                        className="dark-dropdown",
                    ),
                ]),
                html.Div([
                    html.Label("📁 Project", style={"color": C["text_muted"], "fontSize": "11px", "display": "block", "marginBottom": "3px"}),
                    dcc.Dropdown(
                        id="filter-project",
                        options=[{"label": "All Projects", "value": "ALL"}] +
                                [{"label": f"{row['Project ID']} · {row['Name'][:30]}", "value": row["Project ID"]}
                                 for _, row in df_proj.iterrows()],
                        value="ALL",
                        clearable=False,
                        style={"width": "260px"},
                        className="dark-dropdown",
                    ),
                ]),
                html.Div([
                    html.Label("🏷️ Category", style={"color": C["text_muted"], "fontSize": "11px", "display": "block", "marginBottom": "3px"}),
                    dcc.Dropdown(
                        id="filter-category",
                        options=[{"label": "All Categories", "value": "ALL"}] +
                                [{"label": c, "value": c} for c in sorted(df_exp["Category"].unique())],
                        value="ALL",
                        clearable=False,
                        style={"width": "200px"},
                        className="dark-dropdown",
                    ),
                ]),
                html.Div(
                    html.Button("↺ Reset Filters", id="btn-reset", n_clicks=0,
                                style={
                                    "backgroundColor": "transparent",
                                    "border": f"1px solid {C['gold']}",
                                    "color": C["gold"], "padding": "6px 16px",
                                    "borderRadius": "6px", "cursor": "pointer",
                                    "fontSize": "12px", "fontWeight": "600",
                                }),
                    style={"marginTop": "14px"},
                ),
                html.Div(id="active-filter-badge", style={"marginTop": "14px"}),
            ],
        ),

        # ── MAIN BODY ────────────────────────────────────────
        html.Div(
            style={"padding": "20px 24px"},
            children=[

                # ─ KPI ROW ─
                html.Div(id="kpi-row",
                    style={"display": "grid",
                           "gridTemplateColumns": "repeat(auto-fill, minmax(180px, 1fr))",
                           "gap": "14px", "marginBottom": "20px"},
                ),

                # ─ STORY INSIGHT BANNER ─
                html.Div(id="story-banner",
                    style={
                        "backgroundColor": C["green_dark"],
                        "border": f"1px solid {C['gold']}",
                        "borderLeft": f"5px solid {C['gold']}",
                        "borderRadius": "8px",
                        "padding": "12px 18px",
                        "marginBottom": "20px",
                        "color": C["text_main"],
                        "fontSize": "13px",
                        "lineHeight": "1.6",
                    },
                ),

                # ─ ROW 1: Monthly burn + Category pie ─
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "16px", "marginBottom": "16px"},
                    children=[
                        html.Div(dcc.Graph(id="chart-monthly-burn", config={"displayModeBar": False}), style=card_style()),
                        html.Div(dcc.Graph(id="chart-category-pie", config={"displayModeBar": False}), style=card_style()),
                    ],
                ),

                # ─ ROW 2: Project budget vs expenses bar + Income vs Expenses ─
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                    children=[
                        html.Div(dcc.Graph(id="chart-project-budget", config={"displayModeBar": False}), style=card_style()),
                        html.Div(dcc.Graph(id="chart-income-expenses", config={"displayModeBar": False}), style=card_style()),
                    ],
                ),

                # ─ ROW 3: Top expense accounts + Budget utilisation gauge ─
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "16px", "marginBottom": "16px"},
                    children=[
                        html.Div(dcc.Graph(id="chart-top-accounts", config={"displayModeBar": False}), style=card_style()),
                        html.Div(dcc.Graph(id="chart-budget-gauge", config={"displayModeBar": False}), style=card_style()),
                    ],
                ),

                # ─ ROW 4: Overhead breakdown treemap ─
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
                    children=[
                        html.Div(dcc.Graph(id="chart-overhead-tree", config={"displayModeBar": False}), style=card_style()),
                        html.Div(dcc.Graph(id="chart-cumulative", config={"displayModeBar": False}), style=card_style()),
                    ],
                ),

                # ─ ROW 5: Detailed transactions table ─
                html.Div(
                    style=card_style({"marginBottom": "16px"}),
                    children=[
                        section_title("📋 Transaction Detail — Drill-Down Table"),
                        html.Div(id="detail-table"),
                    ],
                ),

                # ─ Footer ─
                html.Div(
                    "GreenStars · Financial Intelligence Dashboard · 2026  |  Data as of April 2026",
                    style={
                        "textAlign": "center", "color": C["text_muted"],
                        "fontSize": "11px", "padding": "20px 0 10px",
                        "borderTop": f"1px solid {C['border']}",
                    },
                ),
            ],
        ),

        # Hidden store for selected KPI
        dcc.Store(id="selected-kpi", data=None),
    ],
)


# ─────────────────────────────────────────
# Utility: apply filters
# ─────────────────────────────────────────
def filter_expenses(month, project, category):
    dfe = df_exp.copy()
    if month != "ALL":
        dfe = dfe[dfe["Date"] == month]
    if project != "ALL":
        dfe = dfe[dfe["Project_ID"] == project]
    if category != "ALL":
        dfe = dfe[dfe["Category"] == category]
    return dfe


def filter_projects(project):
    dfp = df_proj.copy()
    if project != "ALL":
        dfp = dfp[dfp["Project ID"] == project]
    return dfp


def chart_layout(title):
    return dict(
        title=dict(text=title, font=dict(color=C["gold"], size=13, family="Segoe UI")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C["text_main"], family="Segoe UI"),
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["text_muted"], size=10)),
        xaxis=dict(gridcolor=C["green_dark"], linecolor=C["border"], tickfont=dict(color=C["text_muted"], size=10)),
        yaxis=dict(gridcolor=C["green_dark"], linecolor=C["border"], tickfont=dict(color=C["text_muted"], size=10)),
    )


# ─────────────────────────────────────────
# CALLBACKS
# ─────────────────────────────────────────

# Reset button
@app.callback(
    Output("filter-month", "value"),
    Output("filter-project", "value"),
    Output("filter-category", "value"),
    Input("btn-reset", "n_clicks"),
    prevent_initial_call=True,
)
def reset_filters(_):
    return "ALL", "ALL", "ALL"


# Active filter badge
@app.callback(
    Output("active-filter-badge", "children"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def badge(month, project, category):
    parts = []
    if month != "ALL":
        parts.append(f"📅 {month}")
    if project != "ALL":
        parts.append(f"📁 {project}")
    if category != "ALL":
        parts.append(f"🏷️ {category}")
    if not parts:
        return html.Span("No active filters", style={"color": C["text_muted"], "fontSize": "11px"})
    badges = [html.Span(p, style={
        "backgroundColor": C["green_mid"], "color": C["text_main"],
        "padding": "3px 10px", "borderRadius": "20px", "fontSize": "11px",
        "marginRight": "6px", "fontWeight": "600",
    }) for p in parts]
    return html.Div(badges, style={"display": "flex", "flexWrap": "wrap", "gap": "4px"})


# KPI row
@app.callback(
    Output("kpi-row", "children"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def update_kpis(month, project, category):
    dfe = filter_expenses(month, project, category)
    dfp = filter_projects(project)
    dfp_real = dfp[dfp["Category"] != "General"]

    tot_exp = dfe["Amount (RWF)"].sum()
    tot_inc = dfp["Total Income"].sum()
    tot_bud = dfp_real["Total Budget"].sum()
    tot_net = tot_inc - tot_exp
    oh = dfe[dfe["Project_ID"] == "GNRL"]["Amount (RWF)"].sum()
    proj_e = dfe[dfe["Project_ID"] != "GNRL"]["Amount (RWF)"].sum()
    util = tot_exp / tot_bud * 100 if tot_bud else 0
    n_proj = len(dfp[dfp["Category"] == "Project"])
    n_cb = len(dfp[dfp["Category"] == "Capacity Building"])
    monthly_avg = dfe.groupby("Date")["Amount (RWF)"].sum().mean() if len(dfe) else 0

    net_color = C["green_light"] if tot_net >= 0 else C["red"]
    util_color = C["red"] if util > 80 else (C["gold"] if util > 50 else C["green_light"])

    return [
        kpi_card("kpi-total-expenses", "💸", "Total Expenses", fmt_rwf(tot_exp),
                 f"All categories · {month}", C["gold"], True),
        kpi_card("kpi-total-income", "💰", "Total Income", fmt_rwf(tot_inc),
                 "Across active projects", C["green_light"], True),
        kpi_card("kpi-net-position", "📊", "Net Position", fmt_rwf(tot_net),
                 "Income minus expenses", net_color, True),
        kpi_card("kpi-budget-util", "🎯", "Budget Utilization", f"{util:.1f}%",
                 f"of RWF {tot_bud/1e6:.0f}M total budget", util_color, True),
        kpi_card("kpi-overhead", "🏢", "Overhead Costs", fmt_rwf(oh),
                 "General / operational", C["text_muted"], True),
        kpi_card("kpi-project-spend", "🔬", "Project Spend", fmt_rwf(proj_e),
                 "Direct project expenses", C["green_pale"], True),
        kpi_card("kpi-active-proj", "📂", "Active Projects", str(n_proj + n_cb),
                 f"{n_proj} research · {n_cb} capacity building", C["gold_light"], False),
        kpi_card("kpi-monthly-burn", "🔥", "Avg Monthly Burn", fmt_rwf(monthly_avg),
                 "Average monthly spend", C["red_soft"], True),
    ]


# Story banner
@app.callback(
    Output("story-banner", "children"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def update_story(month, project, category):
    dfe = filter_expenses(month, project, category)
    dfp = filter_projects(project)
    dfp_real = dfp[dfp["Category"] != "General"]

    tot_exp = dfe["Amount (RWF)"].sum()
    tot_inc = dfp["Total Income"].sum()
    tot_bud = dfp_real["Total Budget"].sum()
    tot_net = tot_inc - tot_exp

    # Month trend
    monthly = dfe.groupby("Date")["Amount (RWF)"].sum().reset_index()
    trend_str = ""
    if len(monthly) > 1:
        delta = monthly.iloc[-1]["Amount (RWF)"] - monthly.iloc[-2]["Amount (RWF)"]
        direction = "⬆️ increased" if delta > 0 else "⬇️ decreased"
        trend_str = f" Monthly spend {direction} by {fmt_rwf(abs(delta))} from {monthly.iloc[-2]['Date']} to {monthly.iloc[-1]['Date']}."

    top_account = dfe.groupby("Account_Name")["Amount (RWF)"].sum().idxmax() if len(dfe) else "—"
    top_project = dfe.groupby("Project_ID")["Amount (RWF)"].sum().idxmax() if len(dfe) else "—"
    overhead_pct = dfe[dfe["Project_ID"] == "GNRL"]["Amount (RWF)"].sum() / tot_exp * 100 if tot_exp else 0
    util = tot_exp / tot_bud * 100 if tot_bud else 0

    net_sentiment = "positive" if tot_net >= 0 else "⚠️ negative"
    alert = ""
    if overhead_pct > 60:
        alert = f" ⚠️ Overhead represents {overhead_pct:.0f}% of total spend — management attention advised."
    if util > 75:
        alert += f" 🚨 Budget utilization at {util:.0f}% — high burn rate relative to approved budget."

    return [
        html.Strong("📖 Financial Story · ", style={"color": C["gold"]}),
        f"Total expenditure stands at {fmt_rwf(tot_exp)} against recorded income of {fmt_rwf(tot_inc)}, "
        f"resulting in a {net_sentiment} net position of {fmt_rwf(tot_net)}. "
        f"The highest spending account is '{top_account}' while '{top_project}' drives the most project-level activity. "
        f"Overhead costs account for {overhead_pct:.0f}% of all spend.{trend_str}",
        html.Span(alert, style={"color": C["gold"], "fontWeight": "600"}) if alert else "",
    ]


# Monthly burn chart
@app.callback(
    Output("chart-monthly-burn", "figure"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def chart_monthly(month, project, category):
    dfe = filter_expenses(month, project, category)
    monthly = dfe.groupby(["Date", "Category"])["Amount (RWF)"].sum().reset_index()
    all_months = sorted(dfe["Date"].unique())

    fig = go.Figure()
    cats = sorted(monthly["Category"].unique())
    for i, cat in enumerate(cats):
        sub = monthly[monthly["Category"] == cat]
        fig.add_trace(go.Bar(
            x=sub["Date"], y=sub["Amount (RWF)"] / 1e6,
            name=cat, marker_color=PALETTE[i % len(PALETTE)],
            hovertemplate=f"<b>{cat}</b><br>Month: %{{x}}<br>Amount: RWF %{{y:.2f}}M<extra></extra>",
        ))

    # Trend line
    total_by_month = dfe.groupby("Date")["Amount (RWF)"].sum().reset_index()
    if len(total_by_month) > 1:
        fig.add_trace(go.Scatter(
            x=total_by_month["Date"], y=total_by_month["Amount (RWF)"] / 1e6,
            mode="lines+markers", name="Total Trend",
            line=dict(color=C["gold"], width=2, dash="dot"),
            marker=dict(size=8, color=C["gold"]),
            hovertemplate="<b>Total</b><br>Month: %{x}<br>RWF %{y:.2f}M<extra></extra>",
        ))

    fig.update_layout(
        **chart_layout("Monthly Expenditure by Category (RWF Millions)"),
        barmode="stack",
        yaxis_title="RWF (Millions)",
    )
    return fig


# Category pie
@app.callback(
    Output("chart-category-pie", "figure"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def chart_cat_pie(month, project, category):
    dfe = filter_expenses(month, project, category)
    by_cat = dfe.groupby("Category")["Amount (RWF)"].sum().reset_index()
    fig = go.Figure(go.Pie(
        labels=by_cat["Category"],
        values=by_cat["Amount (RWF)"],
        hole=0.5,
        marker=dict(colors=PALETTE[:len(by_cat)], line=dict(color=C["bg_dark"], width=2)),
        textinfo="label+percent",
        textfont=dict(color=C["text_main"], size=11),
        hovertemplate="<b>%{label}</b><br>%{customdata}<br>%{percent}<extra></extra>",
        customdata=[fmt_rwf(v) for v in by_cat["Amount (RWF)"]],
    ))
    fig.update_layout(**chart_layout("Spend by Category"))
    fig.add_annotation(text="Spend Mix", x=0.5, y=0.5, showarrow=False,
                       font=dict(color=C["gold"], size=12, family="Segoe UI"))
    return fig


# Project budget vs expenses
@app.callback(
    Output("chart-project-budget", "figure"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def chart_proj_budget(month, project, category):
    dfe = filter_expenses(month, project, category)
    dfp = df_proj[df_proj["Category"] != "General"].copy()
    if project != "ALL":
        dfp = dfp[dfp["Project ID"] == project]

    proj_actual = dfe[dfe["Project_ID"] != "GNRL"].groupby("Project_ID")["Amount (RWF)"].sum().reset_index()
    proj_actual.columns = ["Project ID", "Actual Expenses"]
    merged = dfp.merge(proj_actual, on="Project ID", how="left").fillna(0)

    short_names = [n[:20] + "…" if len(n) > 20 else n for n in merged["Name"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Total Budget", x=short_names, y=merged["Total Budget"] / 1e6,
        marker_color=C["green_dark"], marker_line=dict(color=C["green_mid"], width=1),
        hovertemplate="<b>Budget</b><br>%{x}<br>RWF %{y:.1f}M<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Actual Expenses", x=short_names, y=merged["Actual Expenses"] / 1e6,
        marker_color=C["gold"],
        hovertemplate="<b>Expenses</b><br>%{x}<br>RWF %{y:.1f}M<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        name="Total Income", x=short_names, y=merged["Total Income"] / 1e6,
        marker_color=C["green_light"],
        hovertemplate="<b>Income</b><br>%{x}<br>RWF %{y:.1f}M<extra></extra>",
    ))
    fig.update_layout(
        **chart_layout("Project Budget vs Expenses vs Income (RWF M)"),
        barmode="group",
        yaxis_title="RWF (Millions)",
    )
    return fig


# Income vs Expenses waterfall/bar
@app.callback(
    Output("chart-income-expenses", "figure"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def chart_income_exp(month, project, category):
    dfe = filter_expenses(month, project, category)
    dfp = filter_projects(project)

    items = []
    for _, row in dfp[dfp["Category"] != "General"].iterrows():
        proj_exp = dfe[dfe["Project_ID"] == row["Project ID"]]["Amount (RWF)"].sum()
        items.append({
            "Name": (row["Name"][:22] + "…") if len(row["Name"]) > 22 else row["Name"],
            "Income": row["Total Income"],
            "Expenses": proj_exp,
            "Net": row["Total Income"] - proj_exp,
        })
    df_it = pd.DataFrame(items)
    if df_it.empty:
        return go.Figure(layout=chart_layout("Income vs Expenses per Project"))

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Income", x=df_it["Name"], y=df_it["Income"] / 1e6,
                         marker_color=C["green_light"],
                         hovertemplate="%{x}<br>Income: RWF %{y:.1f}M<extra></extra>"))
    fig.add_trace(go.Bar(name="Expenses", x=df_it["Name"], y=df_it["Expenses"] / 1e6,
                         marker_color=C["gold"],
                         hovertemplate="%{x}<br>Expenses: RWF %{y:.1f}M<extra></extra>"))
    net_colors = [C["green_light"] if v >= 0 else C["red"] for v in df_it["Net"]]
    fig.add_trace(go.Bar(name="Net", x=df_it["Name"], y=df_it["Net"] / 1e6,
                         marker_color=net_colors,
                         hovertemplate="%{x}<br>Net: RWF %{y:.1f}M<extra></extra>"))
    fig.update_layout(**chart_layout("Income vs Expenses vs Net per Project"), barmode="group", yaxis_title="RWF (M)")
    return fig


# Top accounts horizontal bar
@app.callback(
    Output("chart-top-accounts", "figure"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def chart_top_accounts(month, project, category):
    dfe = filter_expenses(month, project, category)
    top = dfe.groupby("Account_Name")["Amount (RWF)"].sum().sort_values(ascending=True).tail(12)
    if top.empty:
        return go.Figure(layout=chart_layout("Top Expense Accounts"))

    bar_colors = [C["red"] if v == top.max() else C["gold"] if v >= top.quantile(0.75) else C["green_light"]
                  for v in top.values]

    fig = go.Figure(go.Bar(
        x=top.values / 1e6,
        y=[n[:35] for n in top.index],
        orientation="h",
        marker_color=bar_colors,
        text=[fmt_rwf(v) for v in top.values],
        textposition="outside",
        textfont=dict(color=C["text_muted"], size=10),
        hovertemplate="%{y}<br>RWF %{x:.2f}M<extra></extra>",
    ))
    layout = chart_layout("Top 12 Expense Accounts (RWF Millions)")
    layout["yaxis"]["tickfont"] = dict(size=10, color=C["text_muted"])
    fig.update_layout(**layout, xaxis_title="RWF (Millions)", height=400)
    return fig


# Budget utilization gauge
@app.callback(
    Output("chart-budget-gauge", "figure"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def chart_gauge(month, project, category):
    dfe = filter_expenses(month, project, category)
    dfp = filter_projects(project)
    dfp_real = dfp[dfp["Category"] != "General"]
    tot_bud = dfp_real["Total Budget"].sum()
    tot_exp = dfe["Amount (RWF)"].sum()
    util = min(tot_exp / tot_bud * 100 if tot_bud else 0, 100)

    bar_color = C["red"] if util > 75 else (C["gold"] if util > 50 else C["green_light"])

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=util,
        number={"suffix": "%", "font": {"color": C["text_main"], "size": 32}},
        delta={"reference": 50, "font": {"color": C["text_muted"]}, "suffix": "%"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": C["text_muted"],
                     "tickfont": {"color": C["text_muted"], "size": 10}},
            "bar": {"color": bar_color, "thickness": 0.8},
            "bgcolor": C["bg_dark"],
            "bordercolor": C["border"],
            "steps": [
                {"range": [0, 50], "color": C["green_dark"]},
                {"range": [50, 75], "color": "#1b5e20"},
                {"range": [75, 100], "color": "#4a1010"},
            ],
            "threshold": {"line": {"color": C["gold"], "width": 3}, "thickness": 0.8, "value": 75},
        },
        title={"text": "Budget Utilization", "font": {"color": C["gold"], "size": 13}},
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color=C["text_main"]),
                      margin=dict(l=30, r=30, t=60, b=20))
    fig.add_annotation(
        text=f"Spent: {fmt_rwf(tot_exp)}<br>Budget: {fmt_rwf(tot_bud)}",
        x=0.5, y=0.1, showarrow=False,
        font=dict(color=C["text_muted"], size=11),
        align="center",
    )
    return fig


# Overhead treemap
@app.callback(
    Output("chart-overhead-tree", "figure"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def chart_overhead_tree(month, project, category):
    dfe = filter_expenses(month, project, category)
    oh = dfe[dfe["Project_ID"] == "GNRL"].copy()
    if oh.empty:
        return go.Figure(layout=chart_layout("Overhead Breakdown"))

    by_acc = oh.groupby("Account_Name")["Amount (RWF)"].sum().reset_index()
    by_acc = by_acc[by_acc["Amount (RWF)"] > 0]

    fig = go.Figure(go.Treemap(
        labels=by_acc["Account_Name"],
        parents=["Overheads"] * len(by_acc),
        values=by_acc["Amount (RWF)"],
        textinfo="label+value+percent parent",
        textfont=dict(size=11, color=C["text_main"]),
        marker=dict(
            colors=by_acc["Amount (RWF)"],
            colorscale=[[0, C["green_dark"]], [0.5, C["green_mid"]], [1, C["gold"]]],
            showscale=False,
            line=dict(color=C["bg_dark"], width=2),
        ),
        hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
        customdata=[fmt_rwf(v) for v in by_acc["Amount (RWF)"]],
    ))
    fig.update_layout(**chart_layout("Overhead Cost Breakdown (Treemap)"), height=360)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig


# Cumulative spend
@app.callback(
    Output("chart-cumulative", "figure"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def chart_cumulative(month, project, category):
    dfe = filter_expenses(month, project, category)
    monthly_total = dfe.groupby("Date")["Amount (RWF)"].sum().reset_index().sort_values("Date")
    monthly_total["Cumulative"] = monthly_total["Amount (RWF)"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_total["Date"], y=monthly_total["Amount (RWF)"] / 1e6,
        name="Monthly", marker_color=C["green_mid"],
        hovertemplate="%{x}<br>Monthly: RWF %{y:.2f}M<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=monthly_total["Date"], y=monthly_total["Cumulative"] / 1e6,
        name="Cumulative", mode="lines+markers",
        line=dict(color=C["gold"], width=2.5),
        marker=dict(size=9, color=C["gold"], symbol="diamond"),
        yaxis="y2",
        hovertemplate="%{x}<br>Cumulative: RWF %{y:.2f}M<extra></extra>",
    ))
    layout = chart_layout("Monthly vs Cumulative Spend (RWF M)")
    layout["yaxis"]["title"] = "Monthly (RWF M)"
    fig.update_layout(
        **layout,
        yaxis2=dict(
            title="Cumulative (RWF M)",
            overlaying="y", side="right",
            gridcolor=C["green_dark"],
            tickfont=dict(color=C["text_muted"], size=10),
        ),
        legend=dict(x=0.01, y=0.99),
    )
    return fig


# Detail table
@app.callback(
    Output("detail-table", "children"),
    Input("filter-month", "value"),
    Input("filter-project", "value"),
    Input("filter-category", "value"),
)
def update_table(month, project, category):
    dfe = filter_expenses(month, project, category)
    display = dfe[["Date", "Category", "Account_Name", "Project_ID", "Project_Name",
                   "Description", "Amount (RWF)"]].copy()
    display["Amount (RWF)"] = display["Amount (RWF)"].apply(lambda x: f"RWF {x:,.0f}")
    display.columns = ["Month", "Category", "Account", "Project ID", "Project Name",
                       "Description", "Amount (RWF)"]
    display["Project Name"] = display["Project Name"].apply(lambda x: x[:35] + "…" if len(str(x)) > 35 else x)
    display["Account"] = display["Account"].apply(lambda x: x[:30] + "…" if len(str(x)) > 30 else x)

    return dash_table.DataTable(
        data=display.to_dict("records"),
        columns=[{"name": c, "id": c} for c in display.columns],
        page_size=15,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": C["green_dark"],
            "color": C["gold"],
            "fontWeight": "700",
            "fontSize": "11px",
            "border": f"1px solid {C['border']}",
            "textTransform": "uppercase",
            "letterSpacing": "0.8px",
        },
        style_cell={
            "backgroundColor": C["bg_card"],
            "color": C["text_main"],
            "border": f"1px solid {C['green_dark']}",
            "fontSize": "12px",
            "padding": "8px 12px",
            "fontFamily": "Segoe UI",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": C["bg_card2"],
            },
            {
                "if": {"filter_query": '{Category} = "Overheads"'},
                "color": C["text_muted"],
            },
            {
                "if": {"column_id": "Amount (RWF)"},
                "color": C["gold_light"],
                "fontWeight": "600",
            },
        ],
        style_filter={
            "backgroundColor": C["green_dark"],
            "color": C["text_main"],
            "border": f"1px solid {C['border']}",
        },
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
