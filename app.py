import streamlit as st
from vsm import VSM
from utils import preprocess_text
import PyPDF2

st.set_page_config(page_title="VSM Search Engine b AI", layout="wide")
st.title("🔍 VSM Search Engine b AI")

# Init session state
if 'vsm' not in st.session_state:
    st.session_state.vsm = VSM()
    st.session_state.docs_raw = {}
    st.session_state.vsm_fitted = False

# Upload
uploaded_files = st.file_uploader("Upload documents TXT/PDF", accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.docs_raw:
            if file.name.endswith('.pdf'):
                pdf = PyPDF2.PdfReader(file)
                text = ' '.join([p.extract_text() for p in pdf.pages if p.extract_text()])
            else:
                text = file.read().decode('utf-8')
            st.session_state.docs_raw[file.name] = text
    
    # Fit VSM ghir ila kaynin docs
    if st.session_state.docs_raw:
        docs_processed = [preprocess_text(doc) for doc in st.session_state.docs_raw.values()]
        st.session_state.vsm.fit(docs_processed, list(st.session_state.docs_raw.keys()))
        st.session_state.vsm_fitted = True
        st.success(f"✅ {len(docs_processed)} documents indexed!")

# Search section
query = st.text_input("Dakhel query dyalk:")
top_k = st.slider("Top K results", 1, 10, 3)

if st.button("Search"):
    if not st.session_state.vsm_fitted:
        st.error("⚠️ Upload chi documents lawel 3ad dir search")
    elif not query:
        st.warning("Dakhel query 3ad")
    else:
        query_processed = preprocess_text(query)
        results = st.session_state.vsm.query(query_processed, top_k)
        st.subheader("Results:")
        st.dataframe(results, use_container_width=True)
