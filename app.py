import html
import io
import json
import math
import re
from copy import deepcopy
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


APP_NAME = "VSM Builder Pro MAX"
VERSION = "4.0"

DEFAULT_CONFIG = {
    "takt_mode": "Automatique",
    "takt": 1.0,
    "available_minutes": 480,
    "shifts": 1,
    "demande": 480,
    "fourn_nom": "Fournisseur A",
    "fourn_freq": "1/sem",
    "fourn_mode": "Routier",
    "ent_nom": "Mon Usine",
    "ent_erp": "SAP MRP",
    "cli_nom": "Client B",
    "cli_freq": "Quotidien",
}

DEFAULT_STEP = {
    "nom": "Nouvelle opération",
    "tc": 0.50,
    "tcs": 0.10,
    "pers": 1,
    "trs": 85,
    "stock_avant": 0,
    "stock_apres": 0,
}

DEFAULT_STEPS = [
    {
        "nom": "OP10 - Découpe",
        "tc": 0.50,
        "tcs": 0.20,
        "pers": 2,
        "trs": 85,
        "stock_avant": 0,
        "stock_apres": 4600,
    },
    {
        "nom": "OP20 - Usinage",
        "tc": 1.20,
        "tcs": 0.30,
        "pers": 3,
        "trs": 78,
        "stock_avant": 4600,
        "stock_apres": 1100,
    },
    {
        "nom": "OP30 - Assemblage",
        "tc": 0.80,
        "tcs": 0.10,
        "pers": 2,
        "trs": 90,
        "stock_avant": 1100,
        "stock_apres": 0,
    },
]

TEMPLATES = {
    "Usine standard": [
        {
            "nom": "Réception",
            "tc": 0.30,
            "tcs": 0.10,
            "pers": 1,
            "trs": 95,
            "stock_avant": 0,
            "stock_apres": 2000,
        },
        {
            "nom": "Préparation",
            "tc": 0.80,
            "tcs": 0.20,
            "pers": 2,
            "trs": 88,
            "stock_avant": 2000,
            "stock_apres": 1500,
        },
        {
            "nom": "Fabrication",
            "tc": 1.50,
            "tcs": 0.40,
            "pers": 4,
            "trs": 82,
            "stock_avant": 1500,
            "stock_apres": 800,
        },
        {
            "nom": "Contrôle",
            "tc": 0.40,
            "tcs": 0.10,
            "pers": 2,
            "trs": 92,
            "stock_avant": 800,
            "stock_apres": 500,
        },
        {
            "nom": "Expédition",
            "tc": 0.30,
            "tcs": 0.05,
            "pers": 1,
            "trs": 96,
            "stock_avant": 500,
            "stock_apres": 0,
        },
    ],
    "Ligne Lean": [
        {
            "nom": "OP10",
            "tc": 0.60,
            "tcs": 0.05,
            "pers": 1,
            "trs": 92,
            "stock_avant": 50,
            "stock_apres": 50,
        },
        {
            "nom": "OP20",
            "tc": 0.60,
            "tcs": 0.05,
            "pers": 1,
            "trs": 90,
            "stock_avant": 50,
            "stock_apres": 50,
        },
        {
            "nom": "OP30",
            "tc": 0.60,
            "tcs": 0.05,
            "pers": 1,
            "trs": 93,
            "stock_avant": 50,
            "stock_apres": 0,
        },
    ],
}


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(56,189,248,.13), transparent 27%),
        radial-gradient(circle at 90% 5%, rgba(139,92,246,.14), transparent 24%),
        #07101f;
    color: #e5eefb;
}

[data-testid="stSidebar"] {
    background: #091426;
    border-right: 1px solid rgba(148,163,184,.16);
}

.hero {
    padding: 32px;
    border-radius: 24px;
    margin-bottom: 24px;
    background: linear-gradient(125deg, #075985, #5b21b6 65%, #be185d);
    border: 1px solid rgba(255,255,255,.15);
    box-shadow: 0 20px 60px rgba(2,8,23,.50);
}

.hero h1 {
    color: white;
    font-size: clamp(2rem, 4vw, 3.2rem);
    margin: 0;
}

.hero p {
    color: #e0f2fe;
    margin: .6rem 0 0;
}

.badge {
    display: inline-block;
    padding: 6px 11px;
    margin-bottom: 12px;
    border-radius: 999px;
    background: rgba(255,255,255,.15);
    font-size: .78rem;
    font-weight: 700;
}

.kpi {
    min-height: 145px;
    padding: 19px;
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(30,41,59,.95), rgba(15,23,42,.98));
    border: 1px solid rgba(148,163,184,.16);
    box-shadow: 0 10px 30px rgba(0,0,0,.22);
}

