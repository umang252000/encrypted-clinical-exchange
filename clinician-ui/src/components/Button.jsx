export default function Button({ children, variant = "primary", ...props }) {
  const base =
    "px-4 py-2 rounded-md font-medium transition focus:outline-none focus:ring";

  const variants = {
    primary:
      "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-300",
    secondary:
      "bg-slate-200 text-slate-800 hover:bg-slate-300 focus:ring-slate-300",
    danger:
      "bg-red-600 text-white hover:bg-red-700 focus:ring-red-300",
  };

  return (
    <button className={`${base} ${variants[variant]}`} {...props}>
      {children}
    </button>
  );
}