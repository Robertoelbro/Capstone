import { Routes, Route } from "react-router-dom";
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

export default App;
