import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { useSession } from "../session";
import WorkspaceNav from "../Components/WorkspaceNav";

import { ValidatedForm, PhoneField } from "../Components/FormFields";
import AnswerField from "../Components/AnswerField";
import JobFacts from "../Components/JobFacts";
import CompanyPhoto from '../Components/CompanyPhoto';
import ShareJob from "../Components/ShareJob";

export default function Apply() {
  const { jobId } = useParams();
  const { user } = useSession();
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [employment, setEmployment] = useState(null);
  useEffect(() => {
    let active = true;
    Promise.all([api.job(jobId), api.myApplications(), api.employment()])
      .then(([value, applications, status]) => {
        if (active) {
          setJob(value);
          setEmployment(status);
          setSent(applications.some((item) => item.oferta_id === value.id));
        }
      })
      .catch((err) => {
        if (active) setError(err.message);
      });
    return () => {
      active = false;
    };
  }, [jobId]);
  async function submit(event) {
    event.preventDefault();
    if (!employment?.puede_postular) {
      setError("Tu búsqueda está pausada. Revisa tu seguimiento laboral antes de postular.");
      return;
    }
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const respuestas = Object.fromEntries(
      job.preguntas.map((q) => [
        q.id,
        q.tipo === "seleccion_multiple"
          ? form.getAll(`answer_${q.id}`)
          : form.get(`answer_${q.id}`) || "",
      ]),
    );
    try {
      await api.apply({
        oferta_id: job.id,
        formulario_version: job.formulario_version,
        telefono: form.get("telefono"),
        cv_url: form.get("cv_url"),
        mensaje: form.get("mensaje"),
        consentimiento: form.get("consentimiento") === "on",
        respuestas,
      });
      setSent(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="contenedor dashboard">
      <WorkspaceNav />
      <Link className="back-link" to="/ofertas">
        ← Volver a las ofertas
      </Link>
      <h1>Postular</h1>
      {error && (
        <p className="mensaje-error" role="alert">
          {error}
        </p>
      )}
      {!job && !error && <p role="status">Cargando formulario…</p>}
      {job && (
        <div className="application-layout">
          <aside className="tarjeta">
            <CompanyPhoto job={job} />
            <span className="eyebrow">{job.nombre_empresa}</span>
            <h2>{job.titulo}</h2>
            <p className="muted">
              {job.ubicacion} ·{" "}
              {job.modalidad === "hibrido"
                ? "Híbrido"
                : job.modalidad || "Modalidad por definir"}
            </p>
            <p>{job.descripcion}</p>
            <JobFacts job={job} />
            <h3>Requisitos</h3>
            <p>{job.requisitos || "No se indicaron requisitos adicionales."}</p>
            <ShareJob job={job} />
            <button type="button" className="job-ai-question" onClick={() => window.dispatchEvent(new CustomEvent("branchit-open-ai", { detail: { modo: "postulacion", ofertaId: job.id } }))}>Prepararme con IA</button>
          </aside>
          {sent ? (
            <div className="tarjeta">
              <h2>Tu postulación fue recibida</h2>
              <p role="status">
                La empresa puede revisar tus antecedentes. Puedes consultar lo
                que enviaste en tu historial.
              </p>
              <Link className="boton boton-primario" to="/mis-postulaciones">
                Ver mis postulaciones
              </Link>
            </div>
          ) : !employment?.puede_postular ? (
            <div className="tarjeta">
              <h2>{employment?.limite_experiencia ? "Límite de experiencia alcanzado" : "Nuevas postulaciones bloqueadas"}</h2>
              <p>
                {employment?.limite_experiencia
                  ? "Alcanzaste un año de experiencia en la contratación registrada. Puedes consultar y compartir ofertas y usar la IA, pero no enviar nuevas postulaciones. Una suscripción no cambia esta condición."
                  : employment?.requiere_finiquito
                  ? "Tienes una contratación registrada. Presenta tu finiquito desde el seguimiento laboral para revisar si puedes volver a postular."
                  : "Puedes seguir consultando ofertas, pero necesitas reanudar tu búsqueda para postular."}
              </p>
              <Link className="boton boton-secundario" to="/seguimiento">Revisar seguimiento laboral</Link>
            </div>
          ) : !job.activa ? (
            <div className="empty-state">
              <h2>Esta oferta está cerrada</h2>
              <p>Explora otras oportunidades disponibles.</p>
            </div>
          ) : (
            <ValidatedForm className="tarjeta" onSubmit={submit}>
              <h2>Completa tu postulación</h2>
              <p>
                Compartiremos tu nombre, carrera, presentación y correo (
                {user.email}) con {job.nombre_empresa}.
              </p>
              <PhoneField label="Teléfono de contacto (opcional)" />
              <div className="campo">
                <label htmlFor="cv_url">
                  Enlace a tu currículum o portafolio (opcional)
                </label>
                <input
                  id="cv_url"
                  name="cv_url"
                  type="url"
                  placeholder="https://…"
                  maxLength={500}
                />
              </div>
              <div className="campo">
                <label htmlFor="mensaje">
                  Mensaje para la empresa (opcional)
                </label>
                <textarea
                  id="mensaje"
                  name="mensaje"
                  rows={3}
                  maxLength={3000}
                />
              </div>
              {job.preguntas.length > 0 && <h3>Preguntas de la empresa</h3>}
              {job.preguntas.map((q) => (
                <AnswerField key={q.id} question={q} />
              ))}
              <label className="consent">
                <input type="checkbox" name="consentimiento" required />
                Autorizo compartir mi carrera, habilidades, proyectos, certificaciones,
                experiencia laboral, enlace al título y estos antecedentes con esta empresa
                para evaluar mi postulación.
              </label>
              <button className="boton boton-primario" disabled={busy}>
                {busy ? "Enviando…" : "Enviar postulación"}
              </button>
            </ValidatedForm>
          )}
        </div>
      )}
    </section>
  );
}
