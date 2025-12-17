import { useState } from "react";
import { encryptedSearch } from "../api/search";

export default function SearchBox({ onResults }) {
  const [query, setQuery] = useState("");

  async function runSearch() {
    const results = await encryptedSearch(query);
    onResults(results);
  }

  return (
    <div>
      <input
        placeholder="Search clinical cases..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={runSearch}>Search (Encrypted)</button>
    </div>
  );
}