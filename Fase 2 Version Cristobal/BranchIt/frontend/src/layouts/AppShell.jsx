import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

/**
 * Estructura general de la app ya "logueada": sidebar fijo a la izquierda
 * + barra superior + contenido de cada página (Outlet).
 */
export default function AppShell() {
  const [menuAbierto, setMenuAbierto] = useState(false);

  return (
    <div className="min-h-screen lg:flex bg-canvas">
      <Sidebar abierto={menuAbierto} onCerrar={() => setMenuAbierto(false)} />

      <div className="flex-1 min-w-0">
        <Topbar onAbrirMenu={() => setMenuAbierto(true)} />
        <main className="px-4 py-6 lg:px-8 lg:py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
