import { useEffect, useRef, useState } from "react";
import { FiArrowUpRight, FiMessageCircle, FiSend, FiX } from "react-icons/fi";
import { api } from "../api";
import { useSession } from "../session";
import "./GraduateAssistant.css";

function anonymousDraft(profile) {
  let text = profile?.presentacion || "";
  for (const name of [profile?.nombre, profile?.apellido].filter(Boolean)) {
    const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    text = text.replace(new RegExp(`\\b${escaped}\\b`, "gi"), "[nombre omitido]");
  }
  return text.replace(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/g, "[correo omitido]")
    .replace(/https?:\/\/\S+/g, "[enlace omitido]")
    .replace(/\b\d{1,2}\.?\d{3}\.?\d{3}-[\dkK]\b/g, "[RUT omitido]")
    .replace(/\+?\d[\d ()-]{6,}\d/g, "[número omitido]");
}

export default function GraduateAssistant() {
  const { user } = useSession();
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState("presentacion");
  const [draft, setDraft] = useState("");
  const [message, setMessage] = useState("");
  const [jobId, setJobId] = useState("");
  const [jobs, setJobs] = useState([]);
  const [profile, setProfile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [consent, setConsent] = useState(false);
  const [available, setAvailable] = useState(false);
  const [checking, setChecking] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [contextError, setContextError] = useState("");
  const dialogRef = useRef(null);
  const launcherRef = useRef(null);
  const titleRef = useRef(null);
  const errorRef = useRef(null);
  const lastMessageRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    let alive = true;
    setChecking(true);
    setContextError("");
    Promise.allSettled([api.assistantStatus(), api.jobs(), api.obtenerPerfilEgresado(user.id)]).then(([status, offers, account]) => {
      if (!alive) return;
      if (status.status === "fulfilled") setAvailable(status.value.disponible);
      else { setAvailable(false); setContextError(status.reason.message); }
      if (offers.status === "fulfilled") setJobs(offers.value);
      else setContextError((e) => e || offers.reason.message);
      if (account.status === "fulfilled") setProfile(account.value);
      setChecking(false);
    });
    return () => { alive = false; };
  }, [open, user.id]);
  useEffect(() => { if (error) errorRef.current?.focus(); }, [error]);
  useEffect(() => { if (open && messages.length) lastMessageRef.current?.scrollIntoView({block: "nearest"}); }, [messages.length, open]);

  function showAssistant() {
    dialogRef.current.showModal();
    setOpen(true);
    titleRef.current.focus();
  }
  function resetConversation() {
    setMessages([]); setMessage(""); setError(""); setConsent(false);
  }
  function changeMode(value) {
    if (value === mode) return;
    setMode(value);
    resetConversation();
  }
  async function submit(event) {
    event.preventDefault();
    if (busy || checking || !available || !consent) return;
    const text = message.trim() || (mode === "presentacion"
      ? "Revisa mi presentación y propón una versión mejorada sin inventar antecedentes."
      : "Comencemos una entrevista de práctica para esta oferta. Hazme la primera pregunta.");
    if (messages.length && !message.trim()) return;
    setBusy(true); setError("");
    try {
      const result = await api.assistantChat({modo: mode, mensaje: text,
        borrador: mode === "presentacion" ? draft : "",
        oferta_id: mode === "entrevista" ? Number(jobId) : null,
        historial: messages.slice(-20).map(({role, text}) => ({role, text})),
        contenido_anonimo: true});
      setMessages((previous) => [...previous, {role: "user", text},
        {role: "model", text: result.respuesta, incomplete: result.incompleta}]);
      setMessage("");
    } catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }

  return (
    <>
      <button ref={launcherRef} className="ai-launcher" type="button" aria-haspopup="dialog"
        aria-expanded={open} aria-controls="graduate-ai-dialog" onClick={showAssistant}>
        <span className="ai-launcher-icon" aria-hidden="true"><FiMessageCircle /></span>
        <span><strong>Modo IA</strong><small>Tu próximo impulso</small></span>
        <FiArrowUpRight aria-hidden="true" />
      </button>
      <dialog ref={dialogRef} id="graduate-ai-dialog" className="ai-dialog" aria-labelledby="graduate-ai-title"
        aria-describedby="graduate-ai-status" onClose={() => {setOpen(false); launcherRef.current?.focus();}}>
        <header className="ai-dialog-header">
          <div><span className="ai-kicker">BRANCHIT · UN ESPACIO PARA CRECER</span>
            <h2 id="graduate-ai-title" ref={titleRef} tabIndex={-1}>Modo IA <span aria-hidden="true">✦</span></h2></div>
          <button className="ai-close" type="button" onClick={() => dialogRef.current.close()} aria-label="Cerrar Modo IA"><FiX aria-hidden="true" /></button>
        </header>
        <div className="ai-dialog-body">
          <p id="graduate-ai-status" role="status" className="ai-availability">{checking ? "Preparando tu espacio…" : available ? "Gemini · Orientación para tu próximo paso" : "Pendiente de configurar la conexión con Gemini."}</p>
          {contextError && <p className="mensaje-error" role="alert">{contextError}</p>}
          <div className="role-tabs" aria-label="Tipo de orientación">
            <button type="button" aria-pressed={mode === "presentacion"} disabled={busy} onClick={() => changeMode("presentacion")}>Revisar presentación</button>
            <button type="button" aria-pressed={mode === "entrevista"} disabled={busy} onClick={() => changeMode("entrevista")}>Practicar entrevista</button>
          </div>
          <form className="ai-coaching-form" onSubmit={submit}>
            {mode === "presentacion" ? <>
              <label htmlFor="ai-draft">Borrador de tu presentación (sin datos personales)</label>
              <textarea id="ai-draft" rows={5} value={draft} required maxLength={5000} disabled={busy}
                aria-describedby="ai-draft-help" onChange={(e) => {setDraft(e.target.value); resetConversation();}}
                placeholder="Ejemplo ficticio: Soy egresado de Informática y desarrollé un sistema de inventario con Python…" />
              <p id="ai-draft-help" className="ai-help">Puedes editar el borrador antes de enviarlo. Al cambiarlo comienza una nueva conversación. Las sugerencias no modifican tu perfil.</p>
              {profile?.presentacion && <button className="text-link" type="button" disabled={busy} onClick={() => {setDraft(anonymousDraft(profile)); resetConversation();}}>Copiar mi presentación al borrador</button>}
            </> : <>
              <label htmlFor="ai-job">Oferta para practicar</label>
              <select id="ai-job" value={jobId} required disabled={busy || checking} onChange={(e) => {setJobId(e.target.value); resetConversation();}}>
                <option value="">Selecciona una oferta activa</option>
                {jobs.map((job) => <option key={job.id} value={job.id}>{job.titulo} · {job.nombre_empresa}</option>)}
              </select>
              {!checking && !jobs.length && <p className="ai-help">No hay ofertas disponibles para practicar en este momento.</p>}
              <p className="ai-help">Recibirás una pregunta por turno y comentarios sobre tu respuesta. Esta práctica no es una entrevista con la empresa.</p>
            </>}
            <p className="ai-connection-note" id="ai-sharing">El texto y la conversación se enviarán a Google; en entrevistas también se enviará el contenido de la oferta. El servicio gratuito puede usar lo enviado para mejorar sus productos. Usa únicamente contenido ficticio o anonimizado: elimina nombres, contactos y datos personales o confidenciales. Revisa el borrador incluso después de copiarlo.</p>
            <label className="ai-consent"><input type="checkbox" checked={consent} required disabled={busy} aria-describedby="ai-sharing" onChange={(e) => setConsent(e.target.checked)} />Confirmo que el contenido es ficticio o anonimizado y quiero enviarlo a Gemini.</label>
            {!!messages.length && <section className="ai-conversation" role="log" aria-live="polite" aria-relevant="additions" aria-label="Conversación con Gemini">
              {messages.map((item, index) => <article key={index} className={`ai-message ai-message-${item.role}`}>
                <strong>{item.role === "user" ? "Tú" : "Gemini"}</strong><p>{item.text}</p>
                {item.incomplete && <small>La respuesta quedó incompleta. Puedes pedir que continúe.</small>}
              </article>)}<span ref={lastMessageRef} />
            </section>}
            {busy && <p role="status">Gemini está preparando la respuesta…</p>}
            {error && <p ref={errorRef} tabIndex={-1} role="alert" className="mensaje-error">{error}</p>}
            <label htmlFor="graduate-ai-message">{messages.length ? "Tu respuesta o siguiente consulta" : "¿En qué quieres enfocarte? (opcional)"}</label>
            <textarea id="graduate-ai-message" rows={3} value={message} onChange={(e) => setMessage(e.target.value)}
              maxLength={5000} disabled={busy} required={!!messages.length} placeholder={mode === "presentacion" ? "Por ejemplo: ayúdame a explicar mejor mi proyecto académico." : "Por ejemplo: enfoquemos la práctica en preguntas técnicas."} />
            <div className="ai-actions">
              <button type="submit" className="boton boton-primario" disabled={busy || checking || !available || !consent}>{busy ? "Preparando…" : messages.length ? "Enviar" : mode === "presentacion" ? "Revisar presentación" : "Comenzar práctica"}<FiSend aria-hidden="true" /></button>
              {!!messages.length && <button className="text-link" type="button" disabled={busy} onClick={resetConversation}>Nueva conversación</button>}
            </div>
          </form>
          <p className="ai-help">Gemini puede equivocarse. Revisa sus sugerencias. El chat permanece solo mientras mantengas esta página abierta.</p>
        </div>
      </dialog>
    </>
  );
}
