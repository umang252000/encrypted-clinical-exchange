# Threat model (summary)

- Goal: ensure no plaintext PHI leaves hospital premises (clients).
- Assumptions: hospitals generate embeddings locally, encrypt vectors with local symmetric key before sending.
- Server (Cyborg Proxy) is untrusted — stores only ciphertext.
- Adversary types:
  - Passive server attacker: can read stored ciphertexts but cannot decrypt without key.
  - Active network attacker: TLS should be used in production for transport confidentiality (not implemented in dev stub).
  - Insider attacker at hospital: must protect local keys (rotate, HSM recommended).

# Red-team test
- `tests/redteam/inversion_test.py` demonstrates how plaintext embeddings can be used to find semantically similar texts.
- In our encrypted flow, the server cannot run inversion because it never sees vectors.