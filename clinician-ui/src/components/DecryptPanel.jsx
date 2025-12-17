import React from "react";

export default function DecryptPanel({ decrypted }) {
  if (!decrypted) return null;

  return (
    <div
      style={{
        marginTop: 20,
        padding: 16,
        background: "#f5f5f5",
        borderRadius: 8,
        maxWidth: 700
      }}
    >
      <h3 style={{ marginBottom: 10 }}>🔓 Decrypted Case (Local Only)</h3>

      <pre
        style={{
          background: "#fff",
          padding: 12,
          borderRadius: 6,
          overflowX: "auto"
        }}
      >
        {JSON.stringify(decrypted, null, 2)}
      </pre>

      <div style={{ marginTop: 8, fontSize: 12, color: "#555" }}>
        ⚠ Data decrypted locally in browser — never sent to server
      </div>
    </div>
  );
}