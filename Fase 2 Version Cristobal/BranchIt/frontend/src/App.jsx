import { Routes, Route } from "react-router-dom";
<<<<<<< Updated upstream
import MainLayout from "./layouts/MainLayout";
import Home from "./pages/Home";
import RegistroEgresado from "./pages/RegistroEgresado";
import RegistroEmpresa from "./pages/RegistroEmpresa";
import HubEgresado from "./pages/HubEgresado";
import PerfilEgresado from "./pages/PerfilEgresado";
import OfertasEmpresa from "./pages/OfertasEmpresa";

function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/registro/egresado" element={<RegistroEgresado />} />
        <Route path="/registro/empresa" element={<RegistroEmpresa />} />
        <Route path="/hub-egresado" element={<HubEgresado />} />
        <Route path="/perfil-egresado" element={<PerfilEgresado />} />
        <Route path="/ofertas-empresa" element={<OfertasEmpresa />} />
      </Route>
    </Routes>
  );
}
=======
import AppShell from "./layouts/AppShell";
import Home from "./pages/Home";
import Profile from "./pages/Profile";
import Proximamente from "./pages/Proximamente";

const App = () => {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<Home />} />
        <Route path="/perfil" element={<Profile />} />
        <Route path="/explorar" element={<Proximamente titulo="Explorar empleos" />} />
        <Route path="/conexiones" element={<Proximamente titulo="Mis conexiones" />} />
        <Route path="/mensajes" element={<Proximamente titulo="Mensajes" />} />
        <Route path="/guardados" element={<Proximamente titulo="Guardados" />} />
        <Route path="/notificaciones" element={<Proximamente titulo="Notificaciones" />} />
        <Route path="*" element={<Proximamente titulo="Página no encontrada" />} />
      </Route>
    </Routes>
  );
};
>>>>>>> Stashed changes

export default App;
