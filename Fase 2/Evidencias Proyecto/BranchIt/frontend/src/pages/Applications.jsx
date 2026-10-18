import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import WorkspaceNav from "../Components/WorkspaceNav";
import CompanyPhoto from '../Components/CompanyPhoto';

export default function Applications() {
  const { jobId } = useParams();
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  const [page, setPage] = useState(0);
  useEffect(() => {
    let active = true;
    setItems(null);
    setPage(0);
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
      {jobId && items?.length > 0 && <p className="field-help">Ordenados por coincidencias declaradas: carrera (20 puntos) y habilidades o tecnologías solicitadas (40 por coincidencia, hasta 80). Es una ayuda para revisar antecedentes, no una evaluación de desempeño. En un empate se priorizan más coincidencias y luego la fecha de postulación.</p>}
      {(jobId ? items?.slice(page * 10, page * 10 + 10) : items)?.map((item) => (
        <article key={item.id} className="tarjeta application-card">
          <div className="section-heading">
            <div>
              {!jobId && <CompanyPhoto job={item} />}
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
            <span className="status-badge">
              {!item.oferta_activa ? "Convocatoria cerrada" : "Recibida"}
            </span>
            {jobId && item.seleccionada && (
              <span className="status-badge">Candidato seleccionado</span>
            )}
            {jobId && item.destacado && <span className="candidate-featured">Candidato destacado</span>}
          </div>
          {jobId && <div className="candidate-summary">
            <p><strong>Afinidad: {item.afinidad.puntos}/100</strong> · Posición {item.posicion}</p>
            <p>{item.afinidad.carrera_afin ? 'Carrera afín. ' : ''}{item.afinidad.coincidencias.length ? `Coincidencias: ${item.afinidad.coincidencias.join(', ')}.` : 'Sin coincidencias de habilidades registradas.'}</p>
            {item.portfolio_url ? <Link className="boton boton-secundario" to={item.portfolio_url} target="_blank" rel="noopener noreferrer">Ver portafolio ↗</Link> : <p className="muted">Portafolio no publicado.</p>}
          </div>}
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
            {jobId && <section className="candidate-evidence">
              <h3>Antecedentes profesionales</h3>
              <p className="field-help">{item.antecedentes_actuales ? 'Datos actuales del perfil; esta postulación no guardó una copia al enviarse.' : 'Antecedentes guardados al enviar la postulación.'}</p>
              <p><strong>Disponibilidad:</strong> {item.antecedentes.disponibilidad}</p>
              {item.antecedentes.titulo_url && <a className="text-link" href={item.antecedentes.titulo_url} target="_blank" rel="noopener noreferrer">Ver título profesional ↗</a>}
              <h4>Habilidades</h4>
              <p>{item.antecedentes.habilidades.map(s => `${s.nombre} (${s.nivel})`).join(' · ') || 'Sin habilidades registradas.'}</p>
              <h4>Experiencia laboral</h4>
              {item.antecedentes.experiencia_laboral.length ? item.antecedentes.experiencia_laboral.map((work, i) => <article className="candidate-work" key={i}>
                <strong>{work.cargo}</strong><p>{work.empresa} · {work.inicio} — {work.fin || 'Actualidad'}</p><p>{work.descripcion}</p>
              </article>) : <p>Sin experiencia registrada.</p>}
              <h4>Proyectos</h4>
              {item.antecedentes.proyectos.map((project, i) => <article className="candidate-work" key={i}>
                <strong>{project.titulo}</strong><p>{project.descripcion}</p><p>{project.tecnologias.join(' · ')}</p>
                {project.proyecto_url && <a className="text-link" href={project.proyecto_url} target="_blank" rel="noopener noreferrer">Ver proyecto ↗</a>}
                {project.github_url && <a className="text-link" href={project.github_url} target="_blank" rel="noopener noreferrer">GitHub ↗</a>}
              </article>)}
              <h4>Certificaciones</h4>
              {item.antecedentes.certificaciones.map((cert, i) => <p key={i}>{cert.nombre} · {cert.entidad} {cert.url && <a className="text-link" href={cert.url} target="_blank" rel="noopener noreferrer">Ver certificación ↗</a>}</p>)}
            </section>}
            {item.datos.preguntas.map((q) => (
              <div key={q.id} className="answer">
                <strong>{q.etiqueta}</strong>
                <p>
                  {Array.isArray(item.datos.respuestas[q.id])
                    ? item.datos.respuestas[q.id].join(", ") || "Sin respuesta"
                    : item.datos.respuestas[q.id] || "Sin respuesta"}
                </p>
              </div>
            ))}
          </details>
        </article>
      ))}
      {jobId && items?.length > 10 && <nav className="candidate-pagination" aria-label="Páginas de postulantes">
        <button type="button" className="boton boton-secundario" disabled={page === 0} onClick={() => setPage(p => p - 1)}>Anteriores</button>
        <span role="status">{page * 10 + 1}–{Math.min(page * 10 + 10, items.length)} de {items.length}</span>
        <button type="button" className="boton boton-secundario" disabled={(page + 1) * 10 >= items.length} onClick={() => setPage(p => p + 1)}>Siguientes</button>
      </nav>}
    </section>
  );
}
