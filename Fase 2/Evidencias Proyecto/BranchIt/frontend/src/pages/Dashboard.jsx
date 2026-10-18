import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FiArrowRight, FiBriefcase, FiFileText, FiSend } from "react-icons/fi";
import { useSession } from "../session";
import { api } from "../api";
import WorkspaceNav from "../Components/WorkspaceNav";

export default function Dashboard() {
  const { user } = useSession();
  const company = user.tipo === "empresa";
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    const request = company
      ? api.companySummary(user.id)
      : Promise.all([
          api.obtenerPerfilEgresado(user.id),
          api.myApplications(),
          api.jobs(),
        ]).then(([profile, applications, jobs]) => ({
          nombre: profile.nombre,
          presentacion: profile.presentacion,
          postulaciones: applications.length,
          ofertas: jobs.length,
          ultimas: applications.slice(0, 3),
        }));
    request
      .then((value) => {
        if (active) setData(value);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [company, user.id]);
  return (
    <section className="contenedor dashboard">
      <WorkspaceNav />
      <div className="dashboard-heading">
        <h1>{data ? `Hola, ${data.nombre}` : "Tu espacio en BranchIT"}</h1>
      </div>
      {error && (
        <p className="mensaje-error" role="alert">
          {error}
        </p>
      )}
      {!data && !error && <p role="status">Cargando tu resumen…</p>}
      {data && (
        <>
          <div className="stats-grid">
            <article>
              <FiBriefcase />
              <strong>{data.ofertas}</strong>
              <span>
                {company ? "Ofertas publicadas" : "Oportunidades disponibles"}
              </span>
            </article>
            <article>
              <FiSend />
              <strong>{data.postulaciones}</strong>
              <span>
                {company ? "Postulaciones recibidas" : "Postulaciones enviadas"}
              </span>
            </article>
            <article>
              <FiFileText />
              <strong>
                {company
                  ? data.activas
                  : data.presentacion
                  ? "Lista"
                  : "Pendiente"}
              </strong>
              <span>{company ? "Ofertas abiertas" : "Tu presentación"}</span>
            </article>
          </div>
          <div className="dashboard-actions">
            <article className="tarjeta">
              <h2>{company ? "Publicar oferta" : "Mi presentación"}</h2>
              <Link
                className="boton boton-primario"
                to={company ? "/ofertas-empresa" : "/perfil-egresado"}
              >
                {company ? "Gestionar ofertas" : "Editar mi presentación"}
                <FiArrowRight />
              </Link>
            </article>
            <article className="tarjeta">
              <h2>
                {company ? "Revisa las postulaciones" : "Ofertas de empleo"}
              </h2>
              <Link
                className="boton boton-secundario"
                to={company ? "/ofertas-empresa" : "/ofertas"}
              >
                {company ? "Ver mis ofertas" : "Explorar ofertas"}
                <FiArrowRight />
              </Link>
            </article>
          </div>
          {!company && (
            <div className="tarjeta">
              <h2>Últimas postulaciones</h2>
              {!data.ultimas.length ? (
                <p>Aún no has enviado postulaciones.</p>
              ) : (
                data.ultimas.map((item) => (
                  <Link
                    className="activity-row"
                    key={item.id}
                    to="/mis-postulaciones"
                  >
                    <span>
                      <strong>{item.titulo}</strong>
                      <small>{item.nombre_empresa}</small>
                    </span>
                    <span className="status-badge">Recibida</span>
                  </Link>
                ))
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
}
