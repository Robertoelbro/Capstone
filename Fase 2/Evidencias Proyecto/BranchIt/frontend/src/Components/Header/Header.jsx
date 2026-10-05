import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { FiMenu, FiX, FiArrowUpRight } from "react-icons/fi";
import { panelPath, useSession } from "../../session";

export default function Header() {
  const { user, logout } = useSession();
  const [open, setOpen] = useState(false);
  const [logoutError, setLogoutError] = useState("");
  const [closing, setClosing] = useState(false);
  async function signOut() {
    setClosing(true);
    setLogoutError("");
    try {
      await logout();
    } catch (err) {
      setLogoutError(err.message);
    } finally {
      setClosing(false);
    }
  }
  return (
    <header className="site-header">
      <a className="skip-link" href="#contenido">
        Saltar al contenido
      </a>
      <nav className="contenedor nav-bar" aria-label="Navegación principal">
        <Link className="brand" to="/" onClick={() => setOpen(false)}>
          <span className="brand-mark">
            <FiArrowUpRight />
          </span>
          Branch<span>IT</span>
        </Link>
        <button
          className="mobile-toggle"
          aria-label={open ? "Cerrar menú" : "Abrir menú"}
          aria-expanded={open}
          onClick={() => setOpen(!open)}
        >
          {open ? <FiX /> : <FiMenu />}
        </button>
        <div
          className={`nav-links ${open ? "is-open" : ""}`}
          onClick={() => setOpen(false)}
        >
          <NavLink to="/">Buscar empleo</NavLink>
          {!user && <NavLink to="/registro/empresa">Para empresas</NavLink>}
          {user ? (
            <>
              <NavLink to={panelPath(user)}>Mi panel</NavLink>
              <button
                className="boton boton-secundario"
                onClick={signOut}
                disabled={closing}
                title="Cierra todas tus sesiones activas"
              >
                {closing ? "Cerrando…" : "Cerrar sesión"}
              </button>
            </>
          ) : (
            <>
              <NavLink to="/iniciar-sesion">Iniciar sesión</NavLink>
              <Link to="/registro" className="boton boton-primario">
                Crear cuenta <FiArrowUpRight />
              </Link>
            </>
          )}
        </div>
      </nav>
      {logoutError && (
        <p className="contenedor mensaje-error" role="alert">
          {logoutError}
        </p>
      )}
    </header>
  );
}
