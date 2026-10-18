import { useEffect, useRef } from "react";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import PropTypes from "prop-types";
import Header from "./Components/Header/Header";
import Footer from "./Components/Footer/Footer";
import PerfilEmpresa from "./pages/PerfilEmpresa";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import PerfilEgresado from "./pages/PerfilEgresado";
import OfertasEmpresa from "./pages/OfertasEmpresa";
import Dashboard from "./pages/Dashboard";
import Apply from "./pages/Apply";
import Applications from "./pages/Applications";
import PublicPortfolio from "./pages/PublicPortfolio";
import GraduateHub from "./pages/GraduateHub";
import GraduateAssistant from "./Components/GraduateAssistant";
import { panelPath, useSession } from "./session";

function Protected({ role, children }) {
  const { user, loading } = useSession();
  if (loading)
    return (
      <p className="contenedor" role="status">
        Recuperando tu sesión…
      </p>
    );
  if (!user) return <Navigate to="/iniciar-sesion" replace />;
  if (user.tipo !== role) return <Navigate to={panelPath(user)} replace />;
  return children;
}
Protected.propTypes = {
  role: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};

export default function App() {
  const { user } = useSession();
  const location = useLocation();
  const showAssistant = user?.tipo === "egresado" && !location.pathname.startsWith("/p/");
  const previousPath = useRef(location.pathname);
  useEffect(() => {
    const titles = {
      "/": "Buscar empleo", "/ofertas": "Ofertas de empleo",
      "/iniciar-sesion": "Iniciar sesión", "/registro": "Registro de egresado",
      "/registro/empresa": "Registro de empresa", "/perfil-empresa": "Mi empresa",
      "/perfil-egresado": "Mi presentación", "/hub-empresa": "Panel de empresa",
      "/hub-egresado": "Panel de egresado", "/mis-postulaciones": "Mis postulaciones",
      "/ofertas-empresa": "Gestionar ofertas",
    };
    const title = titles[location.pathname] || (location.pathname.startsWith("/p/") ? "Portafolio profesional" : location.pathname.endsWith("/postular") ? "Postular a una oferta" : location.pathname.endsWith("/postulaciones") ? "Postulaciones recibidas" : "Página no encontrada");
    document.title = `${title} | BranchIT`;
    if (previousPath.current !== location.pathname) {
      document.getElementById("contenido")?.focus();
      previousPath.current = location.pathname;
    }
  }, [location.pathname]);
  return (
    <div className={`app-shell${showAssistant ? " has-graduate-assistant" : ""}`}>
      {import.meta.env.VITE_DEMO_MODE === "true" && (
        <div className="demo-banner">
          Vista de prueba · Datos y cuentas ficticios
        </div>
      )}
      <Header />
      <main id="contenido" tabIndex={-1}>
        <Routes>
          <Route path="/perfil-empresa" element={<Protected role="empresa"><PerfilEmpresa /></Protected>} />
          <Route path="/p/:id" element={<PublicPortfolio />} />
          <Route path="/" element={<Home />} />
          <Route path="/ofertas" element={<Home />} />
          <Route
            path="/hub-empresa"
            element={
              <Protected role="empresa">
                <Dashboard />
              </Protected>
            }
          />
          <Route
            path="/ofertas/:jobId/postular"
            element={
              <Protected role="egresado">
                <Apply key={location.pathname} />
              </Protected>
            }
          />
          <Route
            path="/mis-postulaciones"
            element={
              <Protected role="egresado">
                <Applications />
              </Protected>
            }
          />
          <Route
            path="/ofertas-empresa/:jobId/postulaciones"
            element={
              <Protected role="empresa">
                <Applications />
              </Protected>
            }
          />
          <Route
            path="/iniciar-sesion"
            element={<Auth key={location.pathname} />}
          />
          <Route path="/registro" element={<Auth key={location.pathname} />} />
          <Route
            path="/registro/:tipo"
            element={<Auth key={location.pathname} />}
          />
          <Route
            path="/hub-egresado"
            element={
              <Protected role="egresado">
                <GraduateHub />
              </Protected>
            }
          />
          <Route
            path="/perfil-egresado"
            element={
              <Protected role="egresado">
                <PerfilEgresado />
              </Protected>
            }
          />
          <Route
            path="/ofertas-empresa"
            element={
              <Protected role="empresa">
                <OfertasEmpresa />
              </Protected>
            }
          />
          <Route
            path="*"
            element={
              <section className="contenedor">
                <h1>No encontramos esta página</h1>
                <Link to="/">Volver al inicio</Link>
              </section>
            }
          />
        </Routes>
      </main>
      <Footer />
      {showAssistant && <GraduateAssistant key={user.id} />}
    </div>
  );
}
