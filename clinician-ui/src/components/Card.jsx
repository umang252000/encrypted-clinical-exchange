export default function Card({ title, children }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
      {title && (
        <h2 className="text-lg font-semibold mb-3">{title}</h2>
      )}
      {children}
    </div>
  );
}