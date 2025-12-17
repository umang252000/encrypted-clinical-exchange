import React, { useEffect, useState } from "react";
import axios from "axios";

import Navbar from "../components/Navbar";
import Card from "../components/Card";
import Badge from "../components/Badge";

import SearchBox from "../components/SearchBox";
import ResultsTable from "../components/ResultsTable";
import DecryptPanel from "../components/DecryptPanel";

// ===============================
// CONFIG — Proxy URL
// ===============================
const PROXY_BASE =
  window.location.hostname.includes("github.dev")
    ? "https://fuzzy-adventure-5g77j7g7j5wrf4r75-8000.app.github.dev"
    : "http://localhost:8000";

// ===============================
// Crypto helpers (UNCHANGED)
// ===============================
async function importKeyFromRaw(rawKeyBytes) {
  return await window.crypto.subtle.importKey(
    "raw",
    rawKeyBytes,
    { name: "AES-GCM" },
    false,
    ["decrypt"]
  );
}

function hexToUint8(hex) {
  return new Uint8Array(hex.match(/.{1,2}/g).map((b) => parseInt(b, 16)));
}

async function decryptBlob(rawKeyBytes, nonceHex, ciphertextHex) {
  const key = await importKeyFromRaw(rawKeyBytes);
  const iv = hexToUint8(nonceHex);
  const ct = hexToUint8(ciphertextHex);

  const plain = await window.crypto.subtle.decrypt(
    { name: "AES-GCM", iv },
    key,
    ct
  );

  return JSON.parse(new TextDecoder().decode(plain));
}

// ===============================
// Decode JWT (UI only)
// ===============================
function parseJwtPayload(token) {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
  } catch {
    return null;
  }
}

// ===============================
// DASHBOARD
// ===============================
export default function Dashboard() {
  const token = localStorage.getItem("jwt");
  const userInfo = parseJwtPayload(token);

  const [blobs, setBlobs] = useState([]);
  const [results, setResults] = useState([]);
  const [keyFile, setKeyFile] = useState(null);
  const [decrypted, setDecrypted] = useState(null);

  // attach JWT automatically
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = "Bearer " + token;
    }
  }, [token]);

  // ===============================
  // LOAD BLOBS
  // ===============================
  async function loadBlobs() {
    const r = await axios.get(`${PROXY_BASE}/list_blobs`);
    setBlobs(r.data.blobs || []);
  }

  // ===============================
  // DECRYPT
  // ===============================
  async function handleDecrypt(filename) {
    if (!keyFile) {
      alert("Upload hospital AES key first");
      return;
    }

    const fr = new FileReader();
    fr.onload = async (e) => {
      const rawKey = new Uint8Array(e.target.result);
      const r = await axios.get(`${PROXY_BASE}/fetch_blob/${filename}`);
      const enc = r.data.enc_blob;

      const plain = await decryptBlob(
        rawKey.buffer,
        enc.nonce,
        enc.ciphertext
      );

      setDecrypted(plain);
    };

    fr.readAsArrayBuffer(keyFile);
  }

  // ===============================
  // LOGOUT
  // ===============================
  const logout = () => {
    localStorage.removeItem("jwt");
    window.location.reload();
  };

  // ===============================
  // UI
  // ===============================
  return (
    <>
      {/* TOP NAV */}
      <Navbar user={userInfo} onLogout={logout} />

      <div className="p-6 max-w-7xl mx-auto space-y-6">
        {/* STATUS CARDS */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card title="System Status">
            <div className="space-x-2">
              <Badge color="green">Encrypted</Badge>
              <Badge color="blue">RBAC Enabled</Badge>
              <Badge color="green">Audit Logging</Badge>
            </div>
          </Card>

          <Card title="User">
            <p className="text-sm">
              Logged in as <b>{userInfo?.sub}</b> ({userInfo?.role})
            </p>
          </Card>
        </div>

        {/* SEARCH */}
        <Card title="Encrypted Search (RBAC Protected)">
          <SearchBox onResults={setResults} />
          <ResultsTable results={results} />
        </Card>

        {/* DECRYPT */}
        <Card title="Local Decryption (Browser Only)">
          <input
            type="file"
            onChange={(e) => setKeyFile(e.target.files[0])}
            className="mb-3"
          />

          <button
            onClick={loadBlobs}
            className="px-4 py-2 bg-blue-600 text-white rounded"
          >
            List Encrypted Blobs
          </button>

          <ul className="mt-4 space-y-2 text-sm">
            {blobs.map((b) => (
              <li key={b} className="flex justify-between">
                <span>{b}</span>
                <button
                  className="text-blue-600 underline"
                  onClick={() => handleDecrypt(b)}
                >
                  Decrypt
                </button>
              </li>
            ))}
          </ul>

          <DecryptPanel decrypted={decrypted} />
        </Card>
      </div>
    </>
  );
}