import api from "./client";

export async function encryptedSearch(query, k = 5) {
  const res = await api.post("/search", { query, k });
  return res.data.results;
}