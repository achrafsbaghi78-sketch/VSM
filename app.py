import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="VSM Logistique", layout="wide")
st.title("📊 VSM Builder - Cartographie Chaîne de Valeur")

# Sidebar: Config globale
with st.sidebar:
    st.header("⚙️ Paramètres Globaux")
    takt_time = st.number_input("Takt Time (h)", value=4.0)
    demande_client = st.number_input("Demande Client / semaine", value=100)
    st.divider()
    st.header("➕ Ajouter Étape")
    if st.button("Nouvelle Étape", type="primary"):
        st.session_state.n_steps += 1

# Init
if 'n_steps' not in st.session_state:
    st.session_state.n_steps = 3
if 'etapes' not in st.session_state:
    st.session_state.etapes = []

# Tabs
tab1, tab2, tab3 = st.tabs(["🏭 Saisie Processus", "📈 VSM Visuelle", "📊 Analyse"])

with tab1:
    st.subheader("Données Fournisseur / Client")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Nom Fournisseur", "Fournisseur A")
        st.selectbox("Fréquence Livraison", ["1/sem", "2/sem", "Quotidien"])
    with col2:
        st.text_input("Nom Entreprise", "Mon Usine")
    with col3:
        st.text_input("Nom Client", "Client B")
        st.number_input("Takt Time Client", value=takt_time)
    
    st.divider()
    st.subheader("Étapes de Production")
    
    etapes_data = []
    for i in range(st.session_state.n_steps):
        st.markdown(f"#### Étape {i+1}")
        cols = st.columns(6)
        with cols[0]:
            nom = st.text_input("Nom", f"Étape {i+1}", key=f"nom_{i}")
        with cols[1]:
            nb_pers = st.number_input("Nbr Personnes", 1, key=f"pers_{i}")
        with cols[2]:
            tc = st.number_input("Tps Cycle (h)", 0.0, key=f"tc_{i}")
        with cols[3]:
            tcs = st.number_input("Tps Chgt Série (h)", 0.0, key=f"tcs_{i}")
        with cols[4]:
            trs = st.number_input("TRS %", 0, 100, key=f"trs_{i}")
        with cols[5]:
            stock = st.number_input("Stock (pcs)", 0, key=f"stock_{i}")
        
        etapes_data.append({
            "Étape": nom, "Personnes": nb_pers, "TC": tc, 
            "TCS": tcs, "TRS": trs, "Stock": stock
        })
    
    st.session_state.etapes = etapes_data
    df = pd.DataFrame(etapes_data)
    
with tab2:
    st.subheader("Cartographie VSM")
    if st.session_state.etapes:
        # Timeline Lead Time vs VA
        fig = go.Figure()
        cum_time = 0
        for idx, row in df.iterrows():
            # VA = Tps Cycle, NVA = Stock converti en temps
            va = row["TC"]
            nva = row["Stock"] * takt_time / demande_client if demande_client > 0 else 0
            
            fig.add_trace(go.Bar(
                name=f"{row['Étape']} - VA", 
                x=[va], y=[row["Étape"]], 
                orientation='h', marker_color='green'
            ))
            fig.add_trace(go.Bar(
                name=f"{row['Étape']} - NVA", 
                x=[nva], y=[row["Étape"]], 
                orientation='h', marker_color='red'
            ))
        
        fig.update_layout(barmode='stack', height=400, 
                         title="Lead Time: VA vs NVA par Étape")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau résumé
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Ajoute des étapes f tab 'Saisie Processus'")

with tab3:
    st.subheader("Analyse Lean")
    if st.session_state.etapes:
        total_tc = df["TC"].sum()
        total_stock_time = (df["Stock"].sum() * takt_time / demande_client) if demande_client > 0 else 0
        lead_time = total_tc + total_stock_time
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Lead Time Total", f"{lead_time:.1f} h")
        col2.metric("Temps VA Total", f"{total_tc:.1f} h")
        col3.metric("% VA", f"{total_tc/lead_time*100:.1f}%" if lead_time > 0 else "0%")
        col4.metric("Takt Time", f"{takt_time} h")
        
        # Détection goulot
        goulot = df.loc[df["TC"].idxmax()]
        st.error(f"🚨 Goulot détecté: **{goulot['Étape']}** avec TC = {goulot['TC']}h > Takt Time")
