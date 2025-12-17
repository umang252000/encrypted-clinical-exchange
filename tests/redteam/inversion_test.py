# naive embedding-based 'inversion' demo: find nearest corpus item for a query
from sentence_transformers import SentenceTransformer
import numpy as np

def main():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    corpus = [
        "Patient with fever and cough",
        "Elderly patient with chest pain",
        "Young adult with head injury",
        "Child with abdominal pain",
        "Middle-aged patient with stroke symptoms"
    ]
    embs = model.encode(corpus, convert_to_numpy=True)
    query_text = "Fever and cough for 3 days"
    q = model.encode([query_text], convert_to_numpy=True)[0]
    dists = ((embs - q)**2).sum(axis=1)
    idx = int(np.argmin(dists))
    print('Query:', query_text)
    print('Closest corpus item (naive inversion):', corpus[idx])

if __name__ == "__main__":
    main()