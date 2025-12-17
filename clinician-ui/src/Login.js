import React, { useState, useEffect } from "react";

// ----------------------------------
// Helper: decode JWT payload (DEV)
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
  // Decode JWT live when typing
  // ----------------------------------
  useEffect(() => {
    setDecoded(parseJwtPayload(token));
  }, [token]);

  // ----------------------------------
  // Helpers
  // ----------------------------------
  const isExpired =
    decoded?.exp && decoded.exp * 1000 < Date.now();

  const isValid =
    decoded && decoded.sub && decoded.role && !isExpired;

  // ----------------------------------
  // Actions
  // ----------------------------------
  function handleSetToken() {
    if (!isValid) {
      setMessage("❌ Invalid or expired token");
      onToken("");
      return;
    }

    onToken(token);
    setMessage("✅ Token applied successfully");
  }

  function handleClear() {
    setToken("");
    setDecoded(null);
    onToken("");
    setMessage("🔄 Token cleared");
  }

  // ----------------------------------
  // UI
  // ----------------------------------
  return (
    <div style={{ marginBottom: 14 }}>
      <input
        style={{ width: 520 }}
        placeholder="Paste JWT token here (dev)"
        value={token}
        onChange={(e) => setToken(e.target.value)}
      />

      <button
        style={{ marginLeft: 8 }}
        onClick={handleSetToken}
        disabled={!token}
      >
        Set Token
      </button>

      <button style={{ marginLeft: 8 }} onClick={handleClear}>
        Clear
      </button>

      {/* Status Message */}
      {message && (
        <div style={{ marginTop: 8, color: isValid ? "green" : "#d93025" }}>
          {message}
        </div>
      )}

      {/* Decoded Token Info */}
      {decoded && (
        <div
          style={{
            marginTop: 10,
            padding: 8,
            background: "#f5f5f5",
            borderRadius: 6,
            width: 520,
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
    </div>
  );
}