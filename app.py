import streamlit as st
import pandas as pd
import graphviz
import plotly.graph_objects as go
import json
from io import StringIO

st.set_page_config(page_title="VSM Builder Pro", layout="wide", page_icon="🏭")
st.title("🏭 VSM Builder Pro - Cartographie Visuelle")
st.caption("Créez votre Value Stream Mapping avec les symboles Lean standards")

# ─── Session State Init ─────────────────────────────────────────────
def init_state():
    if 'etapes' not in st.session_state:
        st.session_state.etapes = [
            {"nom": "OP10", "tc": 0.5, "tcs": 0.2, "pers": 2, "trs": 85, "stock_avant": 0, "stock_apres": 4600},
            {"nom": "OP20", "tc": 1.2, "tcs": 0.3, "pers": 3, "trs": 78, "stock_avant": 4600, "stock_apres": 1100},
            {"nom": "OP30", "tc": 0.8, "tcs": 0.1, "pers": 2, "trs": 90, "stock_avant": 1100, "stock_apres": 0},
        ]
    if 'config' not in st.session_state:
        st.session_state.config = {
            "takt": 1.0,
            "demande": 480,
            "fourn_nom": "Fournisseur A",
            "fourn_freq": "1/sem",
            "fourn_mode": "🚚 Routier",
            "ent_nom": "Mon Usine",
            "ent_erp": "SAP MRP",
            "cli_nom": "Client B",
            "cli_freq": "1/sem",
        }

init_state()

# ─── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Data persistence
    col_imp, col_exp = st.columns(2)
    with col_imp:
        uploaded = st.file_uploader("📁 Importer", type="json", label_visibility="collapsed")
        if uploaded:
            data = json.load(uploaded)
            st.session_state.etapes = data["etapes"]
            st.session_state.config.update(data["config"])
            st.rerun()
    
    with col_exp:
        export_data = json.dumps({
            "etapes": st.session_state.etapes,
            "config": st.session_state.config
        }, indent=2)
        st.download_button("💾 Exporter", export_data, "vsm_config.json", "application/json", use_container_width=True)
    
    st.divider()
    
    cfg = st.session_state.config
    cfg["takt"] = st.number_input("Takt Time (h)", 0.1, value=cfg["takt"], step=0.1, key="takt")
    cfg["demande"] = st.number_input("Demande / jour", 1, value=cfg["demande"], key="demande")
    
    st.divider()
    st.header("📦 Fournisseur")
    cfg["fourn_nom"] = st.text_input("Nom", cfg["fourn_nom"], key="fourn_nom")
    cfg["fourn_freq"] = st.selectbox("Fréquence", ["1/sem", "2/sem", "Quotidien"], index=["1/sem", "2/sem", "Quotidien"].index(cfg["fourn_freq"]), key="fourn_freq")
    cfg["fourn_mode"] = st.selectbox("Transport", ["🚚 Routier", "🚂 Ferroviaire", "✈️ Aérien"], index=["🚚 Routier", "🚂 Ferroviaire", "✈️ Aérien"].index(cfg["fourn_mode"]), key="fourn_mode")
    
    st.divider()
    st.header("🏢 Entreprise")
    cfg["ent_nom"] = st.text_input("Nom", cfg["ent_nom"], key="ent_nom")
    cfg["ent_erp"] = st.text_input("ERP", cfg["ent_erp"], key="ent_erp")
    
    st.divider()
    st.header("🎯 Client")
    cfg["cli_nom"] = st.text_input("Nom", cfg["cli_nom"], key="cli_nom")
    cfg["cli_freq"] = st.selectbox("Livraison", ["1/sem", "2/sem", "Quotidien"], index=["1/sem", "2/sem", "Quotidien"].index(cfg["cli_freq"]), key="cli_freq")

# ─── Tabs ───────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["✏️ Édition Étapes", "🎨 VSM Visuelle", "📊 Analyse"])

