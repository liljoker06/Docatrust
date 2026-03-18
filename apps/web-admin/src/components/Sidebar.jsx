import { Link } from "react-router-dom";
import "../styles/sidebar.css";

/* ===== ICONS (same style as old sidebar) ===== */
function DashboardIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="3" y="3" width="8" height="8" rx="2"></rect>
      <rect x="13" y="3" width="8" height="5" rx="2"></rect>
      <rect x="13" y="10" width="8" height="11" rx="2"></rect>
      <rect x="3" y="13" width="8" height="8" rx="2"></rect>
    </svg>
  );
}

function SupplierIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M3 21h18"></path>
      <path d="M5 21V7l7-4 7 4v14"></path>
      <path d="M9 9h.01"></path>
      <path d="M9 13h.01"></path>
      <path d="M15 9h.01"></path>
      <path d="M15 13h.01"></path>
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 9v4"></path>
      <path d="M12 17h.01"></path>
      <path d="M10 2h4l8 14H2z"></path>
    </svg>
  );
}

function LogsIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 6h16"></path>
      <path d="M4 12h16"></path>
      <path d="M4 18h16"></path>
    </svg>
  );
}

function ValidationIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M20 6L9 17l-5-5"></path>
    </svg>
  );
}

/* ===== SIDEBAR ===== */
export default function Sidebar() {
  return (
    <div className="sidebar">
      <h3 className="sidebar-title">Admin Menu</h3>

      <div className="sidebar-link">
        <span className="sidebar-icon"><DashboardIcon /></span>
        <Link to="/">Dashboard</Link>
      </div>

      <div className="sidebar-link">
        <span className="sidebar-icon"><SupplierIcon /></span>
        <Link to="/suppliers">Suppliers</Link>
      </div>

      <div className="sidebar-link">
        <span className="sidebar-icon"><AlertIcon /></span>
        <Link to="/alerts">Alerts</Link>
      </div>

      <div className="sidebar-link">
        <span className="sidebar-icon"><LogsIcon /></span>
        <Link to="/logs">Logs</Link>
      </div>

      <div className="sidebar-link">
        <span className="sidebar-icon"><ValidationIcon /></span>
        <Link to="/validation">Validation</Link>
      </div>
    </div>
  );
}