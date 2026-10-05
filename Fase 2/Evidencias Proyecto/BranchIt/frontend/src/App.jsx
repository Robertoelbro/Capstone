import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import PropTypes from "prop-types";
import Header from "./Components/Header/Header";
import Footer from "./Components/Footer/Footer";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import PerfilEgresado from "./pages/PerfilEgresado";
import OfertasEmpresa from "./pages/OfertasEmpresa";
import Dashboard from "./pages/Dashboard";
import Apply from "./pages/Apply";
import Applications from "./pages/Applications";
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
  const location = useLocation();
  return (
    <div className="app-shell">
      {import.meta.env.VITE_DEMO_MODE === "true" && (
        <div className="demo-banner">
          Vista de prueba · Datos y cuentas ficticios
        </div>
      )}
      <Header />
      <main id="contenido">
        <Routes>
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
                <Dashboard />
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
    </div>
  );
}
