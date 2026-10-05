import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import { useSession } from "../session";
import WorkspaceNav from "../Components/WorkspaceNav";

export default function Apply() {
  const { jobId } = useParams();
  const { user } = useSession();
  const [job, setJob] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  useEffect(() => {
    let active = true;
    Promise.all([api.job(jobId), api.myApplications()])
      .then(([value, applications]) => {
        if (active) {
          setJob(value);
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
    setBusy(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const respuestas = Object.fromEntries(
      job.preguntas.map((q) => [q.id, form.get(`answer_${q.id}`) || ""]),
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
      <h1>Postula a tu próxima oportunidad</h1>
      {error && (
        <p className="mensaje-error" role="alert">
          {error}
        </p>
      )}
      {!job && !error && <p role="status">Cargando formulario…</p>}
      {job && (
        <div className="application-layout">
          <aside className="tarjeta">
            <span className="eyebrow">{job.nombre_empresa}</span>
            <h2>{job.titulo}</h2>
            <p className="muted">
              {job.ubicacion} ·{" "}
              {job.modalidad === "hibrido"
                ? "Híbrido"
                : job.modalidad || "Modalidad por definir"}
            </p>
            <p>{job.descripcion}</p>
            <h3>Requisitos</h3>
            <p>{job.requisitos || "No se indicaron requisitos adicionales."}</p>
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
          ) : !job.activa ? (
            <div className="empty-state">
              <h2>Esta oferta está cerrada</h2>
              <p>Explora otras oportunidades disponibles.</p>
            </div>
          ) : (
            <form className="tarjeta" onSubmit={submit}>
              <h2>Completa tu postulación</h2>
              <p>
                Compartiremos tu nombre, carrera, presentación y correo (
                {user.email}) con {job.nombre_empresa}.
              </p>
              <div className="campo">
                <label htmlFor="telefono">
                  Teléfono de contacto (opcional)
                </label>
                <input
                  id="telefono"
                  name="telefono"
                  type="tel"
                  autoComplete="tel"
                  maxLength={30}
                />
              </div>
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
                <div className="campo" key={q.id}>
                  <label htmlFor={`answer_${q.id}`}>
                    {q.etiqueta}{" "}
                    {q.obligatoria ? "(obligatoria)" : "(opcional)"}
                  </label>
                  {q.tipo === "seleccion" ? (
                    <select
                      id={`answer_${q.id}`}
                      name={`answer_${q.id}`}
                      required={q.obligatoria}
                    >
                      <option value="">Selecciona una opción</option>
                      {q.opciones.map((value) => (
                        <option key={value}>{value}</option>
                      ))}
                    </select>
                  ) : q.tipo === "parrafo" ? (
                    <textarea
                      id={`answer_${q.id}`}
                      name={`answer_${q.id}`}
                      required={q.obligatoria}
                      rows={3}
                      maxLength={3000}
                    />
                  ) : (
                    <input
                      id={`answer_${q.id}`}
                      name={`answer_${q.id}`}
                      required={q.obligatoria}
                      type={q.tipo === "numero" ? "number" : "text"}
                      step={q.tipo === "numero" ? "any" : undefined}
                      maxLength={3000}
                    />
                  )}
                </div>
              ))}
              <label className="consent">
                <input type="checkbox" name="consentimiento" required />
                Autorizo compartir estos antecedentes con esta empresa para
                evaluar mi postulación.
              </label>
              <button className="boton boton-primario" disabled={busy}>
                {busy ? "Enviando…" : "Enviar postulación"}
              </button>
            </form>
          )}
        </div>
      )}
    </section>
  );
}
