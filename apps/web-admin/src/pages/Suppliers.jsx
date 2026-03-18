import { Link } from "react-router-dom";
import Table from "../components/Table";
import "../styles/suppliers.css";

export default function Suppliers() {
  const columns = [
    { key: "name", label: "Name" },
    { key: "status", label: "Status" },
    { key: "country", label: "Country" },
  ];

  const data = [
    { id: 1, name: "Supplier A", status: "Validated", country: "France" },
    { id: 2, name: "Supplier B", status: "Pending", country: "Morocco" },
    { id: 3, name: "Supplier C", status: "Rejected", country: "Spain" },
  ];

  return (
    <div className="suppliers-page">
      {/* HEADER */}
      <div className="suppliers-header">
        <h1 className="suppliers-title">Suppliers</h1>
        <p className="suppliers-subtitle">
          View and manage supplier compliance records.
        </p>
      </div>

      {/* TABLE PANEL */}
      <div className="suppliers-panel">
        <div className="panel-head">
          <h3>Suppliers List</h3>
          <span>•••</span>
        </div>

        <div className="suppliers-table-wrap">
          <Table columns={columns} data={data} />
        </div>
      </div>

      {/* DETAILS CARDS */}
      <div className="suppliers-panel">
        <div className="panel-head">
          <h3>Open details</h3>
          <span>•••</span>
        </div>

        <div className="supplier-links">
          {data.map((supplier) => (
            <Link
              key={supplier.id}
              to={`/suppliers/${supplier.id}`}
              className="supplier-link-card"
            >
              <div className="supplier-info">
                <strong>{supplier.name}</strong>
                <p>{supplier.country}</p>
              </div>

              <span className={`supplier-badge ${supplier.status.toLowerCase()}`}>
                {supplier.status}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}