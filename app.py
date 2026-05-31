import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime

st.set_page_config(page_title="VSM Builder Pro MAX", page_icon="factory", layout="wide", initial_sidebar_state="expanded")

st.markdown('''
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap");
* { font-family: 'Inter', sans-serif; }
.main { background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); color: #e2e8f0; }
.main-header { background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%); padding: 2rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 20px 60px rgba(59, 130, 246, 0.3); text-align: center; position: relative; overflow: hidden; }
.main-header::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px); background-size: 20px 20px; animation: moveGrid 20s linear infinite; }
@keyframes moveGrid { 0% { transform: translate(0, 0); } 100% { transform: translate(20px, 20px); } }
.main-header h1 { font-size: 3rem !important; font-weight: 800 !important; color: white !important; text-shadow: 0 2px 10px rgba(0,0,0,0.2); position: relative; z-index: 1; }
.main-header p { font-size: 1.2rem !important; color: rgba(255,255,255,0.9) !important; position: relative; z-index: 1; }
.metric-card { background: linear-gradient(145deg, #1e293b, #334155); border-radius: 16px; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.3); transition: all 0.3s ease; position: relative; overflow: hidden; }
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899); }
.metric-card:hover { transform: translateY(-5px); box-shadow: 0 12px 40px rgba(59, 130, 246, 0.2); }
.metric-value { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.metric-label { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); border-right: 1px solid rgba(255,255,255,0.1); }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background: rgba(30, 41, 59, 0.5); padding: 8px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); }
.stTabs [data-baseweb="tab"] { border-radius: 12px; padding: 12px 24px; font-weight: 600; color: #94a3b8; transition: all 0.3s ease; }
.stTabs [data-baseweb="tab"]:hover { background: rgba(59, 130, 246, 0.2); color: #e2e8f0; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }
.stButton > button { border-radius: 12px !important; font-weight: 600 !important; transition: all 0.3s ease !important; border: none !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3) !important; }
.streamlit-expander { border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 16px !important; background: linear-gradient(145deg, #1e293b, #0f172a) !important; margin-bottom: 1rem !important; overflow: hidden; }
.streamlit-expanderHeader { background: linear-gradient(90deg, #1e293b, #334155) !important; color: #e2e8f0 !important; font-weight: 600 !important; padding: 1rem 1.5rem !important; }
.stNumberInput input, .stTextInput input, .stSelectbox select { border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.2) !important; background: rgba(15, 23, 42, 0.8) !important; color: #e2e8f0 !important; }
.stAlert { border-radius: 16px !important; border: none !important; }
.stDataFrame { border-radius: 16px !important; overflow: hidden !important; }
.stProgress > div > div { border-radius: 10px !important; background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important; }
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #3b82f6, #8b5cf6); border-radius: 4px; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
.animate-in { animation: fadeInUp 0.6s ease-out forwards; }
h2, h3 { color: #e2e8f0 !important; font-weight: 700 !important; }
h2 { border-bottom: 2px solid; border-image: linear-gradient(90deg, #3b82f6, #8b5cf6) 1; padding-bottom: 0.5rem; margin-bottom: 1.5rem !important; }
</style>
''', unsafe_allow_html=True)

