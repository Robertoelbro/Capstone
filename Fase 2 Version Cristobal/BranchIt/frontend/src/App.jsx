import { Routes, Route } from "react-router-dom";
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

export default App;
