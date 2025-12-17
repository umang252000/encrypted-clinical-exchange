import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_key(path):
    key = AESGCM.generate_key(bit_length=256)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(key)
    os.chmod(path, 0o600)
    print("Wrote key:", path)

if __name__ == "__main__":
    generate_key("hospital-agent/hospital_a/keys/hospital_a.key")
    generate_key("hospital-agent/hospital_b/keys/hospital_b.key")