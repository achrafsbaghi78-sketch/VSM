import streamlit as st
from vsm import VSM
from utils import preprocess_text
import PyPDF2

st.set_page_config(page_title="VSM AI App", layout="wide")
st.title("🔍 VSM Search Engine b AI")

if 'vsm' not in st.session_state:
    st.session_state.vsm = VSM()
    st.session_state.docs_raw = {}

uploaded_files = st.file_uploader("Upload documents TXT/PDF", accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        if file.name not in st.session_state.docs_raw:
            if file.name.endswith('.pdf'):
                pdf = PyPDF2.PdfReader(file)
                text = ' '.join([page.extract_text() for page in pdf.pages])
            else:
                text = file.read().decode('utf-8')
            st.session_state.docs_raw[file.name] = text

    docs_processed = [preprocess_text(doc) for doc in st.session_state.docs_raw.values()]
    st.session_state.vsm.fit(docs_processed, list(st.session_state.docs_raw.keys()))
    st.success(f"{len(docs_processed)} documents indexed!")

query = st.text_input("Dakhel query dyalk:")
top_k = st.slider("Top K results", 1, 10, 3)

if st.button("Search") and query:
    query_processed = preprocess_text(query)
    results = st.session_state.vsm.query(query_processed, top_k)
    st.subheader("Results:")
    st.dataframe(results, use_container_width=True)

    with st.expander("Chouf document lawel"):
        top_doc = results.iloc[0]['Document']
        st.write(st.session_state.docs_raw[top_doc][:1000] + "...")
