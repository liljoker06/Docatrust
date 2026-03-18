import "../styles/navbar.css";

function MenuIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 6h16"></path>
      <path d="M4 12h16"></path>
      <path d="M4 18h16"></path>
    </svg>
  );
}

function BellIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M15 17h5l-1.4-1.4A2 2 0 0118 14.2V11a6 6 0 10-12 0v3.2a2 2 0 01-.6 1.4L4 17h5"></path>
      <path d="M10 17a2 2 0 004 0"></path>
    </svg>
  );
}

export default function Navbar() {
  return (
    <div className="navbar">
      <div className="navbar-left">
        <button className="menu-btn">
          <MenuIcon />
        </button>
        <span className="navbar-title">Dashboard</span>
      </div>

      <div className="navbar-right">
        <div className="navbar-search">
          <input type="text" placeholder="Search..." />
        </div>

        <button className="notif-btn">
          <BellIcon />
          <span className="notif-dot"></span>
        </button>

        <div className="avatar">M</div>
      </div>
    </div>
  );
}