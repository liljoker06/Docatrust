import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div style={{ width: "220px", padding: "20px", borderRight: "1px solid #ccc" }}>
      <h3>Admin Menu</h3>

      <div><Link to="/">Dashboard</Link></div>
      <div><Link to="/suppliers">Suppliers</Link></div>
      <div><Link to="/alerts">Alerts</Link></div>
      <div><Link to="/logs">Logs</Link></div>
      <div><Link to="/validation">Validation</Link></div>
    </div>
  );
}