import streamlit as st
import pandas as pd
import graphviz
import plotly.graph_objects as go

st.set_page_config(page_title="VSM Builder Pro", layout="wide", page_icon="🏭")
st.title("🏭 VSM Builder Pro - Cartographie Visuelle")
st.caption("Créez votre Value Stream Mapping avec les symboles Lean standards")

# Init
if 'etapes' not in st.session_state:
    st.session_state.etapes = [
        {"nom": "OP10", "tc": 0.5, "tcs": 0.2, "pers": 2, "trs": 85, "stock_avant": 0, "stock_apres": 4600},
        {"nom": "OP20", "tc": 1.2, "tcs": 0.3, "pers": 3, "trs": 78, "stock_avant": 4600, "stock_apres": 1100},
        {"nom": "OP30", "tc": 0.8, "tcs": 0.1, "pers": 2, "trs": 90, "stock_avant": 1100, "stock_apres": 0},
    ]

# Sidebar - Paramètres
with st.sidebar:
    st.header("⚙️ Configuration")
    takt = st.number_input("Takt Time (h)", 0.1, value=1.0, step=0.1)
    demande = st.number_input("Demande / jour", 1, value=480)
    
    st.divider()
    st.header("📦 Fournisseur")
    four_nom = st.text_input("Nom", "Fournisseur A")
    four_freq = st.selectbox("Fréquence", ["1/sem", "2/sem", "Quotidien"])
    four_mode = st.selectbox("Transport", ["🚚 Routier", "🚂 Ferroviaire", "✈️ Aérien"])
    
    st.divider()
    st.header("🏢 Entreprise")
    ent_nom = st.text_input("Nom", "Mon Usine")
    ent_erp = st.text_input("ERP", "SAP MRP")
    
    st.divider()
    st.header("🎯 Client")
    cli_nom = st.text_input("Nom", "Client B")
    cli_freq = st.selectbox("Livraison", ["1/sem", "2/sem", "Quotidien"], key="cli")

# Tabs
tab1, tab2, tab3 = st.tabs(["✏️ Édition Étapes", "🎨 VSM Visuelle", "📊 Analyse"])

