import { useEffect, useState } from "react";
import { api } from "../services/api";

const ROLES = ["ADMIN", "OPERATOR", "AUDITOR"];

const ROLE_COLORS = {
  ADMIN: "bg-purple-100 text-purple-700",
  OPERATOR: "bg-blue-100 text-blue-700",
  AUDITOR: "bg-slate-100 text-slate-600",
};

function ConfirmModal({ message, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-sm mx-4">
        <p className="text-slate-800 text-sm font-medium mb-5">{message}</p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-lg text-sm text-slate-600 bg-slate-100 hover:bg-slate-200 transition-colors"
          >
            Annuler
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 rounded-lg text-sm text-white bg-red-500 hover:bg-red-600 transition-colors"
          >
            Confirmer
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Users() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirm, setConfirm] = useState(null);

  async function load() {
    try {
      const data = await api.listUsers();
      setUsers(data.users);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleRoleChange(id, role) {
    await api.updateUserRole(id, role);
    setUsers((prev) =>
      prev.map((u) => (u.id === id ? { ...u, role } : u))
    );
  }

  async function handleDisable(id) {
    await api.disableUser(id);
    setUsers((prev) =>
      prev.map((u) => (u.id === id ? { ...u, is_active: false } : u))
    );
    setConfirm(null);
  }

  async function handleDelete(id) {
    await api.deleteUser(id);
    setUsers((prev) => prev.filter((u) => u.id !== id));
    setConfirm(null);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <>
      {confirm && (
        <ConfirmModal
          message={confirm.message}
          onConfirm={confirm.onConfirm}
          onCancel={() => setConfirm(null)}
        />
      )}

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-700">
            {users.length} utilisateur{users.length !== 1 ? "s" : ""}
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 text-slate-500 font-medium text-xs uppercase tracking-wide">
                <th className="text-left px-6 py-3">Email</th>
                <th className="text-left px-6 py-3">Rôle</th>
                <th className="text-left px-6 py-3">Statut</th>
                <th className="text-left px-6 py-3">Créé le</th>
                <th className="text-right px-6 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 text-slate-800 font-medium">
                    {user.email}
                  </td>

                  {/* Role select */}
                  <td className="px-6 py-4">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      className={`text-xs font-semibold px-2.5 py-1.5 rounded-lg border-0 cursor-pointer focus:ring-2 focus:ring-blue-500 ${ROLE_COLORS[user.role] || "bg-slate-100 text-slate-600"}`}
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>{r}</option>
                      ))}
                    </select>
                  </td>

                  {/* Status */}
                  <td className="px-6 py-4">
                    {user.is_active ? (
                      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-50 px-2.5 py-1 rounded-full">
                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                        Actif
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-xs font-medium text-red-600 bg-red-50 px-2.5 py-1 rounded-full">
                        <span className="w-1.5 h-1.5 bg-red-400 rounded-full" />
                        Désactivé
                      </span>
                    )}
                  </td>

                  <td className="px-6 py-4 text-slate-500 text-xs">
                    {user.created_at
                      ? new Date(user.created_at).toLocaleDateString("fr-FR")
                      : "—"}
                  </td>

                  {/* Actions */}
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-2">
                      {user.is_active && (
                        <button
                          onClick={() =>
                            setConfirm({
                              message: `Désactiver le compte de ${user.email} ?`,
                              onConfirm: () => handleDisable(user.id),
                            })
                          }
                          className="text-xs text-orange-600 hover:text-orange-700 font-medium px-2.5 py-1.5 rounded-lg hover:bg-orange-50 transition-colors"
                        >
                          Désactiver
                        </button>
                      )}
                      <button
                        onClick={() =>
                          setConfirm({
                            message: `Supprimer définitivement le compte de ${user.email} ?`,
                            onConfirm: () => handleDelete(user.id),
                          })
                        }
                        className="text-xs text-red-500 hover:text-red-700 font-medium px-2.5 py-1.5 rounded-lg hover:bg-red-50 transition-colors"
                      >
                        Supprimer
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {users.length === 0 && (
            <div className="text-center py-16 text-slate-400 text-sm">
              Aucun utilisateur trouvé.
            </div>
          )}
        </div>
      </div>
    </>
  );
}
