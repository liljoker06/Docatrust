import { Link } from "react-router-dom";
import logo from "../assets/logo.png";
import "../styles/home.css";

const FEATURES = [
  {
    icon: "🔍",
    title: "OCR & Extraction IA",
    desc: "Extraction automatique des données clés depuis vos PDF, images et scans grâce à PaddleOCR et nos modèles NLP.",
  },
  {
    icon: "🏢",
    title: "Vérification SIRENE",
    desc: "Contrôlez instantanément vos fournisseurs via la base officielle INSEE — SIRET, SIREN, statut juridique.",
  },
  {
    icon: "⚡",
    title: "Pipeline automatisé",
    desc: "De l'upload au résultat validé en quelques secondes. Alertes, conformité et historique sans intervention manuelle.",
  },
];

export default function Home() {
  return (
    <div className="home-page">
      {/* Orbs décoratifs */}
      <div className="home-orb one" />
      <div className="home-orb two" />
      <div className="home-orb three" />

      {/* ── Navbar ── */}
      <nav className="home-nav">
        <Link to="/" className="home-nav-brand">
          <img src={logo} alt="Pyra logo" />
          <span>DocaTrust</span>
        </Link>

        <div className="home-nav-actions">
          <Link to="/login" className="home-btn-ghost">Connexion</Link>
          <Link to="/signup" className="home-btn-solid">Inscription</Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="home-hero">
        <div className="home-hero-badge">
          <span />
          Plateforme de conformité documentaire
        </div>

        <h1>
          Automatisez votre<br />
          <em>conformité documentaire</em>
        </h1>

        <p>
          Pyra analyse, classe et valide vos documents métier en quelques secondes
          grâce à l'intelligence artificielle et aux données officielles INSEE.
        </p>

        <div className="home-hero-cta">
          <Link to="/signup" className="home-cta-primary">
            Commencer gratuitement →
          </Link>
          <Link to="/login" className="home-cta-secondary">
            Se connecter
          </Link>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="home-features" id="fonctionnalites">
        <p className="home-features-title">Ce que Pyra fait pour vous</p>
        <div className="home-features-grid">
          {FEATURES.map((f) => (
            <div className="home-feature-card" key={f.title}>
              <div className="home-feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="home-footer">
        © 2026 DocaTrust. Tous droits réservés.
      </footer>
    </div>
  );
}
