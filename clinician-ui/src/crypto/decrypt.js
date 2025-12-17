// AES-GCM helpers (browser crypto)

function hexToUint8(hex) {
  return new Uint8Array(hex.match(/.{1,2}/g).map(b => parseInt(b, 16)));
}

async function importKeyFromRaw(rawKeyBytes) {
  return await window.crypto.subtle.importKey(
    "raw",
    rawKeyBytes,
    { name: "AES-GCM" },
    false,
    ["decrypt"]
  );
}

export async function decryptBlob(rawKeyBytes, encBlob) {
  const key = await importKeyFromRaw(rawKeyBytes);
  const iv = hexToUint8(encBlob.nonce);
  const ciphertext = hexToUint8(encBlob.ciphertext);

  const plaintext = await window.crypto.subtle.decrypt(
    { name: "AES-GCM", iv },
    key,
    ciphertext
  );

  const decoded = new TextDecoder().decode(plaintext);
  return JSON.parse(decoded);
}