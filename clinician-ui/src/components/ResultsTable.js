export default function ResultsTable({ results }) {
  return (
    <table border="1" cellPadding="5">
      <thead>
        <tr>
          <th>Case ID</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        {results.map((r, i) => (
          <tr key={i}>
            <td>{r.id}</td>
            <td>{r.score.toFixed(3)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}