with tab1:
    st.subheader("Édition des Processus")
    
    col_add, col_del = st.columns(2)
    with col_add:
        if st.button("➕ Ajouter Étape", type="primary", use_container_width=True):
            st.session_state.etapes.append({
                "nom": f"OP{len(st.session_state.etapes)*10+10}", 
                "tc": 1.0, "tcs": 0.2, "pers": 1, "trs": 80, 
                "stock_avant": 0, "stock_apres": 0
            })
            st.rerun()
    with col_del:
        if st.button("➖ Supprimer Dernière", use_container_width=True):
            if len(st.session_state.etapes) > 1:
                st.session_state.etapes.pop()
                st.rerun()
    
    st.divider()
    
    for i, etape in enumerate(st.session_state.etapes):
        with st.expander(f"**{etape['nom']}**", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            etape['nom'] = c1.text_input("Nom", etape['nom'], key=f"n{i}")
            etape['tc'] = c2.number_input("TC (h)", 0.0, value=etape['tc'], key=f"tc{i}")
            etape['tcs'] = c3.number_input("T Chgt Série (h)", 0.0, value=etape['tcs'], key=f"tcs{i}")
            etape['pers'] = c4.number_input("Opérateurs", 1, value=etape['pers'], key=f"p{i}")
            
            c5, c6, c7 = st.columns(3)
            etape['trs'] = c5.number_input("TRS %", 0, 100, value=etape['trs'], key=f"trs{i}")
            etape['stock_avant'] = c6.number_input("Stock Avant (pcs)", 0, value=etape['stock_avant'], key=f"sa{i}")
            etape['stock_apres'] = c7.number_input("Stock Après (pcs)", 0, value=etape['stock_apres'], key=f"sp{i}")

with tab2:
    st.subheader("Cartographie VSM - Symboles Lean Standards")
    
    # Création du graph VSM avec Graphviz
    dot = graphviz.Digraph(comment='VSM')
    dot.attr(rankdir='LR', splines='ortho', nodesep='0.8')
    dot.attr('node', fontname='Helvetica', fontsize='10')
    
    # 1. Fournisseur - Icône usine
    dot.node('fournisseur', f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
        <TR><TD><IMG SRC=""/></TD></TR>
        <TR><TD BGCOLOR="lightblue"><B>{four_nom}</B></TD></TR>
        <TR><TD>{four_freq}</TD></TR>
        <TR><TD>{four_mode}</TD></TR>
    </TABLE>>''', shape='none')
    
    # 2. Client - Icône usine
    dot.node('client', f'''<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">
        <TR><TD BGCOLOR="lightgreen"><B>{cli_nom}</B></TD></TR>
        <TR><TD>Takt: {takt}h</TD></TR>
        <TR><TD>Demande: {demande}/j</TD></TR>
    </TABLE>>''', shape='none')
    
    # 3. Entreprise/ERP - Rectangle
    dot.node('erp', f'''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" BGCOLOR="yellow">
        <TR><TD><B>{ent_nom}</B></TD></TR>
        <TR><TD>{ent_erp}</TD></TR>
        <TR><TD>Commande H/J/M</TD></TR>
    </TABLE>>''')
    
    # 4. Étapes de processus
    prev_node = 'fournisseur'
    for i, e in enumerate(st.session_state.etapes):
        # Data box pour l'étape
        node_id = f"op{i}"
        dot.node(node_id, f'''<<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0">
            <TR><TD COLSPAN="2" BGCOLOR="lightgray"><B>{e['nom']}</B></TD></TR>
            <TR><TD ALIGN="LEFT">TC</TD><TD>{e['tc']} h</TD></TR>
            <TR><TD ALIGN="LEFT">T Chgt</TD><TD>{e['tcs']} h</TD></TR>
            <TR><TD ALIGN="LEFT">Opér.</TD><TD>{e['pers']}</TD></TR>
            <TR><TD ALIGN="LEFT">TRS</TD><TD>{e['trs']}%</TD></TR>
        </TABLE>>''', shape='none')
        
        # Stock avant = Triangle I
        if e['stock_avant'] > 0:
            stock_id = f"stock{i}_avant"
            dot.node(stock_id, f'''<<TABLE BORDER="0">
                <TR><TD>▲</TD></TR>
                <TR><TD>I</TD></TR>
                <TR><TD><B>{e['stock_avant']} pcs</B></TD></TR>
            </TABLE>>''', shape='none')
            dot.edge(prev_node, stock_id, style='dashed', label='Flux Poussé')
            dot.edge(stock_id, node_id, style='dashed')
        else:
            dot.edge(prev_node, node_id, style='dashed', label='Flux Poussé')
        
        prev_node = node_id
    
    # Lien vers client
    if st.session_state.etapes[-1]['stock_apres'] > 0:
        dot.node('stock_final', f'''<<TABLE BORDER="0">
            <TR><TD>▲</TD></TR>
            <TR><TD>I</TD></TR>
            <TR><TD><B>{st.session_state.etapes[-1]['stock_apres']} pcs</B></TD></TR>
        </TABLE>>''', shape='none')
        dot.edge(prev_node, 'stock_final', style='dashed')
        dot.edge('stock_final', 'client', style='dashed', label='Expédition')
    else:
        dot.edge(prev_node, 'client', style='dashed', label='Expédition')
    
    # Flux d'information électronique - lignes éclairs
    dot.edge('client', 'erp', style='bold', color='blue', 
             label='Commande', decorate='true')
    dot.edge('erp', 'fournisseur', style='bold', color='blue', 
             label='Ordre Achat', decorate='true')
    for i in range(len(st.session_state.etapes)):
        dot.edge('erp', f'op{i}', style='bold', color='blue', 
                 label='OF', decorate='true')
    
    st.graphviz_chart(dot, use_container_width=True)
    
    st.divider()
    st.subheader("Timeline Lead Time")
    
    # Calcul VA/NVA
    df_timeline = pd.DataFrame(st.session_state.etapes)
    df_timeline['VA (h)'] = df_timeline['tc']
    df_timeline['NVA (h)'] = df_timeline['stock_apres'] * takt / demande if demande > 0 else 0
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_timeline['nom'], 
        y=df_timeline['VA (h)'],
        mode='lines+markers',
        name='VA - Temps Cycle',
        line=dict(color='green', width=4),
        fill='tozeroy'
    ))
    fig.add_trace(go.Scatter(
        x=df_timeline['nom'], 
        y=df_timeline['NVA (h)'],
        mode='lines+markers',
        name='NVA - Attente Stock',
        line=dict(color='red', width=4),
        fill='tonexty'
    ))
    fig.add_hline(y=takt, line_dash="dash", line_color="blue",
                 annotation_text=f"Takt Time = {takt}h")
    fig.update_layout(height=400, title="VA vs NVA par Étape", hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Analyse & KPIs Lean")
    df = pd.DataFrame(st.session_state.etapes)
    
    total_va = df['tc'].sum()
    total_nva = df['stock_apres'].sum() * takt / demande if demande > 0 else 0
    lead_time = total_va + total_nva
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lead Time", f"{lead_time:.1f}h", f"VA: {total_va:.1f}h")
    c2.metric("% Valeur Ajoutée", f"{total_va/lead_time*100:.1f}%" if lead_time > 0 else "0%")
    c3.metric("Takt Time", f"{takt}h")
    c4.metric("TRS Moyen", f"{df['trs'].mean():.0f}%")
    
    # Goulot
    goulot = df.loc[df['tc'].idxmax()]
    if goulot['tc'] > takt:
        st.error(f"🚨 **GOULOT**: {goulot['nom']} avec TC={goulot['tc']}h > Takt {takt}h. Impossible de suivre la demande!")
    else:
        st.success(f"✅ Pas de goulot majeur. Étape critique: {goulot['nom']} ({goulot['tc']}h)")
    
    # Plan d'action
    st.subheader("💡 Plan d'Action Suggéré")
    if goulot['tc'] > takt:
        st.markdown(f"1. **Équilibrer ligne**: Ajouter ressource à {goulot['nom']} ou réduire TC de {goulot['tc']-takt:.1f}h")
    if total_nva > total_va:
        st.markdown(f"2. **Réduire stocks**: {total_nva:.1f}h de NVA = {total_nva/lead_time*100:.0f}% du Lead Time")
    if df['trs'].mean() < 85:
        st.markdown(f"3. **Améliorer TRS**: TRS moyen {df['trs'].mean():.0f}% < 85% objectif")

st.divider()
st.caption("VSM Builder Pro v2.0 | Symboles Lean Standards | Basé sur Learning to See")
