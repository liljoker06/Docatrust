import { useNavigate } from "react-router-dom";
import { api } from "../services/api";

export default function Navbar({ title = "Dashboard" }) {
  const navigate = useNavigate();

  function handleLogout() {
    api.removeToken();
    navigate("/login");
  }

  return (
    <div className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0">
      <h1 className="text-base font-semibold text-slate-800">{title}</h1>

      <div className="flex items-center gap-3">
        <span className="text-xs text-slate-400 bg-slate-100 px-2.5 py-1 rounded-full font-medium">
          ADMIN
        </span>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-red-500 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Déconnexion
        </button>
      </div>
    </div>
  );
}
