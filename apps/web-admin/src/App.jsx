import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import { api } from "./services/api";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import Documents from "./pages/Documents";
import Alerts from "./pages/Alerts";
import Logs from "./pages/Logs";
import ValidationDetails from "./pages/ValidationDetails";

function PrivateRoute({ children, title }) {
  if (!api.getToken()) return <Navigate to="/login" replace />;
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <Navbar title={title} />
        <main className="flex-1 p-6 bg-slate-100">{children}</main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route
          path="/"
          element={<PrivateRoute title="Dashboard"><Dashboard /></PrivateRoute>}
        />
        <Route
          path="/users"
          element={<PrivateRoute title="Utilisateurs"><Users /></PrivateRoute>}
        />
        <Route
          path="/documents"
          element={<PrivateRoute title="Documents"><Documents /></PrivateRoute>}
        />
        <Route
          path="/documents/:id"
          element={<PrivateRoute title="Détails document"><ValidationDetails /></PrivateRoute>}
        />
        <Route
          path="/alerts"
          element={<PrivateRoute title="Alertes de conformité"><Alerts /></PrivateRoute>}
        />
        <Route
          path="/logs"
          element={<PrivateRoute title="Logs pipeline"><Logs /></PrivateRoute>}
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