with tab1:
    st.subheader("Édition des Processus")
    
    col_add, col_del, _ = st.columns([1, 1, 3])
    with col_add:
        if st.button("➕ Ajouter Étape", type="primary", use_container_width=True):
            st.session_state.etapes.append({
                "nom": f"OP{(len(st.session_state.etapes)+1)*10}", 
                "tc": 1.0, "tcs": 0.2, "pers": 1, "trs": 80, 
                "stock_avant": 0, "stock_apres": 0
            })
            st.toast("Étape ajoutée !")
            st.rerun()
    with col_del:
        if st.button("➖ Supprimer Dernière", use_container_width=True):
            if len(st.session_state.etapes) > 1:
                st.session_state.etapes.pop()
                st.toast("Étape supprimée")
                st.rerun()
            else:
                st.warning("Impossible de supprimer la dernière étape")
    
    st.divider()
    
    # Safe editing with copy to avoid mid-loop mutation issues
    etapes_copy = [e.copy() for e in st.session_state.etapes]
    modified = False
    
    for i, etape in enumerate(etapes_copy):
        with st.expander(f"**{etape['nom']}** — TC: {etape['tc']}h | TRS: {etape['trs']}%", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            new_nom = c1.text_input("Nom", etape['nom'], key=f"n{i}")
            new_tc = c2.number_input("TC (h)", 0.0, value=etape['tc'], step=0.1, key=f"tc{i}")
            new_tcs = c3.number_input("T Chgt Série (h)", 0.0, value=etape['tcs'], step=0.1, key=f"tcs{i}")
            new_pers = c4.number_input("Opérateurs", 1, value=etape['pers'], key=f"p{i}")
            
            c5, c6, c7 = st.columns(3)
            new_trs = c5.number_input("TRS %", 0, 100, value=etape['trs'], key=f"trs{i}")
            new_sa = c6.number_input("Stock Avant (pcs)", 0, value=etape['stock_avant'], key=f"sa{i}")
            new_sp = c7.number_input("Stock Après (pcs)", 0, value=etape['stock_apres'], key=f"sp{i}")
            
            # Detect changes
            if (new_nom != etape['nom'] or new_tc != etape['tc'] or 
                new_tcs != etape['tcs'] or new_pers != etape['pers'] or
                new_trs != etape['trs'] or new_sa != etape['stock_avant'] or 
                new_sp != etape['stock_apres']):
                modified = True
                st.session_state.etapes[i] = {
                    "nom": new_nom, "tc": new_tc, "tcs": new_tcs,
                    "pers": new_pers, "trs": new_trs,
                    "stock_avant": new_sa, "stock_apres": new_sp
                }

with tab2:
    st.subheader("Cartographie VSM - Symboles Lean Standards")
    
    cfg = st.session_state.config
    takt = cfg["takt"]
    demande = cfg["demande"]
    
    dot = graphviz.Digraph(comment='VSM')
    dot.attr(rankdir='LR', splines='ortho', nodesep='1.0', ranksep='1.5')
    dot.attr('node', fontname='Helvetica', fontsize='10', shape='none')
    dot.attr('edge', fontname='Helvetica', fontsize='9')
    
    # ── Supplier ──
    dot.node('fournisseur', f'''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="2" BGCOLOR="#E3F2FD">
        <TR><TD CELLPADDING="6"><FONT POINT-SIZE="14">🏭</FONT></TD></TR>
        <TR><TD CELLPADDING="4"><B>{cfg['fourn_nom']}</B></TD></TR>
        <TR><TD CELLPADDING="2"><FONT COLOR="#555">{cfg['fourn_freq']} | {cfg['fourn_mode']}</FONT></TD></TR>
    </TABLE>>''')
    
    # ── Client ──
    dot.node('client', f'''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="2" BGCOLOR="#E8F5E9">
        <TR><TD CELLPADDING="6"><FONT POINT-SIZE="14">🎯</FONT></TD></TR>
        <TR><TD CELLPADDING="4"><B>{cfg['cli_nom']}</B></TD></TR>
        <TR><TD CELLPADDING="2"><FONT COLOR="#555">Takt: {takt}h | {demande}/j</FONT></TD></TR>
    </TABLE>>''')
    
    # ── ERP/Control Center (top) ──
    dot.node('erp', f'''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="2" BGCOLOR="#FFF9C4">
        <TR><TD CELLPADDING="6"><FONT POINT-SIZE="12">⚡</FONT></TD></TR>
        <TR><TD CELLPADDING="4"><B>{cfg['ent_nom']}</B></TD></TR>
        <TR><TD CELLPADDING="2"><FONT COLOR="#555">{cfg['ent_erp']}</FONT></TD></TR>
    </TABLE>>''')
    
    # ── Process Steps ──
    prev_node = 'fournisseur'
    for i, e in enumerate(st.session_state.etapes):
        node_id = f"op{i}"
        
        # Process box (standard VSM shape)
        dot.node(node_id, f'''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" BGCOLOR="#F5F5F5">
            <TR><TD COLSPAN="2" BGCOLOR="#424242" CELLPADDING="4"><FONT COLOR="white"><B>{e['nom']}</B></FONT></TD></TR>
            <TR><TD ALIGN="LEFT" CELLPADDING="3">C/T</TD><TD CELLPADDING="3">{e['tc']} h</TD></TR>
            <TR><TD ALIGN="LEFT" CELLPADDING="3">C/O</TD><TD CELLPADDING="3">{e['tcs']} h</TD></TR>
            <TR><TD ALIGN="LEFT" CELLPADDING="3">Opér.</TD><TD CELLPADDING="3">{e['pers']}</TD></TR>
            <TR><TD ALIGN="LEFT" CELLPADDING="3">TRS</TD><TD CELLPADDING="3">{e['trs']}%</TD></TR>
        </TABLE>>''')
        
        # Inventory triangle (before step)
        if e['stock_avant'] > 0:
            stock_id = f"stock{i}_avant"
            # Standard VSM inventory symbol: triangle
            dot.node(stock_id, f'''<<TABLE BORDER="0" CELLBORDER="0">
                <TR><TD><FONT POINT-SIZE="20" COLOR="#FF9800">◄</FONT></TD></TR>
                <TR><TD><B>I = {e['stock_avant']}</B></TD></TR>
            </TABLE>>''')
            dot.edge(prev_node, stock_id, style='dashed', arrowhead='none', minlen='2')
            dot.edge(stock_id, node_id, style='dashed', arrowhead='none')
        else:
            dot.edge(prev_node, node_id, style='dashed', arrowhead='none', minlen='2')
        
        prev_node = node_id
    
    # Final inventory + client link
    last_stock = st.session_state.etapes[-1]['stock_apres']
    if last_stock > 0:
        dot.node('stock_final', f'''<<TABLE BORDER="0" CELLBORDER="0">
            <TR><TD><FONT POINT-SIZE="20" COLOR="#FF9800">◄</FONT></TD></TR>
            <TR><TD><B>I = {last_stock}</B></TD></TR>
        </TABLE>>''')
        dot.edge(prev_node, 'stock_final', style='dashed', arrowhead='none', minlen='2')
        dot.edge('stock_final', 'client', style='dashed', arrowhead='normal')
    else:
        dot.edge(prev_node, 'client', style='dashed', arrowhead='normal', minlen='2')
    
    # ── Information Flow (electronic) ──
    dot.edge('client', 'erp', style='bold', color='#1976D2', 
             label='Commande\nélectronique', dir='back', arrowhead='none')
    dot.edge('erp', 'fournisseur', style='bold', color='#1976D2', 
             label='Ordre\nAchat', dir='back', arrowhead='none')
    for i in range(len(st.session_state.etapes)):
        dot.edge('erp', f'op{i}', style='bold', color='#1976D2', 
                 label='OF', dir='back', arrowhead='none')
    
    # ── Production Control (dashed box around ERP) ──
    with dot.subgraph(name='cluster_control') as c:
        c.attr(style='dashed', color='#FFC107', label='Contrôle Production')
        c.node('erp')
    
    st.graphviz_chart(dot, use_container_width=True)
    
    st.divider()
    st.subheader("Timeline Lead Time")
    
    # ── CORRECTED VA/NVA Calculation ──
    df_timeline = pd.DataFrame(st.session_state.etapes)
    df_timeline['VA (h)'] = df_timeline['tc']
    # NVA = waiting time = stock / demand_rate
    demand_rate = demande / 24 if demande > 0 else 1  # pieces per hour (assuming 24h day)
    df_timeline['NVA (h)'] = df_timeline['stock_avant'] / demand_rate
    
    fig = go.Figure()
    
    # VA as bottom layer
    fig.add_trace(go.Bar(
        x=df_timeline['nom'], 
        y=df_timeline['VA (h)'],
        name='VA - Temps Cycle',
        marker_color='#4CAF50',
        width=0.6
    ))
    
    # NVA stacked on top
    fig.add_trace(go.Bar(
        x=df_timeline['nom'], 
        y=df_timeline['NVA (h)'],
        name='NVA - Attente Stock',
        marker_color='#F44336',
        width=0.6
    ))
    
    fig.add_hline(y=takt, line_dash="dash", line_color="#2196F3", line_width=2,
                 annotation_text=f"Takt Time = {takt}h", annotation_position="top right")
    
    fig.update_layout(
        barmode='stack',
        height=450,
        title="VA vs NVA par Étape (Stacked)",
        xaxis_title="Étape de Processus",
        yaxis_title="Temps (heures)",
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    st.caption("Détail du Lead Time")
    summary_df = df_timeline[['nom', 'VA (h)', 'NVA (h)']].copy()
    summary_df['Lead Time (h)'] = summary_df['VA (h)'] + summary_df['NVA (h)']
    summary_df['% VA'] = (summary_df['VA (h)'] / summary_df['Lead Time (h)'] * 100).round(1)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Analyse & KPIs Lean")
    df = pd.DataFrame(st.session_state.etapes)
    cfg = st.session_state.config
    takt = cfg["takt"]
    demande = cfg["demande"]
    
    # Corrected calculations
    total_va = df['tc'].sum()
    total_nva = (df['stock_avant'].sum() / (demande / 24)) if demande > 0 else 0
    lead_time = total_va + total_nva
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lead Time Total", f"{lead_time:.1f}h", f"VA: {total_va:.1f}h | NVA: {total_nva:.1f}h")
    c2.metric("% Valeur Ajoutée", f"{total_va/lead_time*100:.1f}%" if lead_time > 0 else "0%")
    c3.metric("Takt Time", f"{takt}h")
    c4.metric("TRS Moyen", f"{df['trs'].mean():.0f}%")
    
    # Bottleneck analysis
    goulot = df.loc[df['tc'].idxmax()]
    col_b1, col_b2 = st.columns(2)
    
    with col_b1:
        if goulot['tc'] > takt:
            st.error(f"🚨 **GOULOT DÉTECTÉ**\n\n{goulot['nom']}: TC={goulot['tc']}h > Takt={takt}h\n\n**Capacité insuffisante de {(goulot['tc']/takt - 1)*100:.0f}%**")
        else:
            st.success(f"✅ **Capacité suffisante**\n\nÉtape critique: {goulot['nom']} ({goulot['tc']}h)\nMarge: {((takt - goulot['tc'])/takt*100):.0f}% sous le Takt")
    
    with col_b2:
        # Capacity chart
        fig_cap = go.Figure()
        fig_cap.add_trace(go.Bar(
            x=df['nom'], y=df['tc'],
            name='Temps Cycle', marker_color='#42A5F5'
        ))
        fig_cap.add_hline(y=takt, line_dash="dash", line_color="red", line_width=3,
                         annotation_text="Takt Time")
        fig_cap.update_layout(
            title="Capacité vs Takt Time",
            yaxis_title="Temps (h)",
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_cap, use_container_width=True)
    
    # Action plan
    st.subheader("💡 Plan d'Action Suggéré")
    actions = []
    
    if goulot['tc'] > takt:
        gap = goulot['tc'] - takt
        actions.append(f"1. **Équilibrer la ligne** : Ajouter {(goulot['tc']/takt):.1f} opérateurs à {goulot['nom']} ou réduire le TC de {gap:.1f}h")
    
    if total_nva > total_va:
        actions.append(f"2. **Réduire les stocks** : {total_nva:.1f}h de NVA représentent {total_nva/lead_time*100:.0f}% du Lead Time total")
    
    if df['trs'].mean() < 85:
        actions.append(f"3. **Améliorer le TRS** : Moyenne de {df['trs'].mean():.0f}% vs objectif 85%. Perte de capacité: {(85-df['trs'].mean())/85*100:.0f}%")
    
    if df['tcs'].sum() > total_va * 0.2:
        actions.append(f"4. **Réduire les changements série** : {df['tcs'].sum():.1f}h total ({df['tcs'].sum()/lead_time*100:.0f}% du LT)")
    
    if not actions:
        st.info("Aucune action critique identifiée. Continuer le Kaizen !")
    else:
        for action in actions:
            st.markdown(action)
    
    # Export analysis
    st.divider()
    analysis_text = f"""# Analyse VSM - {cfg['ent_nom']}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## KPIs
- Lead Time: {lead_time:.1f}h (VA: {total_va:.1f}h, NVA: {total_nva:.1f}h)
- % Valeur Ajoutée: {total_va/lead_time*100:.1f}%
- TRS Moyen: {df['trs'].mean():.0f}%
- Takt Time: {takt}h

## Actions recommandées
{chr(10).join(actions) if actions else "Aucune action critique"}
"""
    st.download_button("📄 Télécharger l'analyse", analysis_text, "vsm_analyse.md", "text/markdown")

st.divider()
st.caption("VSM Builder Pro v2.1 | Symboles Lean Standards | Basé sur *Learning to See* — Rother & Shook")
