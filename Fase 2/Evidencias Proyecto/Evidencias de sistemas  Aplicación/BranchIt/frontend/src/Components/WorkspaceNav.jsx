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
        <>
          <NavLink to="/ofertas-empresa/nueva">Crear oferta laboral</NavLink>
          <NavLink to="/ofertas-empresa" end>
            Ver ofertas creadas
          </NavLink>
          <NavLink to="/perfil-empresa">Mi empresa</NavLink>
        </>
      ) : (
        <>
          <NavLink to="/perfil-egresado">Mi presentación</NavLink>
          <NavLink to="/mis-postulaciones">Mis postulaciones</NavLink>
          <NavLink to="/seguimiento">Seguimiento laboral</NavLink>
          <NavLink to="/suscripcion">Mi suscripción</NavLink>
          <NavLink to="/ofertas">Explorar ofertas</NavLink>
        </>
      )}
      <NavLink to="/cuenta">Cuenta y seguridad</NavLink>
    </nav>
  );
}
