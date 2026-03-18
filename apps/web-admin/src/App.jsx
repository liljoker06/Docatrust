import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Suppliers from "./pages/Suppliers";
import SupplierDetails from "./pages/SupplierDetails";
import Alerts from "./pages/Alerts";
import Logs from "./pages/Logs";
import ValidationDetails from "./pages/ValidationDetails";

function Layout({ children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <div style={{ flex: 1 }}>
        <Navbar />
        <div style={{ padding: "20px" }}>{children}</div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <Layout>
              <Dashboard />
            </Layout>
          }
        />
        <Route
          path="/suppliers"
          element={
            <Layout>
              <Suppliers />
            </Layout>
          }
        />
        <Route
          path="/suppliers/:id"
          element={
            <Layout>
              <SupplierDetails />
            </Layout>
          }
        />
        <Route
          path="/alerts"
          element={
            <Layout>
              <Alerts />
            </Layout>
          }
        />
        <Route
          path="/logs"
          element={
            <Layout>
              <Logs />
            </Layout>
          }
        />
        <Route
          path="/validation"
          element={
            <Layout>
              <ValidationDetails />
            </Layout>
          }
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}