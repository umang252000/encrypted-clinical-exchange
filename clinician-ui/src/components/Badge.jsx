export default function Badge({ children, color = "gray" }) {
  const colors = {
    gray: "bg-slate-200 text-slate-700",
    green: "bg-green-100 text-green-700",
    blue: "bg-blue-100 text-blue-700",
    red: "bg-red-100 text-red-700",
  };

  return (
    <span className={`px-2 py-1 text-xs rounded ${colors[color]}`}>
      {children}
    </span>
  );
}