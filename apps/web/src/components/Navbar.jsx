import "../styles/navbar.css";
import { useState } from "react";

function BellIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M18 8a6 6 0 10-12 0c0 7-3 7-3 7h18s-3 0-3-7"></path>
      <path d="M13.73 21a2 2 0 01-3.46 0"></path>
    </svg>
  );
}

function MenuIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M3 6h18M3 12h18M3 18h18"></path>
    </svg>
  );
}

export default function Navbar() {
  const [search, setSearch] = useState("");

  return (
    <header className="navbar">
      {/* LEFT */}
      <div className="navbar-left">
        <button className="menu-btn">
          <MenuIcon />
        </button>

        <h2 className="navbar-title">Dashboard</h2>
      </div>

      {/* RIGHT */}
      <div className="navbar-right">
        {/* SEARCH */}
        <div className="navbar-search">
          <input
            type="text"
            placeholder="Search documents..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* NOTIFICATION */}
        <button className="notif-btn">
          <BellIcon />
          <span className="notif-dot"></span>
        </button>

        {/* USER */}
        <div className="avatar">J</div>
      </div>
    </header>
  );
}