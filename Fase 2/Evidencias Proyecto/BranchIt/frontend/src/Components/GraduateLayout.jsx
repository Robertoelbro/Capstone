import PropTypes from "prop-types";
import { NavLink } from "react-router-dom";
import {
  FiHome,
  FiSearch,
  FiUser,
  FiSend,
  FiArrowUpRight,
} from "react-icons/fi";
import { growth } from "../portfolio";
import GrowthTree from "./GrowthTree";

export default function GraduateLayout({ profile, children }) {
  const { percent } = growth(profile);
  return (
    <div className="garden-layout">
      <aside className="garden-sidebar">
        <div className="garden-wordmark">
          <span>❧</span>
          <strong>BranchIt</strong>
        </div>
        <nav aria-label="Mi espacio">
          <NavLink to="/hub-egresado">
            <FiHome />
            Para ti
          </NavLink>
          <NavLink to="/ofertas">
            <FiSearch />
            Explorar empleos
          </NavLink>
          <NavLink to="/perfil-egresado">
            <FiUser />
            Mi portafolio
          </NavLink>
          <NavLink to="/mis-postulaciones">
            <FiSend />
            Mis postulaciones
          </NavLink>
        </nav>
        <div className="sidebar-growth">
          <GrowthTree percent={percent} />
          <strong>Perfil completo</strong>
          <progress value={percent} max="100" aria-label="Perfil completo" />

          <NavLink to="/perfil-egresado">
            Editar perfil <FiArrowUpRight />
          </NavLink>
        </div>
      </aside>
      <div className="garden-content">{children}</div>
    </div>
  );
}
GraduateLayout.propTypes = {
  profile: PropTypes.object,
  children: PropTypes.node.isRequired,
};
