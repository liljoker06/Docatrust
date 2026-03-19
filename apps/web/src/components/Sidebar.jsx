import { Link, useLocation } from "react-router-dom";
import "../styles/sidebar.css";
import { clearAuthSession } from "../lib/auth";

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

function UploadIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 16V6"></path>
      <path d="M8 10l4-4 4 4"></path>
      <path d="M4 18h16"></path>
    </svg>
  );
}

function DocumentIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z"></path>
      <path d="M14 3v5h5"></path>
    </svg>
  );
}

function GenerationIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M12 2v4"></path>
      <path d="M12 18v4"></path>
      <path d="M4.93 4.93l2.83 2.83"></path>
      <path d="M16.24 16.24l2.83 2.83"></path>
      <path d="M2 12h4"></path>
      <path d="M18 12h4"></path>
      <path d="M4.93 19.07l2.83-2.83"></path>
      <path d="M16.24 7.76l2.83-2.83"></path>
    </svg>
  );
}

function OcrIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"></path>
      <path d="M3.27 6.96L12 12.01l8.73-5.05"></path>
      <path d="M12 22.08V12"></path>
    </svg>
  );
}

function LogoutIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"></path>
      <path d="M16 17l5-5-5-5"></path>
      <path d="M21 12H9"></path>
    </svg>
  );
}

export default function Sidebar() {
  const location = useLocation();

  const navItems = [
    { to: "/dashboard", label: "Dashboard", icon: <DashboardIcon /> },
    { to: "/upload", label: "Upload", icon: <UploadIcon /> },
    { to: "/documents", label: "Documents", icon: <DocumentIcon /> },
    { to: "/generation", label: "Génération", icon: <GenerationIcon /> },
    { to: "/ocr", label: "OCR", icon: <OcrIcon /> },
    { to: "/", label: "Logout", icon: <LogoutIcon /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <h2 className="sidebar-title">Menu</h2>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.to + item.label}
              to={item.to}
              onClick={() => {
                if (item.label === "Logout") {
                  clearAuthSession();
                }
              }}
              className={`sidebar-link ${location.pathname === item.to ? "active" : ""}`}
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </div>
    </aside>
  );
}