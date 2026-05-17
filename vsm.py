from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class VSM:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = None
        self.doc_names = []

    def fit(self, documents, doc_names):
        self.doc_names = doc_names
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

    def query(self, query_text, top_k=5):
        query_vec = self.vectorizer.transform([query_text])
        cos_sim = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        results = pd.DataFrame({
            'Document': self.doc_names,
            'Score': cos_sim
        }).sort_values('Score', ascending=False).head(top_k)
        return results