.kpi-label {
    color: #94a3b8;
    font-size: .75rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 700;
}

.kpi-value {
    color: #f8fafc;
    font-size: 2rem;
    font-weight: 800;
    margin: 8px 0;
}

.kpi-hint {
    color: #94a3b8;
    font-size: .80rem;
}

.good { color: #4ade80; }
.warn { color: #fbbf24; }
.bad { color: #fb7185; }

[data-baseweb="tab-list"] {
    gap: 6px;
    padding: 7px;
    border-radius: 14px;
    overflow-x: auto;
    background: rgba(15,23,42,.75);
}

[data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 16px;
    white-space: nowrap;
}

[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(120deg, #0284c7, #7c3aed);
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 11px;
    font-weight: 700;
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(148,163,184,.17);
    border-radius: 14px;
    background: rgba(15,23,42,.68);
}

.action {
    padding: 14px 16px;
    margin: 8px 0;
    border-radius: 12px;
    background: #101c30;
    border-left: 4px solid #38bdf8;
}

.footer {
    text-align: center;
    color: #94a3b8;
    font-size: .82rem;
}

@media (max-width: 700px) {
    .hero {
        padding: 22px 18px;
    }

    .kpi {
        min-height: 120px;
        padding: 14px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def init_state():
    if "config" not in st.session_state:
        st.session_state.config = deepcopy(DEFAULT_CONFIG)

    if "current_steps" not in st.session_state:
        st.session_state.current_steps = deepcopy(DEFAULT_STEPS)

    if "future_steps" not in st.session_state:
        st.session_state.future_steps = deepcopy(DEFAULT_STEPS)


def clean_filename(name):
    clean = re.sub(r"[^A-Za-z0-9_-]+", "_", name.strip())
    return clean[:50] or "VSM"


def takt_time(config):
    if config["takt_mode"] == "Automatique":
        available_hours = (
            config["available_minutes"] * config["shifts"]
        ) / 60

        return available_hours / max(config["demande"], 1)

    return max(float(config["takt"]), 0.001)


def flow_inventories(steps):
    if not steps:
        return []

    stocks = [int(step["stock_avant"]) for step in steps]
    stocks.append(int(steps[-1]["stock_apres"]))

    return stocks


def analyse(steps, config):
    df = pd.DataFrame(steps)

    takt = takt_time(config)

    available_hours = (
        config["available_minutes"] * config["shifts"]
    ) / 60

    production_rate = (
        config["demande"] / available_hours
        if available_hours > 0
        else 1
    )

    inventories = flow_inventories(steps)
    total_stock = sum(inventories)

    total_va = float(df["tc"].sum())
    total_nva = total_stock / max(production_rate, 0.001)
    lead_time = total_va + total_nva

    trs_average = float(df["trs"].mean())
    total_changeover = float(df["tcs"].sum())

    pct_va = (
        total_va / lead_time * 100
        if lead_time > 0
        else 0
    )

    bottleneck = df.loc[df["tc"].idxmax()]

    capacities = []

    for step in steps:
        capacity = (
            available_hours
            * (step["trs"] / 100)
            / max(step["tc"], 0.001)
        )

        capacities.append(capacity)

    line_capacity = min(capacities) if capacities else 0

    return {
        "df": df,
        "takt": takt,
        "production_rate": production_rate,
        "inventories": inventories,
        "total_stock": total_stock,
        "va": total_va,
        "nva": total_nva,
        "lead_time": lead_time,
        "pct_va": pct_va,
        "trs": trs_average,
        "changeover": total_changeover,
        "bottleneck": bottleneck,
        "capacity": line_capacity,
        "can_meet_demand": line_capacity >= config["demande"],
    }


def action_plan(result, config):
    actions = []

    bottleneck = result["bottleneck"]

    if bottleneck["tc"] > result["takt"]:
        required_stations = math.ceil(
            bottleneck["tc"] / result["takt"]
        )

        reduction = bottleneck["tc"] - result["takt"]

        actions.append(
            f"Équilibrage : prévoir {required_stations} postes "
            f"parallèles au niveau « {bottleneck['nom']} » ou réduire "
            f"son temps de cycle de {reduction:.2f} h."
        )

    if result["nva"] > result["va"]:
        nva_percent = (
            result["nva"] / result["lead_time"] * 100
            if result["lead_time"] > 0
            else 0
        )

        actions.append(
            f"Flux tiré : réduire les encours de "
            f"{result['total_stock']:,} pièces. Ils représentent "
            f"{nva_percent:.1f}% du lead time."
        )

    if result["trs"] < 85:
        actions.append(
            f"TPM : améliorer le TRS moyen de "
            f"{result['trs']:.1f}% vers un minimum de 85%."
        )

    if result["changeover"] > result["va"] * 0.20:
        actions.append(
            f"SMED : les changements de série représentent "
            f"{result['changeover']:.2f} h. Standardiser les réglages."
        )

    if not result["can_meet_demand"]:
        actions.append(
            f"Capacité insuffisante : environ "
            f"{result['capacity']:.0f} pièces/jour pour une demande "
            f"de {config['demande']} pièces/jour."
        )

    if not actions:
        actions.append(
            "Aucune alerte critique. Maintenir le management visuel "
            "et poursuivre le Kaizen."
        )

    return actions


def metric_card(label, value, hint="", tone=""):
    st.markdown(
        f"""
        <div class="kpi">
            <div class="kpi-label">{html.escape(label)}</div>
            <div class="kpi-value {tone}">{html.escape(value)}</div>
            <div class="kpi-hint">{html.escape(hint)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def summary_dataframe(steps, result):
    rows = []

    for step in steps:
        waiting_time = (
            step["stock_avant"]
            / max(result["production_rate"], 0.001)
        )

        step_lead_time = step["tc"] + waiting_time

        va_percent = (
            step["tc"] / step_lead_time * 100
            if step_lead_time > 0
            else 0
        )

        rows.append(
            {
                "Étape": step["nom"],
                "C/T (h)": step["tc"],
                "C/O (h)": step["tcs"],
                "Opérateurs": step["pers"],
                "TRS %": step["trs"],
                "Stock avant": step["stock_avant"],
                "Stock après": step["stock_apres"],
                "Attente (h)": waiting_time,
                "Lead time (h)": step_lead_time,
                "% VA": va_percent,
            }
        )

    return pd.DataFrame(rows)


def render_editor(state_key, prefix):
    steps = st.session_state[state_key]

    col1, col2, col3 = st.columns(3)

    if col1.button(
        "＋ Ajouter une étape",
        key=f"{prefix}_add",
        use_container_width=True,
    ):
        new_step = deepcopy(DEFAULT_STEP)
        new_step["nom"] = f"OP{(len(steps) + 1) * 10}"
        steps.append(new_step)
        st.rerun()

    if col2.button(
        "⧉ Dupliquer la dernière",
        key=f"{prefix}_duplicate",
        use_container_width=True,
    ):
        new_step = deepcopy(steps[-1])
        new_step["nom"] += " - copie"
        steps.append(new_step)
        st.rerun()

    if col3.button(
        "↺ Réinitialiser",
        key=f"{prefix}_reset",
        use_container_width=True,
    ):
        if state_key == "current_steps":
            st.session_state[state_key] = deepcopy(DEFAULT_STEPS)
        else:
            st.session_state[state_key] = deepcopy(
                st.session_state.current_steps
            )

        st.rerun()

    for index, step in enumerate(steps):
        title = (
            f"{index + 1}. {step['nom']} · "
            f"C/T {step['tc']:.2f} h · TRS {step['trs']}%"
        )

        with st.expander(title, expanded=index == 0):
            h1, h2, h3, h4 = st.columns([5, 1, 1, 1])

            step["nom"] = h1.text_input(
                "Nom de l'étape",
                value=step["nom"],
                key=f"{prefix}_name_{index}",
            )

            if h2.button(
                "↑",
                key=f"{prefix}_up_{index}",
                disabled=index == 0,
                use_container_width=True,
            ):
                steps[index - 1], steps[index] = (
                    steps[index],
                    steps[index - 1],
                )
                st.rerun()

            if h3.button(
                "↓",
                key=f"{prefix}_down_{index}",
                disabled=index == len(steps) - 1,
                use_container_width=True,
            ):
                steps[index + 1], steps[index] = (
                    steps[index],
                    steps[index + 1],
                )
                st.rerun()

            if h4.button(
                "✕",
                key=f"{prefix}_delete_{index}",
                disabled=len(steps) == 1,
                use_container_width=True,
            ):
                steps.pop(index)
                st.rerun()

            c1, c2, c3, c4 = st.columns(4)

            step["tc"] = c1.number_input(
                "C/T (h/pièce)",
                min_value=0.0,
                value=float(step["tc"]),
                step=0.05,
                key=f"{prefix}_tc_{index}",
            )

            step["tcs"] = c2.number_input(
                "C/O (h)",
                min_value=0.0,
                value=float(step["tcs"]),
                step=0.05,
                key=f"{prefix}_co_{index}",
            )

            step["pers"] = c3.number_input(
                "Opérateurs",
                min_value=1,
                value=int(step["pers"]),
                key=f"{prefix}_operators_{index}",
            )

            step["trs"] = c4.slider(
                "TRS %",
                min_value=0,
                max_value=100,
                value=int(step["trs"]),
                key=f"{prefix}_trs_{index}",
            )

            c5, c6 = st.columns(2)

            step["stock_avant"] = c5.number_input(
                "Stock avant",
                min_value=0,
                value=int(step["stock_avant"]),
                key=f"{prefix}_stock_before_{index}",
            )

            step["stock_apres"] = c6.number_input(
                "Stock après",
                min_value=0,
                value=int(step["stock_apres"]),
                key=f"{prefix}_stock_after_{index}",
            )


def create_charts(result):
    df = result["df"]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Temps de cycle vs Takt Time",
            "TRS par étape",
        ),
    )

    cycle_colors = [
        "#22c55e" if value <= result["takt"] else "#fb7185"
        for value in df["tc"]
    ]

    fig.add_trace(
        go.Bar(
            x=df["nom"],
            y=df["tc"],
            marker_color=cycle_colors,
            text=df["tc"].round(2),
            textposition="outside",
        ),
        row=1,
        col=1,
    )

    fig.add_hline(
        y=result["takt"],
        line_dash="dash",
        line_color="#38bdf8",
        annotation_text=f"Takt {result['takt']:.3f} h",
        row=1,
        col=1,
    )

    trs_colors = [
        "#22c55e" if value >= 85 else "#f59e0b"
        for value in df["trs"]
    ]

    fig.add_trace(
        go.Bar(
            x=df["nom"],
            y=df["trs"],
            marker_color=trs_colors,
            text=df["trs"].astype(int),
            textposition="outside",
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dbeafe",
        showlegend=False,
    )

    fig.update_xaxes(
        gridcolor="rgba(148,163,184,.12)"
    )

    fig.update_yaxes(
        gridcolor="rgba(148,163,184,.12)"
    )

    return fig


def create_vsm_svg(steps, config, state_title):
    escape = lambda value: html.escape(str(value), quote=True)

    width = max(1180, 290 * len(steps) + 430)
    height = 470
    process_y = 190
    start_x = 245
    gap = 260

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',

        """
        <defs>
            <linearGradient id="processGradient" x1="0" x2="1">
                <stop stop-color="#0284c7"/>
                <stop offset="1" stop-color="#7c3aed"/>
            </linearGradient>

            <marker id="arrow" markerWidth="9" markerHeight="7"
                    refX="8" refY="3.5" orient="auto">
                <polygon points="0 0, 9 3.5, 0 7" fill="#94a3b8"/>
            </marker>
        </defs>
        """,

        '<rect width="100%" height="100%" rx="22" fill="#081426"/>',

        f'<text x="{width / 2}" y="38" text-anchor="middle" '
        f'fill="#f8fafc" font-size="22" font-weight="700">'
        f'{escape(config["ent_nom"])} · {escape(state_title)}</text>',

        f'<g transform="translate(35,{process_y})">'
        f'<rect width="170" height="110" rx="13" fill="#075985"/>'
        f'<text x="85" y="30" text-anchor="middle" '
        f'fill="white" font-weight="700">FOURNISSEUR</text>'
        f'<text x="85" y="57" text-anchor="middle" fill="#dbeafe">'
        f'{escape(config["fourn_nom"])}</text>'
        f'<text x="85" y="82" text-anchor="middle" fill="#bae6fd">'
        f'{escape(config["fourn_freq"])} · '
        f'{escape(config["fourn_mode"])}</text></g>',

        f'<g transform="translate({width - 205},{process_y})">'
        f'<rect width="170" height="110" rx="13" fill="#047857"/>'
        f'<text x="85" y="30" text-anchor="middle" '
        f'fill="white" font-weight="700">CLIENT</text>'
        f'<text x="85" y="57" text-anchor="middle" fill="#d1fae5">'
        f'{escape(config["cli_nom"])}</text>'
        f'<text x="85" y="82" text-anchor="middle" fill="#a7f3d0">'
        f'{config["demande"]} pcs/jour</text></g>',

        f'<g transform="translate({width / 2 - 105},75)">'
        f'<rect width="210" height="62" rx="11" fill="#f59e0b"/>'
        f'<text x="105" y="25" text-anchor="middle" '
        f'fill="#111827" font-weight="700">CONTRÔLE PRODUCTION</text>'
        f'<text x="105" y="47" text-anchor="middle" fill="#111827">'
        f'{escape(config["ent_erp"])}</text></g>',
    ]

    for index, step in enumerate(steps):
        x = start_x + index * gap

        if step["trs"] >= 85:
            trs_color = "#22c55e"
        elif step["trs"] >= 70:
            trs_color = "#f59e0b"
        else:
            trs_color = "#fb7185"

        svg.append(
            f'<g transform="translate({x},{process_y})">'
            f'<rect width="205" height="135" rx="12" '
            f'fill="#17243a" stroke="#38bdf8" stroke-width="2"/>'
            f'<rect width="205" height="34" rx="12" '
            f'fill="url(#processGradient)"/>'
            f'<text x="102" y="23" text-anchor="middle" '
            f'fill="white" font-size="13" font-weight="700">'
            f'{escape(step["nom"][:28])}</text>'
            f'<text x="15" y="61" fill="#94a3b8">C/T</text>'
            f'<text x="105" y="61" fill="white">'
            f'{step["tc"]:.2f} h</text>'
            f'<text x="15" y="84" fill="#94a3b8">C/O</text>'
            f'<text x="105" y="84" fill="white">'
            f'{step["tcs"]:.2f} h</text>'
            f'<text x="15" y="107" fill="#94a3b8">Opér.</text>'
            f'<text x="105" y="107" fill="white">'
            f'{step["pers"]}</text>'
            f'<text x="15" y="127" fill="#94a3b8">TRS</text>'
            f'<text x="105" y="127" fill="{trs_color}" '
            f'font-weight="700">{step["trs"]}%</text></g>'
        )

        svg.append(
            f'<g transform="translate({x - 43},{process_y + 46})">'
            f'<polygon points="22,0 44,34 0,34" fill="#fbbf24"/>'
            f'<text x="22" y="50" text-anchor="middle" '
            f'fill="#fde68a" font-size="10">'
            f'{step["stock_avant"]}</text></g>'
        )

        svg.append(
            f'<line x1="{x + 205}" y1="{process_y + 68}" '
            f'x2="{x + gap}" y2="{process_y + 68}" '
            f'stroke="#94a3b8" stroke-width="2" '
            f'stroke-dasharray="7 5" marker-end="url(#arrow)"/>'
        )

        svg.append(
            f'<line x1="{width / 2}" y1="137" '
            f'x2="{x + 102}" y2="{process_y}" '
            f'stroke="#38bdf8" stroke-dasharray="4 5"/>'
        )

    if steps:
        last_x = start_x + (len(steps) - 1) * gap + 225

        svg.append(
            f'<polygon points="{last_x},{process_y + 46} '
            f'{last_x + 22},{process_y + 80} '
            f'{last_x - 22},{process_y + 80}" fill="#fbbf24"/>'
            f'<text x="{last_x}" y="{process_y + 98}" '
            f'text-anchor="middle" fill="#fde68a" font-size="10">'
            f'{steps[-1]["stock_apres"]}</text>'
        )

    svg.append(
        f'<text x="{width / 2}" y="430" text-anchor="middle" '
        f'fill="#94a3b8" font-size="12">'
        f'Takt Time : {takt_time(config):.3f} h/pièce · '
        f'Flux matière en pointillés · Flux information en bleu'
        f'</text></svg>'
    )

    return "".join(svg)


def create_excel(current, future, config):
    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter",
    ) as writer:
        pd.DataFrame([config]).to_excel(
            writer,
            sheet_name="Configuration",
            index=False,
        )

        summary_dataframe(
            st.session_state.current_steps,
            current,
        ).to_excel(
            writer,
            sheet_name="Current State",
            index=False,
        )

        summary_dataframe(
            st.session_state.future_steps,
            future,
        ).to_excel(
            writer,
            sheet_name="Future State",
            index=False,
        )

        comparison = pd.DataFrame(
            {
                "Indicateur": [
                    "Lead time (h)",
                    "VA (%)",
                    "TRS (%)",
                    "Stock (pcs)",
                    "Capacité (pcs/j)",
                ],
                "Current State": [
                    current["lead_time"],
                    current["pct_va"],
                    current["trs"],
                    current["total_stock"],
                    current["capacity"],
                ],
                "Future State": [
                    future["lead_time"],
                    future["pct_va"],
                    future["trs"],
                    future["total_stock"],
                    future["capacity"],
                ],
            }
        )

        comparison.to_excel(
            writer,
            sheet_name="Comparaison",
            index=False,
        )

    return output.getvalue()


def create_pdf(current, future, config):
    output = io.BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
    )

    styles = getSampleStyleSheet()

    content = [
        Paragraph(
            f"Rapport VSM - {html.escape(config['ent_nom'])}",
            styles["Title"],
        ),
        Paragraph(
            f"Généré le {datetime.now():%d/%m/%Y %H:%M}",
            styles["Normal"],
        ),
        Spacer(1, 20),
    ]

    table_data = [
        [
            "Indicateur",
            "Current State",
            "Future State",
        ],
        [
            "Lead time",
            f"{current['lead_time']:.2f} h",
            f"{future['lead_time']:.2f} h",
        ],
        [
            "Valeur ajoutée",
            f"{current['pct_va']:.2f}%",
            f"{future['pct_va']:.2f}%",
        ],
        [
            "TRS moyen",
            f"{current['trs']:.1f}%",
            f"{future['trs']:.1f}%",
        ],
        [
            "Stock",
            f"{current['total_stock']:,}",
            f"{future['total_stock']:,}",
        ],
        [
            "Capacité",
            f"{current['capacity']:.0f} pcs/j",
            f"{future['capacity']:.0f} pcs/j",
        ],
    ]

    table = Table(table_data)

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#075985"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
            ]
        )
    )

    content.append(table)
    content.append(Spacer(1, 20))
    content.append(
        Paragraph("Plan d'action", styles["Heading2"])
    )

    for action in action_plan(current, config):
        content.append(
            Paragraph(
                f"• {html.escape(action)}",
                styles["BodyText"],
            )
        )

    document.build(content)

    return output.getvalue()


def import_project(uploaded_file):
    try:
        data = json.load(uploaded_file)

        current_steps = data.get(
            "current_state",
            data.get("etapes"),
        )

        if not isinstance(current_steps, list):
            raise ValueError(
                "Le fichier ne contient pas d'étapes valides."
            )

        st.session_state.current_steps = current_steps
        st.session_state.future_steps = data.get(
            "future_state",
            deepcopy(current_steps),
        )

        imported_config = deepcopy(DEFAULT_CONFIG)
        imported_config.update(data.get("config", {}))
        st.session_state.config = imported_config

        return True

    except Exception as error:
        st.error(f"Import impossible : {error}")
        return False


init_state()

config = st.session_state.config

st.markdown(
    f"""
<section class="hero">
    <span class="badge">LEAN DIGITAL SUITE · VERSION {VERSION}</span>
    <h1>{APP_NAME}</h1>
    <p>
        Construisez, analysez et améliorez votre flux
        avec Current State et Future State.
    </p>
</section>
""",
    unsafe_allow_html=True,
)


with st.sidebar:
    st.markdown("## Configuration générale")

    template = st.selectbox(
        "Template",
        ["Personnalisé"] + list(TEMPLATES.keys()),
    )

    if (
        template != "Personnalisé"
        and st.button(
            "Appliquer le template",
            use_container_width=True,
        )
    ):
        st.session_state.current_steps = deepcopy(
            TEMPLATES[template]
        )

        st.session_state.future_steps = deepcopy(
            TEMPLATES[template]
        )

        st.rerun()

    st.divider()
    st.markdown("#### Demande et temps")

    config["takt_mode"] = st.radio(
        "Calcul du Takt Time",
        ["Automatique", "Manuel"],
        index=(
            0
            if config["takt_mode"] == "Automatique"
            else 1
        ),
        horizontal=True,
    )

    config["demande"] = st.number_input(
        "Demande client (pcs/jour)",
        min_value=1,
        value=int(config["demande"]),
    )

    time_col1, time_col2 = st.columns(2)

    config["available_minutes"] = time_col1.number_input(
        "Minutes/équipe",
        min_value=1,
        value=int(config["available_minutes"]),
    )

    config["shifts"] = time_col2.number_input(
        "Équipes/jour",
        min_value=1,
        max_value=10,
        value=int(config["shifts"]),
    )

    if config["takt_mode"] == "Manuel":
        config["takt"] = st.number_input(
            "Takt manuel (h/pièce)",
            min_value=0.001,
            value=float(config["takt"]),
            step=0.01,
            format="%.3f",
        )

    st.info(
        f"Takt utilisé : {takt_time(config):.3f} h/pièce"
    )

    st.divider()
    st.markdown("#### Fournisseur")

    config["fourn_nom"] = st.text_input(
        "Nom du fournisseur",
        config["fourn_nom"],
    )

    config["fourn_freq"] = st.selectbox(
        "Fréquence d'approvisionnement",
        ["1/sem", "2/sem", "Quotidien"],
    )

    config["fourn_mode"] = st.selectbox(
        "Mode de transport",
        ["Routier", "Ferroviaire", "Aérien", "Maritime"],
    )

    st.divider()
    st.markdown("#### Entreprise et client")

    config["ent_nom"] = st.text_input(
        "Entreprise",
        config["ent_nom"],
    )

    config["ent_erp"] = st.text_input(
        "ERP / système",
        config["ent_erp"],
    )

    config["cli_nom"] = st.text_input(
        "Client",
        config["cli_nom"],
    )

    config["cli_freq"] = st.selectbox(
        "Fréquence de livraison",
        [
            "1/sem",
            "2/sem",
            "Quotidien",
            "Just-in-Time",
        ],
        index=2,
    )

    st.divider()

    uploaded = st.file_uploader(
        "Importer un projet JSON",
        type="json",
    )

    if (
        uploaded is not None
        and st.button(
            "Valider l'import",
            use_container_width=True,
        )
    ):
        if import_project(uploaded):
            st.success("Projet importé avec succès.")
            st.rerun()


current_result = analyse(
    st.session_state.current_steps,
    config,
)

future_result = analyse(
    st.session_state.future_steps,
    config,
)

tabs = st.tabs(
    [
        "🧩 Current State",
        "🗺️ Carte VSM",
        "📊 Analyse",
        "🚀 Future State",
        "📄 Rapport & exports",
    ]
)


with tabs[0]:
    st.subheader("Édition du flux actuel")

    st.caption(
        "Les temps sont exprimés en heures par pièce. "
        "Les stocks sont comptés une seule fois."
    )

    render_editor(
        "current_steps",
        "current",
    )


with tabs[1]:
    st.subheader("Cartographie VSM")

    current_svg = create_vsm_svg(
        st.session_state.current_steps,
        config,
        "Current State",
    )

    st.components.v1.html(
        f"""
        <div style="overflow-x:auto;border-radius:22px">
            {current_svg}
        </div>
        """,
        height=500,
        scrolling=True,
    )

    st.download_button(
        "Télécharger la carte SVG",
        data=current_svg,
        file_name=(
            f"VSM_{clean_filename(config['ent_nom'])}.svg"
        ),
        mime="image/svg+xml",
    )

    st.plotly_chart(
        create_charts(current_result),
        use_container_width=True,
    )

    current_summary = summary_dataframe(
        st.session_state.current_steps,
        current_result,
    )

    st.dataframe(
        current_summary.style.format(
            {
                "C/T (h)": "{:.2f}",
                "C/O (h)": "{:.2f}",
                "Attente (h)": "{:.2f}",
                "Lead time (h)": "{:.2f}",
                "% VA": "{:.2f}%",
            }
        ).background_gradient(
            subset=["TRS %", "% VA"],
            cmap="RdYlGn",
        ),
        use_container_width=True,
        hide_index=True,
    )


with tabs[2]:
    st.subheader("Cockpit de performance Lean")

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        metric_card(
            "Lead time",
            f"{current_result['lead_time']:.1f} h",
            (
                f"VA {current_result['va']:.2f} h · "
                f"NVA {current_result['nva']:.1f} h"
            ),
        )

    with kpi2:
        metric_card(
            "Valeur ajoutée",
            f"{current_result['pct_va']:.2f}%",
            "Part du lead time",
            (
                "good"
                if current_result["pct_va"] >= 25
                else "warn"
            ),
        )

    with kpi3:
        metric_card(
            "Takt Time",
            f"{current_result['takt']:.3f} h",
            f"{config['demande']} pcs/jour",
        )

    with kpi4:
        metric_card(
            "TRS moyen",
            f"{current_result['trs']:.1f}%",
            "Objectif ≥ 85%",
            (
                "good"
                if current_result["trs"] >= 85
                else "warn"
            ),
        )

    with kpi5:
        metric_card(
            "Capacité",
            f"{current_result['capacity']:.0f} pcs/j",
            (
                "Demande couverte"
                if current_result["can_meet_demand"]
                else "Sous-capacité"
            ),
            (
                "good"
                if current_result["can_meet_demand"]
                else "bad"
            ),
        )

    st.plotly_chart(
        create_charts(current_result),
        use_container_width=True,
    )

    bottleneck = current_result["bottleneck"]

    if bottleneck["tc"] > current_result["takt"]:
        st.error(
            f"Goulot critique : **{bottleneck['nom']}** — "
            f"C/T {bottleneck['tc']:.2f} h > "
            f"Takt {current_result['takt']:.3f} h."
        )
    else:
        st.success(
            f"Goulot maîtrisé : **{bottleneck['nom']}** — "
            f"C/T {bottleneck['tc']:.2f} h ≤ "
            f"Takt {current_result['takt']:.3f} h."
        )

    st.markdown("#### Plan d'action priorisé")

    for number, action in enumerate(
        action_plan(current_result, config),
        start=1,
    ):
        st.markdown(
            f"""
            <div class="action">
                <b>{number:02d}</b> · {html.escape(action)}
            </div>
            """,
            unsafe_allow_html=True,
        )


with tabs[3]:
    st.subheader("Conception du Future State")

    st.caption(
        "Modifiez votre objectif futur sans modifier "
        "la situation actuelle."
    )

    if st.button(
        "Copier le Current State",
        use_container_width=True,
    ):
        st.session_state.future_steps = deepcopy(
            st.session_state.current_steps
        )

        st.rerun()

    if current_result["lead_time"] > 0:
        lead_gain = (
            1
            - future_result["lead_time"]
            / current_result["lead_time"]
        ) * 100
    else:
        lead_gain = 0

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        metric_card(
            "Gain lead time",
            f"{lead_gain:+.1f}%",
            (
                f"{current_result['lead_time']:.1f} → "
                f"{future_result['lead_time']:.1f} h"
            ),
            "good" if lead_gain > 0 else "warn",
        )

    with f2:
        metric_card(
            "Gain TRS",
            (
                f"{future_result['trs'] - current_result['trs']:+.1f} pts"
            ),
            (
                f"{current_result['trs']:.1f}% → "
                f"{future_result['trs']:.1f}%"
            ),
        )

    with f3:
        metric_card(
            "Réduction stock",
            (
                f"{current_result['total_stock'] - future_result['total_stock']:+,}"
            ),
            (
                f"{current_result['total_stock']:,} → "
                f"{future_result['total_stock']:,} pcs"
            ),
        )

    with f4:
        metric_card(
            "Gain capacité",
            (
                f"{future_result['capacity'] - current_result['capacity']:+.0f}"
            ),
            (
                f"{current_result['capacity']:.0f} → "
                f"{future_result['capacity']:.0f} pcs/j"
            ),
        )

    render_editor(
        "future_steps",
        "future",
    )

    future_svg = create_vsm_svg(
        st.session_state.future_steps,
        config,
        "Future State",
    )

    st.components.v1.html(
        f"""
        <div style="overflow-x:auto;border-radius:22px">
            {future_svg}
        </div>
        """,
        height=500,
        scrolling=True,
    )


with tabs[4]:
    st.subheader("Rapport professionnel et exports")

    company_name = clean_filename(
        config["ent_nom"]
    )

    project_data = {
        "metadata": {
            "app": APP_NAME,
            "version": VERSION,
            "exported_at": datetime.now().isoformat(
                timespec="seconds"
            ),
        },
        "config": config,
        "current_state": st.session_state.current_steps,
        "future_state": st.session_state.future_steps,
    }

    export1, export2, export3, export4 = st.columns(4)

    export1.download_button(
        "⬇ PDF",
        data=create_pdf(
            current_result,
            future_result,
            config,
        ),
        file_name=f"Rapport_VSM_{company_name}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    export2.download_button(
        "⬇ Excel",
        data=create_excel(
            current_result,
            future_result,
            config,
        ),
        file_name=f"Analyse_VSM_{company_name}.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
    )

    export3.download_button(
        "⬇ JSON",
        data=json.dumps(
            project_data,
            ensure_ascii=False,
            indent=2,
        ),
        file_name=f"Projet_VSM_{company_name}.json",
        mime="application/json",
        use_container_width=True,
    )

    export4.download_button(
        "⬇ SVG",
        data=create_vsm_svg(
            st.session_state.current_steps,
            config,
            "Current State",
        ),
        file_name=f"Carte_VSM_{company_name}.svg",
        mime="image/svg+xml",
        use_container_width=True,
    )

    comparison = pd.DataFrame(
        {
            "Indicateur": [
                "Lead time (h)",
                "Valeur ajoutée (%)",
                "TRS moyen (%)",
                "Stock total (pcs)",
                "Capacité (pcs/j)",
            ],
            "Current State": [
                current_result["lead_time"],
                current_result["pct_va"],
                current_result["trs"],
                current_result["total_stock"],
                current_result["capacity"],
            ],
            "Future State": [
                future_result["lead_time"],
                future_result["pct_va"],
                future_result["trs"],
                future_result["total_stock"],
                future_result["capacity"],
            ],
        }
    )

    st.markdown("#### Synthèse exécutive")

    st.dataframe(
        comparison.style.format(
            {
                "Current State": "{:,.2f}",
                "Future State": "{:,.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Actions recommandées")

    for action in action_plan(
        current_result,
        config,
    ):
        st.markdown(f"- {action}")


st.divider()

st.markdown(
    f"""
    <p class="footer">
        <b>{APP_NAME} v{VERSION}</b> · Current/Future State ·
        KPIs Lean · PDF · Excel · JSON · SVG
    </p>
    """,
    unsafe_allow_html=True,
)
