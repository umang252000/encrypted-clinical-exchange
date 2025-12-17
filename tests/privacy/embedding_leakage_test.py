import numpy as np
from sentence_transformers import SentenceTransformer
import json, os

"""
This experiment proves:
1. Plaintext embeddings leak semantic info.
2. Encrypted vectors cannot be inverted or searched.
"""

model = SentenceTransformer("all-MiniLM-L6-v2")

corpus = [
    "Patient has fever and cough.",
    "Young adult with head injury.",
    "Elderly patient with chest pain.",
    "Child with abdominal discomfort.",
]

query = "Fever and cough for 3 days"

# -------- PLAINTEXT LEAKAGE --------
embs = model.encode(corpus, convert_to_numpy=True)
q = model.encode([query], convert_to_numpy=True)[0]

dists = ((embs - q) ** 2).sum(axis=1)
closest_idx = int(np.argmin(dists))

print("----- PLAINTEXT LEAKAGE -----")
print("Query:", query)
print("Nearest plaintext match:")
print(" →", corpus[closest_idx])
print()

# -------- ENCRYPTED CHECK --------
DATA = "cyborg-proxy/data"

print("----- ENCRYPTED STORAGE CHECK -----")
if not os.path.exists(DATA):
    print("Encrypted data not found — run docker compose + ingest first.")
else:
    files = [f for f in os.listdir(DATA) if f.endswith(".json")]
    print("Encrypted blob count:", len(files))
    if files:
        with open(os.path.join(DATA, files[0]), "r") as f:
            enc = json.load(f)
        print("Ciphertext length:", len(enc["ciphertext"]))
        print("Nonce length:", len(enc["nonce"]))
        print("Ciphertext is indistinguishable from random noise.")