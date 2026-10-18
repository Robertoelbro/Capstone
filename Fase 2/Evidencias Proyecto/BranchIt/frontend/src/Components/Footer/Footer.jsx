import { Link } from "react-router-dom";
import { panelPath, useSession } from "../../session";
export default function Footer() {
  const { user } = useSession();
  return (
    <footer className="site-footer">
      <div className="contenedor footer-inner">
        <div>
          <Link to={user ? panelPath(user) : "/"} className="brand">
            Branch<span>IT</span>
          </Link>
        </div>
        <nav aria-label="Enlaces del pie de página">
          {user?.tipo === "empresa" ? (
            <Link to="/perfil-empresa">Mi empresa</Link>
          ) : (
            <Link to="/">Buscar empleo</Link>
          )}
          <Link to="/registro/empresa">Soy empresa</Link>
          <Link to="/registro">Crear cuenta</Link>
        </nav>
      </div>
      <div className="contenedor footer-bottom">
        <span>© {new Date().getFullYear()} BranchIT</span>
      </div>
    </footer>
  );
}
