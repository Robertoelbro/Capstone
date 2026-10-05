import { Link } from "react-router-dom";
export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="contenedor footer-inner">
        <div>
          <Link to="/" className="brand">
            Branch<span>IT</span>
          </Link>
          <p>El primer paso hacia todo lo que puedes ser.</p>
        </div>
        <nav aria-label="Enlaces del pie de página">
          <Link to="/">Buscar empleo</Link>
          <Link to="/registro/empresa">Soy empresa</Link>
          <Link to="/registro">Crear cuenta</Link>
        </nav>
      </div>
      <div className="contenedor footer-bottom">
        <span>© {new Date().getFullYear()} BranchIT</span>
        <span>Hecho para quienes están comenzando.</span>
      </div>
    </footer>
  );
}
