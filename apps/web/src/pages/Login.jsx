import { useNavigate, Link } from "react-router-dom";
import { useState } from "react";
import logo from "../assets/logo.png";
import "../styles/login.css";

function MailIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="3" y="5" width="18" height="14" rx="2"></rect>
      <path d="M4 7l8 6 8-6"></path>
    </svg>
  );
}

function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="5" y="11" width="14" height="10" rx="2"></rect>
      <path d="M8 11V8a4 4 0 118 0v3"></path>
    </svg>
  );
}

function EyeIcon({ open }) {
  return open ? (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6-10-6-10-6z"></path>
      <circle cx="12" cy="12" r="3"></circle>
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M3 3l18 18"></path>
    </svg>
  );
}

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = (e) => {
    e.preventDefault();
    navigate("/dashboard");
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
          <h2 className="login-title">Login</h2>

          <form onSubmit={handleLogin}>
            <div className="login-field">
              <div className="login-label">
                <MailIcon />
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

            <div className="login-field">
              <div className="login-label">
                <LockIcon />
                <span>Password</span>
              </div>
              <div className="login-input-wrap">
                <input
                  className="login-input"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword((prev) => !prev)}
                >
                  <EyeIcon open={showPassword} />
                </button>
              </div>
            </div>

            <button className="login-button" type="submit">
              Sign In
            </button>
          </form>

          <p className="login-footer-text">
            Don’t have an account? <Link to="/signup">Sign Up</Link>
          </p>

          <div className="login-social-row">
            <div className="login-social-line"></div>
            <div className="login-social-icons">
              <div className="social-btn">G</div>
              <div className="social-btn"></div>
              <div className="social-btn">f</div>
            </div>
            <div className="login-social-line"></div>
          </div>

          <div className="login-copyright">
            © 2026 DocaTrust. All rights reserved.
          </div>
        </div>
      </div>
    </div>
  );
}