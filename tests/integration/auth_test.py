import requests
import os

PROXY = "http://localhost:8000"

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
CLINICIAN_TOKEN = os.getenv("CLINICIAN_TOKEN")
BAD_TOKEN = "bad.token.value"


def test_list_blobs_no_token():
    r = requests.get(f"{PROXY}/list_blobs")
    assert r.status_code == 401


def test_list_blobs_clinician_ok():
    r = requests.get(
        f"{PROXY}/list_blobs",
        headers={"Authorization": f"Bearer {CLINICIAN_TOKEN}"}
    )
    assert r.status_code == 200


def test_store_blob_clinician_forbidden():
    payload = {
        "hospital": "Test",
        "case_id": "x",
        "enc_blob": {"nonce": "00", "ciphertext": "00"}
    }
    r = requests.post(
        f"{PROXY}/store_blob",
        json=payload,
        headers={"Authorization": f"Bearer {CLINICIAN_TOKEN}"}
    )
    assert r.status_code == 403


def test_store_blob_admin_ok():
    payload = {
        "hospital": "Test",
        "case_id": "x",
        "enc_blob": {"nonce": "00", "ciphertext": "00"}
    }
    r = requests.post(
        f"{PROXY}/store_blob",
        json=payload,
        headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
    )
    assert r.status_code == 200