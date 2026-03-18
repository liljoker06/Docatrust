import { useNavigate, Link } from "react-router-dom";
import { useState } from "react";
import logo from "../assets/logo.png";
import "../styles/login.css";

export default function SignUp() {
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSignUp = (e) => {
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

            <button className="login-button" type="submit">
              Create Account
            </button>
          </form>

          <p className="login-footer-text">
            Already have an account? <Link to="/">Sign In</Link>
          </p>

          <div className="login-copyright">
            © 2026 DocaTrust. All rights reserved.
          </div>
        </div>
      </div>
    </div>
  );
}
