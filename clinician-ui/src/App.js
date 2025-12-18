import React, { useState, useEffect } from "react";
import axios from "axios";

import Login from "./Login";
import SearchBox from "./components/SearchBox";
import ResultsTable from "./components/ResultsTable";
import DecryptPanel from "./components/DecryptPanel";

// ✅ NEW (added, not breaking anything)
import Dashboard from "./pages/Dashboard";

// ===============================
// CONFIG — Proxy URL
// ===============================
const PROXY_BASE =
  window.location.hostname.includes("github.dev")
    ? "https://fuzzy-adventure-5g77j7g7j5wrf4r75-8000.app.github.dev"
    : "http://localhost:8000";

// ===============================
//   Crypto Helpers (UNCHANGED)
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
// Masking logic
// ===============================
function maskMetadata(metadata) {
  const m = { ...metadata };
  if (m.age) m.age = "##";
  if (m.name) m.name = "REDACTED";
  return m;
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
// INTERNAL APP (UNCHANGED LOGIC)
// ===============================
function LegacyClinicianApp() {
  const [token, setToken] = useState("");
  const [userInfo, setUserInfo] = useState(null);

  const [blobs, setBlobs] = useState([]);
  const [keyFile, setKeyFile] = useState(null);
  const [results, setResults] = useState([]);
  const [decrypted, setDecrypted] = useState(null);

  function setAuthToken(t) {
    setToken(t);

    if (t) {
      axios.defaults.headers.common["Authorization"] = "Bearer " + t;
      sessionStorage.setItem("jwt", t);

      const payload = parseJwtPayload(t);
      setUserInfo(payload ? { sub: payload.sub, role: payload.role } : null);
    } else {
      delete axios.defaults.headers.common["Authorization"];
      sessionStorage.removeItem("jwt");
      setUserInfo(null);
    }
  }

  useEffect(() => {
    const saved = sessionStorage.getItem("jwt");
    if (saved) setAuthToken(saved);
  }, []);

  async function loadBlobs() {
    const r = await axios.get(`${PROXY_BASE}/list_blobs`);
    setBlobs(r.data.blobs || []);
  }

  async function handleDecrypt(filename) {
    if (!keyFile) return alert("Upload key file first");

    const fr = new FileReader();
    fr.onload = async (e) => {
      const rawKey = new Uint8Array(e.target.result);
      const r = await axios.get(`${PROXY_BASE}/fetch_blob/${filename}`);
      const enc = r.data.enc_blob;

      let plain = await decryptBlob(
        rawKey.buffer,
        enc.nonce,
        enc.ciphertext
      );

      if (plain.metadata) {
        plain.metadata = maskMetadata(plain.metadata);
      }

      setDecrypted(plain);
    };

    fr.readAsArrayBuffer(keyFile);
  }

  return (
    <div style={{ padding: 20 }}>
      <h2>Clinician UI — Secure Encrypted Federation</h2>

      <Login onToken={setAuthToken} />

      {userInfo ? (
        <div style={{ marginBottom: 12 }}>
          Logged in as <b>{userInfo.sub}</b> ({userInfo.role})
          <button style={{ marginLeft: 10 }} onClick={() => setAuthToken("")}>
            Logout
          </button>
        </div>
      ) : (
        <div style={{ color: "#777" }}>Not logged in</div>
      )}

      <hr />

      <h3>Encrypted Search</h3>
      <SearchBox onResults={setResults} />
      <ResultsTable results={results} />

      <hr />

      <h3>Local Decryption</h3>
      <input type="file" onChange={(e) => setKeyFile(e.target.files[0])} />
      <button onClick={loadBlobs}>List Blobs</button>

      <ul>
        {blobs.map((b) => (
          <li key={b}>
            {b}
            <button onClick={() => handleDecrypt(b)}>Decrypt</button>
          </li>
        ))}
      </ul>

      <DecryptPanel decrypted={decrypted} />
    </div>
  );
}

// ===============================
// ✅ FINAL APP (WITH NEW RETURN CODE)
// ===============================
export default function App() {
  const token = localStorage.getItem("jwt");

  // Logic to handle the token from the Login component
  const applyToken = (newToken) => {
    if (newToken) {
      localStorage.setItem("jwt", newToken);
      window.location.reload();
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f1f5f9",
        display: "flex",
        alignItems: token ? "flex-start" : "center",
        justifyContent: token ? "flex-start" : "center",
        padding: token ? 24 : 0,
      }}
    >
      {/* ================= LOGIN STATE ================= */}
      {!token && (
        <div
          style={{
            background: "#fff",
            padding: 32,
            borderRadius: 10,
            boxShadow: "0 10px 30px rgba(0,0,0,0.12)",
            width: 600,
          }}
        >
          <h2 style={{ marginBottom: 20, textAlign: "center" }}>
            🔐 Clinician Login
          </h2>

          <Login onToken={applyToken} />

          <div
            style={{
              marginTop: 16,
              color: "#666",
              textAlign: "center",
              fontSize: 14,
            }}
          >
            Paste a valid JWT to access the encrypted clinical federation
          </div>
        </div>
      )}

      {/* ================= DASHBOARD STATE ================= */}
      {token && (
        <div style={{ width: "100%" }}>
          <Dashboard />
        </div>
      )}
    </div>
  );
}