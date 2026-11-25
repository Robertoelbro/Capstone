import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { useSession } from "../session";
import CompanyPhoto from "../Components/CompanyPhoto";
import JobFacts from "../Components/JobFacts";
import ShareJob from "../Components/ShareJob";

export default function JobDetail() {
  const { jobId } = useParams();
  const { user } = useSession();
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    api.job(jobId).then((data) => { if (active) setJob(data); }).catch((err) => { if (active) setError(err.message); });
    return () => { active = false; };
  }, [jobId]);
  return <section className="contenedor dashboard">
    <Link to="/ofertas" className="back-link">← Ver ofertas</Link>
    {error && <p role="alert" className="mensaje-error">{error}</p>}
    {!job && !error && <p role="status">Cargando oferta…</p>}
    {job && <article className="tarjeta public-job-detail">
      <CompanyPhoto job={job} />
      <p className="eyebrow">{job.nombre_empresa}</p>
      <h1>{job.titulo}</h1>
      <p>{job.ubicacion || "Ubicación por definir"} · {job.modalidad || "Modalidad por definir"}</p>
      <p>{job.descripcion}</p>
      <JobFacts job={job} />
      <h2>Requisitos</h2><p>{job.requisitos || "No se indicaron requisitos adicionales."}</p>
      <ShareJob job={job} />
      {!job.activa ? <p role="status">Esta convocatoria está cerrada.</p> : user?.tipo === "empresa" ? null :
        <Link to={user ? `/ofertas/${job.id}/postular` : "/iniciar-sesion"} className="boton boton-primario">{user ? "Revisar acceso a postulación" : "Iniciar sesión para postular"}</Link>}
      {user?.tipo === "egresado" && job.activa && <button type="button" className="job-ai-question" onClick={() => window.dispatchEvent(new CustomEvent("branchit-open-ai", { detail: { modo: "postulacion", ofertaId: job.id } }))}>¿Qué necesito para postular?</button>}
    </article>}
  </section>;
}
