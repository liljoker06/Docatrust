import { useNavigate, Link } from "react-router-dom";
import { useState } from "react";
import logo from "../assets/logo.png";
import "../styles/login.css";
import { setAuthSession } from "../lib/auth";
import { loginApi, registerApi } from "../services/authApi";

export default function SignUp() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignUp = async (e) => {
    e.preventDefault();
    if (!fullName.trim() || !email.trim() || !password.trim()) {
      setError("All fields are required.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await registerApi(email.trim(), password);
      const loginData = await loginApi(email.trim(), password);
      setAuthSession({
        token: loginData.token,
        user: { ...loginData.user, name: fullName.trim() },
      });
      navigate("/dashboard");
    } catch (e2) {
      setError(e2.message || "Sign up failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-orb one"></div>
      <div className="login-orb two"></div>
      <div className="login-orb three"></div>

      <div className="login-shell">
        <div className="login-brand">
          <img src={logo} alt="DocaTrust logo" />
          <h1>DocaTrust</h1>
        </div>

        <div className="login-card">
          <h2 className="login-title">Create Account</h2>

          <form onSubmit={handleSignUp}>
            {/* Full Name */}
            <div className="login-field">
              <div className="login-label">
                <span>Full Name</span>
              </div>
              <div className="login-input-wrap">
                <input
                  className="login-input"
                  type="text"
                  placeholder="John Doe"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                />
              </div>
            </div>

            {/* Email */}
            <div className="login-field">
              <div className="login-label">
                <span>Email</span>
              </div>
              <div className="login-input-wrap">
                <input
                  className="login-input"
                  type="email"
                  placeholder="john.doe@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            {/* Password */}
            <div className="login-field">
              <div className="login-label">
                <span>Password</span>
              </div>
              <div className="login-input-wrap">
                <input
                  className="login-input"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <button className="login-button" type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create Account"}
            </button>
            {error && (
              <p style={{ color: "#ffb8b8", fontSize: 13, marginTop: 10 }}>
                {error}
              </p>
            )}
          </form>

          <p className="login-footer-text">
            Déjà un compte ? <Link to="/login">Se connecter</Link>
          </p>
          <p className="login-footer-text" style={{ marginTop: 0 }}>
            <Link to="/" style={{ color: "#79a0ff", fontSize: 13 }}>← Retour à l'accueil</Link>
          </p>

          <div className="login-copyright">
            © 2026 DocaTrust. All rights reserved.
          </div>
        </div>
      </div>
    </div>
  );
}
