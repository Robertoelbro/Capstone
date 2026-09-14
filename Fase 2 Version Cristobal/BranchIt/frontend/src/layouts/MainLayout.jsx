import { Link, Outlet } from "react-router-dom";
import "./MainLayout.css";

export default function MainLayout() {
  return (
    <div className="layout">
      <header className="layout-header">
        <div className="contenedor layout-header__inner">
          <Link to="/" className="marca">
            Branch<span className="marca__acento">It</span>
          </Link>
          <nav className="layout-nav">
            <Link to="/hub-egresado">Ofertas</Link>
            <Link to="/perfil-egresado">Mi perfil</Link>
            <Link to="/ofertas-empresa">Panel empresa</Link>
          </nav>
        </div>
      </header>

      <main className="layout-main">
        <Outlet />
      </main>

      <footer className="layout-footer">
        <div className="contenedor">
          <p>BranchIt · Proyecto de título DuocUC</p>
        </div>
      </footer>
    </div>
  );
}
