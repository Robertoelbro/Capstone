import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import WorkspaceNav from "../Components/WorkspaceNav";

export default function Applications() {
  const { jobId } = useParams();
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setItems(null);
    setError("");
    (jobId ? api.applicants(jobId) : api.myApplications())
      .then((data) => {
        if (active) setItems(data);
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [jobId]);
  return (
    <section className="contenedor dashboard">
      <WorkspaceNav />
      <h1>{jobId ? "Postulaciones recibidas" : "Mis postulaciones"}</h1>
      <p className="muted">
        {jobId
          ? "Los datos se comparten contigo para evaluar esta postulación."
          : "Revisa el detalle de los antecedentes que enviaste a cada empresa."}
      </p>
      {error && (
        <p className="mensaje-error" role="alert">
          {error}
        </p>
      )}
      {!items && !error && <p role="status">Cargando postulaciones…</p>}
      {items?.length === 0 && (
        <div className="empty-state">
          <h2>Todavía no hay postulaciones</h2>
          <p>
            {jobId
              ? "Las nuevas postulaciones aparecerán aquí."
              : "Encuentra una oferta que se ajuste a tus intereses."}
          </p>
          <Link to={jobId ? "/ofertas-empresa" : "/ofertas"}>Ver ofertas</Link>
        </div>
      )}
      {items?.map((item) => (
        <article key={item.id} className="tarjeta application-card">
          <div className="section-heading">
            <div>
              <h2>
                {jobId
                  ? `${item.datos.nombre} ${item.datos.apellido}`
                  : item.titulo}
              </h2>
              <p>
                {jobId ? item.titulo : item.nombre_empresa} ·{" "}
                {new Date(
                  item.fecha_postulacion +
                    (item.fecha_postulacion.endsWith("Z") ? "" : "Z"),
                ).toLocaleDateString("es-CL")}
              </p>
            </div>
            <span className="status-badge">Recibida</span>
          </div>
          {!item.oferta_activa && (
            <p className="muted">Esta oferta está cerrada.</p>
          )}
          <details>
            <summary>
              {jobId ? "Ver antecedentes y respuestas" : "Ver mi postulación"}
            </summary>
            <dl className="application-details">
              <dt>Nombre</dt>
              <dd>
                {item.datos.nombre} {item.datos.apellido}
              </dd>
              <dt>Correo</dt>
              <dd>{item.datos.email}</dd>
              <dt>Teléfono</dt>
              <dd>{item.datos.telefono || "No indicado"}</dd>
              <dt>Carrera</dt>
              <dd>{item.datos.carrera || "No indicada"}</dd>
              <dt>Presentación al postular</dt>
              <dd>{item.datos.presentacion || "Sin presentación"}</dd>
              <dt>Mensaje</dt>
              <dd>{item.datos.mensaje || "Sin mensaje adicional"}</dd>
              {item.datos.cv_url && (
                <>
                  <dt>Currículum o portafolio</dt>
                  <dd>
                    <a
                      href={item.datos.cv_url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Abrir enlace compartido
                    </a>
                  </dd>
                </>
              )}
            </dl>
            {item.datos.preguntas.map((q) => (
              <div key={q.id} className="answer">
                <strong>{q.etiqueta}</strong>
                <p>{item.datos.respuestas[q.id] || "Sin respuesta"}</p>
              </div>
            ))}
          </details>
        </article>
      ))}
    </section>
  );
}
