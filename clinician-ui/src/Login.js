import React, { useState, useEffect } from "react";

// ----------------------------------
// Helper: decode JWT payload (UI only)
// ----------------------------------
function parseJwtPayload(token) {
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}

export default function Login({ onToken }) {
  const [token, setToken] = useState("");
  const [decoded, setDecoded] = useState(null);
  const [message, setMessage] = useState("");

  // ----------------------------------
  // Load saved token on mount
  // ----------------------------------
  useEffect(() => {
    const saved = sessionStorage.getItem("jwt");
    if (saved) {
      setToken(saved);
      setDecoded(parseJwtPayload(saved));
    }
  }, []);

  // ----------------------------------
  // Decode JWT live
  // ----------------------------------
  useEffect(() => {
    setDecoded(parseJwtPayload(token));
  }, [token]);

  // ----------------------------------
  // Validation
  // ----------------------------------
  const isExpired =
    decoded?.exp && decoded.exp * 1000 < Date.now();

  const isValid =
    decoded && decoded.sub && decoded.role && !isExpired;

  // ----------------------------------
  // Actions
  // ----------------------------------
  function handleLogin() {
    if (!isValid) {
      setMessage("❌ Invalid or expired token");
      onToken("");
      return;
    }

    onToken(token);
    setMessage("✅ Logged in successfully");
  }

  function handleClear() {
    setToken("");
    setDecoded(null);
    onToken("");
    sessionStorage.removeItem("jwt");
    setMessage("🔄 Token cleared");
  }

  // ----------------------------------
  // UI
  // ----------------------------------
  return (
    <div
      style={{
        maxWidth: 520,
        padding: 20,
        borderRadius: 10,
        border: "1px solid #ddd",
        background: "#fff",
        marginBottom: 24,
      }}
    >
      <h3 style={{ marginBottom: 12 }}>
        🔐 Clinician Login
      </h3>

      <input
        style={{
          width: "100%",
          padding: "10px 12px",
          borderRadius: 6,
          border: "1px solid #ccc",
          marginBottom: 10,
        }}
        placeholder="Paste JWT token here"
        value={token}
        onChange={(e) => setToken(e.target.value)}
      />

      <div style={{ display: "flex", gap: 8 }}>
        <button
          onClick={handleLogin}
          disabled={!token}
          style={{
            padding: "8px 14px",
            borderRadius: 6,
            border: "none",
            background: "#2563eb",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Login
        </button>

        <button
          onClick={handleClear}
          style={{
            padding: "8px 14px",
            borderRadius: 6,
            border: "1px solid #ccc",
            background: "#f5f5f5",
            cursor: "pointer",
          }}
        >
          Clear
        </button>
      </div>

      {/* Status Message */}
      {message && (
        <div
          style={{
            marginTop: 10,
            color: isValid ? "green" : "#d93025",
          }}
        >
          {message}
        </div>
      )}

      {/* Decoded Token Info */}
      {decoded && (
        <div
          style={{
            marginTop: 14,
            padding: 10,
            background: "#f9fafb",
            borderRadius: 6,
            fontSize: 14,
          }}
        >
          <b>Decoded Token</b>
          <div>User: <b>{decoded.sub}</b></div>
          <div>Role: <b>{decoded.role}</b></div>
          {decoded.exp && (
            <div>
              Expires:{" "}
              <b style={{ color: isExpired ? "#d93025" : "green" }}>
                {new Date(decoded.exp * 1000).toLocaleString()}
              </b>
              {isExpired && " ⚠"}
            </div>
          )}
        </div>
      )}

      <div style={{ marginTop: 10, fontSize: 12, color: "#666" }}>
        Token is stored locally and never sent anywhere except secured API calls.
      </div>
    </div>
  );
}
