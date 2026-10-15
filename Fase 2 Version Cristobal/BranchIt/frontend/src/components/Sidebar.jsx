import { NavLink } from "react-router-dom";
import {
  HiOutlineHome,
  HiOutlineSearch,
  HiOutlineUserGroup,
  HiOutlineChatAlt2,
  HiOutlineBookmark,
} from "react-icons/hi";
import Logo from "./Logo";
import GrowthWidget from "./GrowthWidget";
import { usuarioActual } from "../data/mockData";

const links = [
  { to: "/", label: "Inicio", icon: HiOutlineHome, fin: true },
  { to: "/explorar", label: "Explorar empleos", icon: HiOutlineSearch },
  { to: "/conexiones", label: "Mis conexiones", icon: HiOutlineUserGroup },
  { to: "/mensajes", label: "Mensajes", icon: HiOutlineChatAlt2 },
  { to: "/guardados", label: "Guardados", icon: HiOutlineBookmark },
];

const itemClase = ({ isActive }) =>
  `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive
      ? "bg-brand-50 text-brand-700"
      : "text-ink/80 hover:bg-canvas hover:text-ink"
  }`;

/**
 * Barra lateral fija: navegación principal + widget de crecimiento.
 * En mobile se oculta detrás de un botón hamburguesa (ver Topbar/AppShell).
 */
export default function Sidebar({ abierto, onCerrar }) {
  return (
    <>
      {abierto && (
        <button
          aria-label="Cerrar menú"
          onClick={onCerrar}
          className="fixed inset-0 z-30 bg-black/30 lg:hidden"
        />
      )}
      <aside
        className={`fixed z-40 inset-y-0 left-0 w-64 shrink-0 border-r border-line bg-surface p-5 flex flex-col gap-6
          transition-transform lg:static lg:translate-x-0
          ${abierto ? "translate-x-0" : "-translate-x-full"}`}
      >
        <Logo />

        <nav className="flex flex-col gap-1">
          {links.map(({ to, label, icon: Icon, fin }) => (
            <NavLink key={to} to={to} end={fin} className={itemClase} onClick={onCerrar}>
              <Icon className="text-lg" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto">
          <GrowthWidget porcentaje={usuarioActual.crecimiento} />
        </div>
      </aside>
    </>
  );
}
