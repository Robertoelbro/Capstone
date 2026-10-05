import { NavLink } from "react-router-dom";
import { useSession } from "../session";

export default function WorkspaceNav() {
  const { user } = useSession();
  return (
    <nav className="workspace-nav" aria-label="Mi espacio">
      <NavLink to={user.tipo === "empresa" ? "/hub-empresa" : "/hub-egresado"}>
        Resumen
      </NavLink>
      {user.tipo === "empresa" ? (
        <NavLink to="/ofertas-empresa">Gestionar ofertas</NavLink>
      ) : (
        <>
          <NavLink to="/perfil-egresado">Mi presentación</NavLink>
          <NavLink to="/mis-postulaciones">Mis postulaciones</NavLink>
          <NavLink to="/ofertas">Explorar ofertas</NavLink>
        </>
      )}
    </nav>
  );
}
