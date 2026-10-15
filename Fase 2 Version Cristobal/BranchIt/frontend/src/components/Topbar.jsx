import { NavLink } from "react-router-dom";
import {
  HiOutlineBriefcase,
  HiOutlineLocationMarker,
  HiOutlineSearch,
  HiOutlineHome,
  HiOutlineUserGroup,
  HiOutlineChatAlt2,
  HiOutlineBell,
  HiOutlineUserCircle,
  HiOutlineMenu,
} from "react-icons/hi";

const iconLinkClase = ({ isActive }) =>
  `p-2 rounded-full text-xl transition-colors ${
    isActive ? "text-brand-600 bg-brand-50" : "text-muted hover:text-ink hover:bg-canvas"
  }`;

/**
 * Barra superior: buscador (cargo/categoría + lugar) y accesos rápidos.
 * El botón hamburguesa solo se ve en mobile y abre el Sidebar.
 */
export default function Topbar({ onAbrirMenu }) {
  return (
    <header className="sticky top-0 z-20 bg-canvas/90 backdrop-blur border-b border-line">
      <div className="flex items-center gap-3 px-4 py-3 lg:px-8">
        <button
          onClick={onAbrirMenu}
          className="lg:hidden text-2xl text-ink shrink-0"
          aria-label="Abrir menú"
        >
          <HiOutlineMenu />
        </button>

        <form
          onSubmit={(e) => e.preventDefault()}
          className="flex flex-1 items-center gap-2 bg-surface border border-line rounded-full px-2 py-1.5 max-w-xl"
        >
          <div className="flex flex-1 items-center gap-2 px-2 min-w-0">
            <HiOutlineBriefcase className="text-muted shrink-0" />
            <input
              type="text"
              placeholder="Cargo o Categoría"
              className="w-full bg-transparent text-sm outline-none placeholder:text-muted"
            />
          </div>
          <div className="hidden sm:flex flex-1 items-center gap-2 px-2 border-l border-line min-w-0">
            <HiOutlineLocationMarker className="text-muted shrink-0" />
            <input
              type="text"
              placeholder="Lugar"
              className="w-full bg-transparent text-sm outline-none placeholder:text-muted"
            />
          </div>
          <button
            type="submit"
            aria-label="Buscar"
            className="shrink-0 bg-brand-600 hover:bg-brand-700 text-white rounded-full p-2 transition-colors"
          >
            <HiOutlineSearch />
          </button>
        </form>

        <div className="hidden md:flex items-center gap-1 ml-auto">
          <NavLink to="/" end className={iconLinkClase} aria-label="Inicio">
            <HiOutlineHome />
          </NavLink>
          <NavLink to="/conexiones" className={iconLinkClase} aria-label="Conexiones">
            <HiOutlineUserGroup />
          </NavLink>
          <NavLink to="/mensajes" className={iconLinkClase} aria-label="Mensajes">
            <HiOutlineChatAlt2 />
          </NavLink>
          <NavLink to="/notificaciones" className={iconLinkClase} aria-label="Notificaciones">
            <HiOutlineBell />
          </NavLink>
          <NavLink to="/perfil" className={iconLinkClase} aria-label="Mi perfil">
            <HiOutlineUserCircle />
          </NavLink>
        </div>
      </div>
    </header>
  );
}
