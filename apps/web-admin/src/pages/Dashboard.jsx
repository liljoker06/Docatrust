import StatCard from "../components/StatCard";

export default function Dashboard() {
  return (
    <div>
      <h1>Admin Dashboard</h1>
      <p>Compliance and supplier monitoring overview.</p>

      <StatCard title="Suppliers" value="24" />
      <StatCard title="Pending validations" value="7" />
      <StatCard title="Alerts" value="3" />
    </div>
  );
}