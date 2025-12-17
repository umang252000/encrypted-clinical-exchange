import Button from "./Button";

export default function Navbar({ user, onLogout }) {
  return (
    <div className="bg-white border-b px-6 py-3 flex justify-between items-center">
      <div className="font-semibold text-lg">
        🏥 Encrypted Clinical Exchange
      </div>

      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-600">
          {user.sub} ({user.role})
        </span>
        <Button variant="secondary" onClick={onLogout}>
          Logout
        </Button>
      </div>
    </div>
  );
}