def create_gauge_chart(value, title, max_val=100, color="blue"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#e2e8f0'}},
        gauge={'axis': {'range': [None, max_val], 'tickcolor': '#94a3b8'}, 'bar': {'color': color, 'thickness': 0.75}, 'bgcolor': '#1e293b', 'borderwidth': 2, 'bordercolor': '#334155', 'steps': [{'range': [0, max_val*0.5], 'color': '#1e293b'}, {'range': [max_val*0.5, max_val*0.8], 'color': '#1e293b'}, {'range': [max_val*0.8, max_val], 'color': '#1e293b'}], 'threshold': {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': max_val * 0.85}}
    ))
    fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'})
    return fig

def create_vsm_timeline(df, takt):
    fig = make_subplots(rows=2, cols=1, subplot_titles=('Timeline VA/NVA', 'Capacite vs Takt Time'), vertical_spacing=0.15, row_heights=[0.6, 0.4])
    fig.add_trace(go.Bar(x=df['nom'], y=df['VA (h)'], name='VA - Temps Cycle', marker_color='#10b981', text=df['VA (h)'].round(2), textposition='inside', hovertemplate='<b>%{x}</b><br>VA: %{y:.2f}h<extra></extra>'), row=1, col=1)
    fig.add_trace(go.Bar(x=df['nom'], y=df['NVA (h)'], name='NVA - Attente Stock', marker_color='#f43f5e', text=df['NVA (h)'].round(2), textposition='inside', hovertemplate='<b>%{x}</b><br>NVA: %{y:.2f}h<extra></extra>'), row=1, col=1)
    colors = ['#10b981' if tc <= takt else '#f43f5e' for tc in df['tc']]
    fig.add_trace(go.Bar(x=df['nom'], y=df['tc'], name='Temps Cycle', marker_color=colors, text=df['tc'].round(2), textposition='outside', hovertemplate='<b>%{x}</b><br>TC: %{y:.2f}h<extra></extra>'), row=2, col=1)
    fig.add_hline(y=takt, line_dash="dash", line_color="#3b82f6", line_width=3, annotation_text=f"Takt Time = {takt}h", row=2, col=1)
    fig.update_layout(barmode='stack', height=600, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0', 'size': 12}, legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, bgcolor='rgba(0,0,0,0.5)'), xaxis=dict(gridcolor='rgba(255,255,255,0.1)'), yaxis=dict(gridcolor='rgba(255,255,255,0.1)'), xaxis2=dict(gridcolor='rgba(255,255,255,0.1)'), yaxis2=dict(gridcolor='rgba(255,255,255,0.1)'))
    return fig

def create_vsm_svg(etapes, config):
    width = max(1200, len(etapes) * 300 + 400)
    height = 500
    svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">'
    svg += '<defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" /><stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" /></linearGradient><linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#10b981;stop-opacity:1" /><stop offset="100%" style="stop-color:#34d399;stop-opacity:1" /></linearGradient><filter id="glow"><feGaussianBlur stdDeviation="3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter><marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6" /></marker><marker id="arrowhead-dashed" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" /></marker></defs>'
    svg += '<rect width="100%" height="100%" fill="#0f172a"/><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/></pattern><rect width="100%" height="100%" fill="url(#grid)"/>'
    svg += f'<text x="{width/2}" y="40" text-anchor="middle" fill="url(#grad1)" font-size="24" font-weight="bold" filter="url(#glow)">Value Stream Mapping - {config["ent_nom"]}</text>'
    svg += f'<g transform="translate(50, 150)"><rect x="0" y="0" width="180" height="120" rx="15" fill="url(#grad1)" opacity="0.9" filter="url(#glow)"/><text x="90" y="35" text-anchor="middle" fill="white" font-size="14" font-weight="bold">FOURNISSEUR</text><text x="90" y="60" text-anchor="middle" fill="white" font-size="12">{config["fourn_nom"]}</text><text x="90" y="80" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="11">{config["fourn_freq"]}</text><text x="90" y="100" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="11">{config["fourn_mode"]}</text></g>'
    svg += f'<g transform="translate({width/2 - 100}, 80)"><rect x="0" y="0" width="200" height="60" rx="10" fill="#fbbf24" opacity="0.9" filter="url(#glow)"/><text x="100" y="25" text-anchor="middle" fill="#1e293b" font-size="14" font-weight="bold">CONTROLE PRODUCTION</text><text x="100" y="45" text-anchor="middle" fill="#1e293b" font-size="12">{config["ent_erp"]}</text></g>'
    svg += f'<g transform="translate({width - 230}, 150)"><rect x="0" y="0" width="180" height="120" rx="15" fill="url(#grad2)" opacity="0.9" filter="url(#glow)"/><text x="90" y="35" text-anchor="middle" fill="white" font-size="14" font-weight="bold">CLIENT</text><text x="90" y="60" text-anchor="middle" fill="white" font-size="12">{config["cli_nom"]}</text><text x="90" y="80" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="11">Takt: {config["takt"]}h</text><text x="90" y="100" text-anchor="middle" fill="rgba(255,255,255,0.8)" font-size="11">{config["demande"]}/jour</text></g>'
    x_start = 280
    x_step = 250
    y_process = 180
    for i, e in enumerate(etapes):
        x = x_start + i * x_step
        trs_color = "#10b981" if e["trs"] >= 85 else "#f43f5e"
        svg += f'<g transform="translate({x}, {y_process})"><rect x="0" y="0" width="200" height="140" rx="12" fill="#334155" stroke="url(#grad1)" stroke-width="2" filter="url(#glow)"/><rect x="0" y="0" width="200" height="35" rx="12" fill="url(#grad1)"/><text x="100" y="24" text-anchor="middle" fill="white" font-size="14" font-weight="bold">{e["nom"]}</text><text x="15" y="60" fill="#94a3b8" font-size="11">C/T</text><text x="100" y="60" fill="white" font-size="12" font-weight="600">{e["tc"]}h</text><text x="15" y="80" fill="#94a3b8" font-size="11">C/O</text><text x="100" y="80" fill="white" font-size="12" font-weight="600">{e["tcs"]}h</text><text x="15" y="100" fill="#94a3b8" font-size="11">Oper.</text><text x="100" y="100" fill="white" font-size="12" font-weight="600">{e["pers"]}</text><text x="15" y="120" fill="#94a3b8" font-size="11">TRS</text><text x="100" y="120" fill="{trs_color}" font-size="12" font-weight="600">{e["trs"]}%</text></g>'
        if e['stock_avant'] > 0:
            svg += f'<g transform="translate({x - 60}, {y_process + 50})"><polygon points="30,0 60,40 0,40" fill="#fbbf24" opacity="0.8" stroke="#f59e0b" stroke-width="2"/><text x="30" y="55" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="bold">I = {e["stock_avant"]}</text></g>'
        if i < len(etapes) - 1:
            svg += f'<line x1="{x + 200}" y1="{y_process + 70}" x2="{x + x_step}" y2="{y_process + 70}" stroke="#94a3b8" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrowhead-dashed)"/>'
    last_x = x_start + (len(etapes) - 1) * x_step + 200
    if etapes[-1]['stock_apres'] > 0:
        svg += f'<g transform="translate({last_x + 20}, {y_process + 50})"><polygon points="30,0 60,40 0,40" fill="#fbbf24" opacity="0.8" stroke="#f59e0b" stroke-width="2"/><text x="30" y="55" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="bold">I = {etapes[-1]["stock_apres"]}</text></g>'
    offset = 80 if etapes[-1]['stock_apres'] > 0 else 0
    svg += f'<line x1="{last_x + offset}" y1="{y_process + 70}" x2="{width - 250}" y2="{y_process + 70}" stroke="#94a3b8" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrowhead-dashed)"/>'
    svg += f'<line x1="230" y1="{y_process + 70}" x2="{x_start}" y2="{y_process + 70}" stroke="#94a3b8" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#arrowhead-dashed)"/>'
    svg += f'<path d="M {width - 140} 150 Q {width/2} 100 {width/2 + 100} 140" fill="none" stroke="#3b82f6" stroke-width="3" marker-end="url(#arrowhead)"/><text x="{(width - 140 + width/2 + 100)/2}" y="115" fill="#3b82f6" font-size="11" font-weight="bold">Commande</text>'
    svg += f'<path d="M {width/2 - 100} 140 Q {width/4} 100 140 150" fill="none" stroke="#3b82f6" stroke-width="3" marker-end="url(#arrowhead)"/><text x="{(width/2 - 100 + 140)/2}" y="115" fill="#3b82f6" font-size="11" font-weight="bold">Ordre Achat</text>'
    for i in range(len(etapes)):
        x = x_start + i * x_step + 100
        svg += f'<line x1="{width/2}" y1="140" x2="{x}" y2="{y_process}" stroke="#3b82f6" stroke-width="2" stroke-dasharray="5,5" marker-end="url(#arrowhead)"/>'
    svg += '</svg>'
    return svg

def init_session():
    if 'etapes' not in st.session_state:
        st.session_state.etapes = [
            {"nom": "OP10 - Decoupe", "tc": 0.5, "tcs": 0.2, "pers": 2, "trs": 85, "stock_avant": 0, "stock_apres": 4600},
            {"nom": "OP20 - Usinage", "tc": 1.2, "tcs": 0.3, "pers": 3, "trs": 78, "stock_avant": 4600, "stock_apres": 1100},
            {"nom": "OP30 - Assemblage", "tc": 0.8, "tcs": 0.1, "pers": 2, "trs": 90, "stock_avant": 1100, "stock_apres": 0},
        ]
    if 'config' not in st.session_state:
        st.session_state.config = {
            "takt": 1.0, "demande": 480,
            "fourn_nom": "Fournisseur A", "fourn_freq": "1/sem", "fourn_mode": "Routier",
            "ent_nom": "Mon Usine", "ent_erp": "SAP MRP",
            "cli_nom": "Client B", "cli_freq": "1/sem",
        }
    if 'templates' not in st.session_state:
        st.session_state.templates = {
            "Usine Standard": {
                "etapes": [
                    {"nom": "OP10 - Reception", "tc": 0.3, "tcs": 0.1, "pers": 1, "trs": 95, "stock_avant": 0, "stock_apres": 2000},
                    {"nom": "OP20 - Preparation", "tc": 0.8, "tcs": 0.2, "pers": 2, "trs": 88, "stock_avant": 2000, "stock_apres": 1500},
                    {"nom": "OP30 - Fabrication", "tc": 1.5, "tcs": 0.4, "pers": 4, "trs": 82, "stock_avant": 1500, "stock_apres": 800},
                    {"nom": "OP40 - Controle", "tc": 0.4, "tcs": 0.1, "pers": 2, "trs": 92, "stock_avant": 800, "stock_apres": 500},
                    {"nom": "OP50 - Expedition", "tc": 0.3, "tcs": 0.05, "pers": 1, "trs": 96, "stock_avant": 500, "stock_apres": 0},
                ],
                "config": {"takt": 1.2, "demande": 400}
            },
            "Ligne Lean": {
                "etapes": [
                    {"nom": "OP10", "tc": 0.6, "tcs": 0.05, "pers": 1, "trs": 92, "stock_avant": 50, "stock_apres": 50},
                    {"nom": "OP20", "tc": 0.6, "tcs": 0.05, "pers": 1, "trs": 90, "stock_avant": 50, "stock_apres": 50},
                    {"nom": "OP30", "tc": 0.6, "tcs": 0.05, "pers": 1, "trs": 93, "stock_avant": 50, "stock_apres": 0},
                ],
                "config": {"takt": 0.65, "demande": 600}
            },
            "Production Lourde": {
                "etapes": [
                    {"nom": "OP10 - Fonderie", "tc": 4.0, "tcs": 2.0, "pers": 6, "trs": 75, "stock_avant": 0, "stock_apres": 500},
                    {"nom": "OP20 - Forge", "tc": 3.5, "tcs": 1.5, "pers": 5, "trs": 78, "stock_avant": 500, "stock_apres": 300},
                    {"nom": "OP30 - Traitement", "tc": 2.0, "tcs": 1.0, "pers": 3, "trs": 85, "stock_avant": 300, "stock_apres": 200},
                    {"nom": "OP40 - Finition", "tc": 1.5, "tcs": 0.5, "pers": 2, "trs": 88, "stock_avant": 200, "stock_apres": 0},
                ],
                "config": {"takt": 5.0, "demande": 100}
            }
        }

init_session()

st.markdown('''
<div class="main-header animate-in">
    <h1>VSM Builder Pro MAX</h1>
    <p>Cartographie Visuelle du Flux de Valeur | Lean Manufacturing Excellence</p>
</div>
''', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Configuration Generale")
    cfg = st.session_state.config
    st.markdown("#### Templates Predefinis")
    template_choice = st.selectbox("Charger un template", ["Personnalise"] + list(st.session_state.templates.keys()))
    if template_choice != "Personnalise" and st.button("Appliquer Template", use_container_width=True):
        template = st.session_state.templates[template_choice]
        st.session_state.etapes = [e.copy() for e in template["etapes"]]
        for k, v in template["config"].items():
            st.session_state.config[k] = v
        st.success(f"Template '{template_choice}' charge!")
        st.rerun()
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        cfg["takt"] = st.number_input("Takt Time (h)", 0.01, value=float(cfg["takt"]), step=0.1, key="takt")
    with col2:
        cfg["demande"] = st.number_input("Demande/jour", 1, value=int(cfg["demande"]), key="demande")
    st.divider()
    st.markdown("#### Fournisseur")
    cfg["fourn_nom"] = st.text_input("Nom", cfg["fourn_nom"], key="fourn_nom")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        cfg["fourn_freq"] = st.selectbox("Frequence", ["1/sem", "2/sem", "Quotidien"], index=["1/sem", "2/sem", "Quotidien"].index(cfg["fourn_freq"]), key="fourn_freq")
    with col_f2:
        modes = ["Routier", "Ferroviaire", "Aerien", "Maritime"]
        current_mode = cfg["fourn_mode"].replace("🚚 ", "").replace("🚂 ", "").replace("✈️ ", "").replace("🚢 ", "")
        if current_mode not in modes: current_mode = "Routier"
        cfg["fourn_mode"] = st.selectbox("Transport", modes, index=modes.index(current_mode), key="fourn_mode")
    st.divider()
    st.markdown("#### Entreprise")
    cfg["ent_nom"] = st.text_input("Nom", cfg["ent_nom"], key="ent_nom")
    cfg["ent_erp"] = st.text_input("ERP/Systeme", cfg["ent_erp"], key="ent_erp")
    st.divider()
    st.markdown("#### Client")
    cfg["cli_nom"] = st.text_input("Nom", cfg["cli_nom"], key="cli_nom")
    freqs = ["1/sem", "2/sem", "Quotidien", "Just-in-Time"]
    current_freq = cfg["cli_freq"] if cfg["cli_freq"] in freqs else "1/sem"
    cfg["cli_freq"] = st.selectbox("Livraison", freqs, index=freqs.index(current_freq), key="cli_freq")
    st.divider()
    st.markdown("#### Donnees")
    col_imp, col_exp = st.columns(2)
    with col_imp:
        uploaded = st.file_uploader("Importer", type="json", label_visibility="collapsed")
        if uploaded:
            data = json.load(uploaded)
            st.session_state.etapes = data.get("etapes", st.session_state.etapes)
            st.session_state.config.update(data.get("config", {}))
            st.success("Import reussi!")
            st.rerun()
    with col_exp:
        export_data = json.dumps({"etapes": st.session_state.etapes, "config": st.session_state.config, "export_date": datetime.now().isoformat()}, indent=2, ensure_ascii=False)
        st.download_button("Exporter", export_data, f"vsm_config_{datetime.now().strftime('%Y%m%d_%H%M')}.json", "application/json", use_container_width=True)

tab1, tab2, tab3, tab4 = st.tabs(["Edition", "VSM Visuel", "Analyse & KPIs", "Rapport"])

with tab1:
    st.markdown("### Edition des Processus")
    col_add, col_del, col_dup = st.columns([1, 1, 1])
    with col_add:
        if st.button("Ajouter Etape", type="primary", use_container_width=True):
            st.session_state.etapes.append({"nom": f"OP{(len(st.session_state.etapes)+1)*10}", "tc": 1.0, "tcs": 0.2, "pers": 1, "trs": 80, "stock_avant": 0, "stock_apres": 0})
            st.toast("Etape ajoutee!")
            st.rerun()
    with col_del:
        if st.button("Supprimer", use_container_width=True):
            if len(st.session_state.etapes) > 1:
                st.session_state.etapes.pop()
                st.toast("Etape supprimee")
                st.rerun()
            else:
                st.warning("Minimum 1 etape requise")
    with col_dup:
        if st.button("Dupliquer Derniere", use_container_width=True):
            if st.session_state.etapes:
                last = st.session_state.etapes[-1].copy()
                last["nom"] = f"OP{(len(st.session_state.etapes)+1)*10}"
                st.session_state.etapes.append(last)
                st.toast("Etape dupliquee!")
                st.rerun()
    st.divider()
    for i, etape in enumerate(st.session_state.etapes):
        with st.expander(f"{etape['nom']} | TC: {etape['tc']}h | TRS: {etape['trs']}% | Stock: {etape['stock_avant']}->{etape['stock_apres']}", expanded=(i == 0)):
            c1, c2, c3, c4 = st.columns(4)
            etape['nom'] = c1.text_input("Nom de l'etape", etape['nom'], key=f"n{i}")
            etape['tc'] = c2.number_input("C/T (h)", 0.0, value=float(etape['tc']), step=0.1, key=f"tc{i}")
            etape['tcs'] = c3.number_input("C/O (h)", 0.0, value=float(etape['tcs']), step=0.1, key=f"tcs{i}")
            etape['pers'] = c4.number_input("Operateurs", 1, value=int(etape['pers']), key=f"p{i}")
            c5, c6, c7 = st.columns(3)
            etape['trs'] = c5.slider("TRS %", 0, 100, value=int(etape['trs']), key=f"trs{i}")
            etape['stock_avant'] = c6.number_input("Stock Avant (pcs)", 0, value=int(etape['stock_avant']), key=f"sa{i}")
            etape['stock_apres'] = c7.number_input("Stock Apres (pcs)", 0, value=int(etape['stock_apres']), key=f"sp{i}")
            trs_color = "#10b981" if etape['trs'] >= 85 else "#f59e0b" if etape['trs'] >= 70 else "#f43f5e"
            fig_gauge = create_gauge_chart(etape['trs'], "TRS", 100, trs_color)
            st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{i}")

with tab2:
    st.markdown("### Cartographie VSM Interactive")
    cfg = st.session_state.config
    takt = cfg["takt"]
    demande = cfg["demande"]
    svg_content = create_vsm_svg(st.session_state.etapes, cfg)
    st.components.v1.html(f'<div style="background: linear-gradient(145deg, #0f172a, #1e293b); border-radius: 20px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 60px rgba(0,0,0,0.5); overflow-x: auto;">{svg_content}</div>', height=520)
    st.divider()
    st.markdown("### Timeline VA/NVA")
    df_timeline = pd.DataFrame(st.session_state.etapes)
    df_timeline['VA (h)'] = df_timeline['tc']
    demand_rate = demande / 24 if demande > 0 else 1
    df_timeline['NVA (h)'] = df_timeline['stock_avant'] / demand_rate
    fig_timeline = create_vsm_timeline(df_timeline, takt)
    st.plotly_chart(fig_timeline, use_container_width=True)
    st.markdown("### Detail par Etape")
    summary = df_timeline[['nom', 'tc', 'tcs', 'pers', 'trs', 'stock_avant', 'stock_apres']].copy()
    summary['Lead Time (h)'] = summary['tc'] + (summary['stock_avant'] / demand_rate)
    summary['% VA'] = (summary['tc'] / summary['Lead Time (h)'] * 100).round(1)
    summary.columns = ['Etape', 'C/T (h)', 'C/O (h)', 'Oper.', 'TRS %', 'Stock Av.', 'Stock Ap.', 'Lead Time', '% VA']
    st.dataframe(summary.style.background_gradient(subset=['TRS %', '% VA'], cmap='RdYlGn').format({'C/T (h)': '{:.2f}', 'C/O (h)': '{:.2f}', 'Lead Time': '{:.2f}', '% VA': '{:.1f}%'}), use_container_width=True, hide_index=True)

with tab3:
    st.markdown("### Analyse & KPIs Lean")
    df = pd.DataFrame(st.session_state.etapes)
    cfg = st.session_state.config
    takt = cfg["takt"]
    demande = cfg["demande"]
    total_va = df['tc'].sum()
    total_nva = (df['stock_avant'].sum() / (demande / 24)) if demande > 0 else 0
    lead_time = total_va + total_nva
    trs_moyen = df['trs'].mean()
    total_co = df['tcs'].sum()
    pct_va = (total_va/lead_time*100) if lead_time > 0 else 0
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{lead_time:.1f}h</div><div class="metric-label">Lead Time Total</div><div style="margin-top:10px; font-size:0.85rem; color:#94a3b8;">VA: {total_va:.1f}h | NVA: {total_nva:.1f}h</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{pct_va:.1f}%</div><div class="metric-label">% Valeur Ajoutee</div><div style="margin-top:10px;"><div style="background:#1e293b; border-radius:10px; height:8px; overflow:hidden;"><div style="background:linear-gradient(90deg, #10b981, #34d399); width:{min(pct_va, 100)}%; height:100%; border-radius:10px;"></div></div></div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{takt}h</div><div class="metric-label">Takt Time</div><div style="margin-top:10px; font-size:0.85rem; color:#94a3b8;">Demande: {demande}/jour</div></div>', unsafe_allow_html=True)
    with col4:
        trs_bar_color = '#10b981' if trs_moyen >= 85 else '#f59e0b' if trs_moyen >= 70 else '#f43f5e'
        st.markdown(f'<div class="metric-card"><div class="metric-value">{trs_moyen:.0f}%</div><div class="metric-label">TRS Moyen</div><div style="margin-top:10px;"><div style="background:#1e293b; border-radius:10px; height:8px; overflow:hidden;"><div style="background:{trs_bar_color}; width:{trs_moyen}%; height:100%; border-radius:10px;"></div></div></div></div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("### Analyse du Goulot")
    goulot = df.loc[df['tc'].idxmax()]
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if goulot['tc'] > takt:
            gap = goulot['tc'] - takt
            surplus_pct = (goulot['tc']/takt - 1) * 100
            goulot_msg = f"GOULOT CRITIQUE DETECTE - **{goulot['nom']}** - TC: {goulot['tc']}h > Takt: {takt}h - Ecart: +{gap:.1f}h ({surplus_pct:.0f}%)"
            st.error(goulot_msg)
        else:
            marge = ((takt - goulot['tc'])/takt*100)
            succes_msg = f"Capacite Suffisante - **{goulot['nom']}** - TC: {goulot['tc']}h < Takt: {takt}h - Marge: {marge:.0f}%"
            st.success(succes_msg)
    with col_b2:
        fig_cap = go.Figure()
        colors = ['#10b981' if tc <= takt else '#f43f5e' for tc in df['tc']]
        fig_cap.add_trace(go.Bar(x=df['nom'], y=df['tc'], marker_color=colors, text=df['tc'].round(2), textposition='outside', name='Temps Cycle'))
        fig_cap.add_hline(y=takt, line_dash="dash", line_color="#3b82f6", line_width=3, annotation_text=f"Takt Time = {takt}h")
        fig_cap.update_layout(title="Capacite vs Takt Time", yaxis_title="Temps (heures)", height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'}, xaxis=dict(gridcolor='rgba(255,255,255,0.1)'), yaxis=dict(gridcolor='rgba(255,255,255,0.1)'))
        st.plotly_chart(fig_cap, use_container_width=True)
    st.divider()
    st.markdown("### Plan d'Action Suggere")
    actions = []
    if goulot['tc'] > takt:
        gap = goulot['tc'] - takt
        ops_needed = goulot['tc'] / takt
        actions.append(f"EQUILIBRER LA LIGNE: Ajouter {ops_needed:.1f} operateurs a {goulot['nom']} ou reduire le TC de {gap:.1f}h")
    if total_nva > total_va:
        actions.append(f"REDUIRE LES STOCKS: {total_nva:.1f}h de NVA = {total_nva/lead_time*100:.0f}% du Lead Time. Objectif: NVA < VA")
    if trs_moyen < 85:
        actions.append(f"AMELIORER LE TRS: Moyenne {trs_moyen:.0f}% < 85%. Perte de capacite: {(85-trs_moyen)/85*100:.0f}%")
    if total_co > total_va * 0.2:
        actions.append(f"SMED / REDUIRE C/O: {total_co:.1f}h total de changements = {total_co/lead_time*100:.0f}% du LT")
    total_stock = df['stock_avant'].sum() + df['stock_apres'].sum()
    if total_stock > demande * 7:
        actions.append(f"EXCES DE STOCK: {total_stock} pcs > 7 jours de demande. Reduire WIP")
    if not actions:
        st.info("Excellent! Aucune action critique identifiee. Continuer le Kaizen!")
    else:
        for i, action in enumerate(actions, 1):
            st.markdown(f'<div style="background: linear-gradient(145deg, #1e293b, #0f172a); border-radius: 12px; padding: 1rem; margin-bottom: 0.5rem; border-left: 4px solid #3b82f6;"><strong>{i}.</strong> {action}</div>', unsafe_allow_html=True)
    st.markdown("### Performance par Etape")
    fig_perf = make_subplots(rows=1, cols=2, subplot_titles=('TRS par Etape', 'Temps de Changement Serie'), specs=[[{"type": "bar"}, {"type": "bar"}]])
    fig_perf.add_trace(go.Bar(x=df['nom'], y=df['trs'], marker_color=['#10b981' if t >= 85 else '#f59e0b' if t >= 70 else '#f43f5e' for t in df['trs']], text=df['trs'].astype(int), textposition='outside', name='TRS %'), row=1, col=1)
    fig_perf.add_trace(go.Bar(x=df['nom'], y=df['tcs'], marker_color='#8b5cf6', text=df['tcs'].round(2), textposition='outside', name='C/O (h)'), row=1, col=2)
    fig_perf.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#e2e8f0'}, showlegend=False)
    fig_perf.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
    fig_perf.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
    st.plotly_chart(fig_perf, use_container_width=True)

with tab4:
    st.markdown("### Rapport Complet VSM")
    report_date = datetime.now().strftime("%d/%m/%Y %H:%M")
    report_lines = []
    report_lines.append(f"# Rapport VSM - {cfg['ent_nom']}")
    report_lines.append(f"**Date:** {report_date}")
    report_lines.append("")
    report_lines.append("## Resume Executif")
    report_lines.append("")
    report_lines.append("| Indicateur | Valeur | Statut |")
    report_lines.append("|------------|--------|--------|")
    report_lines.append(f"| Lead Time Total | {lead_time:.1f}h | {'OK' if lead_time < 10 else 'A ameliorer'} |")
    report_lines.append(f"| % Valeur Ajoutee | {pct_va:.1f}% | {'Excellent' if pct_va > 50 else 'A ameliorer'} |")
    report_lines.append(f"| TRS Moyen | {trs_moyen:.0f}% | {'Objectif atteint' if trs_moyen >= 85 else 'Sous objectif'} |")
    report_lines.append(f"| Takt Time | {takt}h | - |")
    report_lines.append(f"| Demande | {demande}/jour | - |")
    report_lines.append("")
    report_lines.append("## Configuration")
    report_lines.append("")
    report_lines.append(f"**Fournisseur:** {cfg['fourn_nom']} ({cfg['fourn_freq']} - {cfg['fourn_mode']})")
    report_lines.append(f"**Entreprise:** {cfg['ent_nom']} (ERP: {cfg['ent_erp']})")
    report_lines.append(f"**Client:** {cfg['cli_nom']} ({cfg['cli_freq']})")
    report_lines.append("")
    report_lines.append("## Detail des Etapes")
    report_lines.append("")
    report_lines.append("| Etape | C/T (h) | C/O (h) | Oper. | TRS % | Stock Av. | Stock Ap. | Lead Time | % VA |")
    report_lines.append("|-------|---------|---------|-------|-------|-----------|-----------|-----------|------|")
    for _, row in summary.iterrows():
        report_lines.append(f"| {row['Etape']} | {row['C/T (h)']:.2f} | {row['C/O (h)']:.2f} | {int(row['Oper.'])} | {int(row['TRS %'])}% | {int(row['Stock Av.'])} | {int(row['Stock Ap.'])} | {row['Lead Time']:.2f}h | {row['% VA']:.1f}% |")
    report_lines.append("")
    report_lines.append("## Analyse du Goulot")
    report_lines.append("")
    report_lines.append(f"**Etape critique:** {goulot['nom']}")
    report_lines.append(f"**Temps Cycle:** {goulot['tc']}h")
    report_lines.append(f"**Takt Time:** {takt}h")
    report_lines.append(f"**Ecart:** {goulot['tc'] - takt:.1f}h")
    report_lines.append("")
    report_lines.append('La ligne peut suivre la demande' if goulot['tc'] <= takt else 'CAPACITE INSUFFISANTE')
    report_lines.append("")
    report_lines.append("## Plan d'Action")
    report_lines.append("")
    if actions:
        for i, action in enumerate(actions, 1):
            report_lines.append(f"{i}. {action}")
    else:
        report_lines.append("Aucune action critique identifiee. Continuer le Kaizen!")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("*Rapport genere automatiquement par VSM Builder Pro MAX*")
    report_lines.append("*Base sur les principes Lean et le livre 'Learning to See' de Rother & Shook*")
    report_md = "\n".join(report_lines)
    st.markdown(report_md)
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button("Telecharger en Markdown", report_md, f"VSM_Rapport_{cfg['ent_nom']}_{datetime.now().strftime('%Y%m%d')}.md", "text/markdown", use_container_width=True)
    with col_exp2:
        full_export = json.dumps({"metadata": {"app": "VSM Builder Pro MAX", "version": "3.0", "date": report_date}, "config": st.session_state.config, "etapes": st.session_state.etapes, "analyse": {"lead_time": lead_time, "pct_va": pct_va, "trs_moyen": trs_moyen, "goulot": goulot['nom'], "actions": actions}}, indent=2, ensure_ascii=False)
        st.download_button("Telecharger Donnees (JSON)", full_export, f"VSM_Data_{cfg['ent_nom']}_{datetime.now().strftime('%Y%m%d')}.json", "application/json", use_container_width=True)

st.divider()
st.markdown('<div style="text-align: center; padding: 1rem; color: #64748b; font-size: 0.9rem;"><p><strong>VSM Builder Pro MAX v3.0</strong> | Symboles Lean Standards | Base sur <em>Learning to See</em> - Rother & Shook</p><p style="font-size: 0.8rem; margin-top: 0.5rem;">Design Pro - Animations - Export JSON - Templates - Dashboard 7ya</p></div>', unsafe_allow_html=True)
