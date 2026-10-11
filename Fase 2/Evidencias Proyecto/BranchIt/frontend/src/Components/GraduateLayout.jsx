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
          <strong>
            BranchIt<small>Tu carrera, tu crecimiento.</small>
          </strong>
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
          <span className="eyebrow">MI CRECIMIENTO</span>
          <GrowthTree percent={percent} />
          <strong>Tu historia toma forma</strong>
          <progress value={percent} max="100" aria-label="Perfil completo" />
          <p>Tu progreso refleja lo que has añadido a tu perfil.</p>
          <NavLink to="/perfil-egresado">
            Seguir creciendo <FiArrowUpRight />
          </NavLink>
        </div>
        <small className="sidebar-note">
          No necesitas tenerlo todo resuelto.
          <br />
          Solo dar el siguiente paso.
        </small>
      </aside>
      <div className="garden-content">{children}</div>
    </div>
  );
}
GraduateLayout.propTypes = {
  profile: PropTypes.object,
  children: PropTypes.node.isRequired,
};
