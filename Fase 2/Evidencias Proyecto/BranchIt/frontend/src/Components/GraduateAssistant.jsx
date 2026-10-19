import { useEffect, useRef, useState } from "react";
import { FiArrowUpRight, FiMessageCircle, FiSend, FiX, FiEyeOff, FiPlus, FiChevronDown, FiChevronUp } from "react-icons/fi";
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
  const [hidden, setHidden] = useState(() => {
    try { return sessionStorage.getItem(`branchit-ai-hidden-${user.id}`) === "true"; }
    catch { return false; }
  });
  const [setupOpen, setSetupOpen] = useState(true);
  const [pendingText, setPendingText] = useState("");
  const [mode, setMode] = useState("presentacion");
  const [draft, setDraft] = useState("");
  const [message, setMessage] = useState("");
  const [jobId, setJobId] = useState("");
  const [jobs, setJobs] = useState([]);
  const [profile, setProfile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [consent, setConsent] = useState(false);
  const [available, setAvailable] = useState(false);
  const [dailyInterview, setDailyInterview] = useState(null);
  const [interviewId, setInterviewId] = useState(null);
  const [checking, setChecking] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [contextError, setContextError] = useState("");
  const dialogRef = useRef(null);
  const launcherRef = useRef(null);
  const titleRef = useRef(null);
  const errorRef = useRef(null);
  const lastMessageRef = useRef(null);
  const messageRef = useRef(null);
  const sendingRef = useRef(false);

  useEffect(() => {
    if (!open) return;
    let alive = true;
    setChecking(true);
    setContextError("");
    Promise.allSettled([api.assistantStatus(), api.jobs(), api.obtenerPerfilEgresado(user.id)]).then(([status, offers, account]) => {
      if (!alive) return;
      if (status.status === "fulfilled") { setAvailable(status.value.disponible); setDailyInterview(status.value.entrevista_hoy); }
      else { setAvailable(false); setContextError(status.reason.message); }
      if (offers.status === "fulfilled") setJobs(offers.value);
      else setContextError((e) => e || offers.reason.message);
      if (account.status === "fulfilled") setProfile(account.value);
      setChecking(false);
    });
    return () => { alive = false; };
  }, [open, user.id]);
  useEffect(() => { if (error) errorRef.current?.focus(); }, [error]);
  useEffect(() => {
    if (open && (messages.length || busy)) lastMessageRef.current?.scrollIntoView({block: "nearest"});
  }, [messages.length, busy, open]);
  useEffect(() => {
    if (!busy && sendingRef.current) {
      sendingRef.current = false;
      if (open && !error) messageRef.current?.focus();
    }
  }, [busy, open, error]);
  useEffect(() => {
    function fromNavigation(event) {
      if (event.detail?.ofertaId && !sendingRef.current) {
        setMode('postulacion'); setJobId(String(event.detail.ofertaId));
        setMessages([]); setMessage(''); setError(''); setConsent(false); setSetupOpen(true); setInterviewId(null);
      }
      setHidden(false);
      try { sessionStorage.removeItem(`branchit-ai-hidden-${user.id}`); } catch { /* Storage may be unavailable. */ }
      if (!dialogRef.current.open) dialogRef.current.showModal();
      setOpen(true);
      titleRef.current.focus();
    }
    window.addEventListener("branchit-open-ai", fromNavigation);
    return () => window.removeEventListener("branchit-open-ai", fromNavigation);
  }, [user.id]);

  function hideAssistant() {
    setHidden(true);
    try { sessionStorage.setItem(`branchit-ai-hidden-${user.id}`, "true"); } catch { /* Keep the preference in memory. */ }
    if (dialogRef.current.open) dialogRef.current.close();
    document.getElementById("graduate-ai-nav")?.focus();
  }

  function showAssistant() {
    dialogRef.current.showModal();
    setOpen(true);
    titleRef.current.focus();
  }
  function resetConversation() {
    setMessages([]); setMessage(""); setError(""); setConsent(false); setSetupOpen(true); setInterviewId(null);
  }
  function resumeInterview() {
    setMode('entrevista'); setJobId(String(dailyInterview.oferta_id));
    setInterviewId(dailyInterview.id); setMessages(dailyInterview.historial);
    setError(''); setMessage(''); setConsent(false); setSetupOpen(false);
  }
  function changeMode(value) {
    if (value === mode) return;
    setMode(value);
    resetConversation();
  }
  async function submit(event) {
    event.preventDefault();
    if (busy || checking || !available || !consent) return;
    if (mode === "presentacion" && !draft.trim()) { setSetupOpen(true); setError("Añade un borrador de tu presentación antes de enviarlo."); return; }
    if (mode !== "presentacion" && !jobId) { setSetupOpen(true); setError("Selecciona una oferta antes de comenzar."); return; }
    if (mode === 'entrevista' && dailyInterview && (!interviewId || dailyInterview.finalizada)) {
      setError('Ya utilizaste tu entrevista diaria. Retoma la de hoy o vuelve mañana, según la hora de Santiago.'); return;
    }
    const text = message.trim() || (mode === "presentacion"
      ? "Revisa mi presentación y propón una versión mejorada sin inventar antecedentes."
      : mode === 'postulacion' ? '¿Qué necesito para postular a esta oferta y cómo puedo prepararme?'
      : "Comencemos una entrevista de práctica para esta oferta. Hazme la primera pregunta.");
    if (messages.length && !message.trim()) return;
    sendingRef.current = true;
    setBusy(true); setPendingText(text); setSetupOpen(false); setError("");
    try {
      const result = await api.assistantChat({modo: mode, mensaje: text,
        borrador: mode === "presentacion" ? draft : "",
        oferta_id: mode !== "presentacion" ? Number(jobId) : null,
        entrevista_id: mode === 'entrevista' ? interviewId : null,
        historial: messages.slice(-20).map(({role, text}) => ({role, text})),
        contenido_anonimo: true});
      setMessages((previous) => [...previous, {role: "user", text},
        {role: "model", text: result.respuesta, incomplete: result.incompleta, recursos: result.recursos_certificacion || []}]);
      if (result.entrevista) { setInterviewId(result.entrevista.id); setDailyInterview(result.entrevista); }
      setMessage("");
    } catch (err) {
      setError(err.message);
      if (mode === 'entrevista') {
        try { const status = await api.assistantStatus(); setDailyInterview(status.entrevista_hoy); } catch { /* Keep original error. */ }
      }
    }
    finally { setBusy(false); setPendingText(""); }
  }

  return (
    <>
      {!hidden && <div className="ai-launcher-group">
        <button ref={launcherRef} className="ai-launcher" type="button" aria-haspopup="dialog"
          aria-expanded={open} aria-controls="graduate-ai-dialog" onClick={showAssistant}>
          <span className="ai-launcher-icon" aria-hidden="true"><FiMessageCircle /></span>
          <span><strong>Modo IA</strong></span>
          <FiArrowUpRight aria-hidden="true" />
        </button>
        <button type="button" className="ai-hide-launcher" onClick={hideAssistant} aria-label="Ocultar botón Modo IA" title="Ocultar; puedes abrir Modo IA desde el menú"><FiEyeOff aria-hidden="true" /></button>
      </div>}
      <dialog ref={dialogRef} id="graduate-ai-dialog" className="ai-dialog" aria-labelledby="graduate-ai-title"
        aria-describedby="graduate-ai-status" onClose={() => {
          setOpen(false);
          (launcherRef.current || document.getElementById("graduate-ai-nav"))?.focus();
        }}>
        <div className="ai-chat-shell">
          <header className="ai-dialog-header">
            <div className="ai-heading"><span className="ai-heading-icon" aria-hidden="true"><FiMessageCircle /></span><div>
              <h2 id="graduate-ai-title" ref={titleRef} tabIndex={-1}>Modo IA <span aria-hidden="true">✦</span></h2>
              <p id="graduate-ai-status" role="status" className="ai-availability">{checking ? "Comprobando disponibilidad…" : available ? "Gemini habilitado" : "Conexión pendiente con Gemini"}</p>
            </div></div>
            <div className="ai-header-actions">
              <button className="ai-icon-button" type="button" disabled={busy} onClick={resetConversation} aria-label="Nueva conversación" title="Nueva conversación"><FiPlus aria-hidden="true" /></button>
              <button className="ai-icon-button" type="button" onClick={hideAssistant} aria-label="Ocultar Modo IA y su botón" title="Ocultar; abre desde el menú"><FiEyeOff aria-hidden="true" /></button>
              <button className="ai-icon-button" type="button" onClick={() => dialogRef.current.close()} aria-label="Minimizar conversación" title="Minimizar conversación"><FiX aria-hidden="true" /></button>
            </div>
          </header>
          <form className="ai-chat-form" onSubmit={submit} noValidate>
            <div className="ai-chat-scroll">
              {contextError && <p className="mensaje-error" role="alert">{contextError}</p>}
              <div className="ai-mode-tabs" aria-label="Tipo de orientación">
                <button type="button" aria-pressed={mode === "presentacion"} disabled={busy} onClick={() => changeMode("presentacion")}>Mi presentación</button>
                <button type="button" aria-pressed={mode === "entrevista"} disabled={busy} onClick={() => changeMode("entrevista")}>Entrevista de práctica</button>
                <button type="button" aria-pressed={mode === "postulacion"} disabled={busy} onClick={() => changeMode("postulacion")}>Preparar postulación</button>
              </div>
              {mode === 'entrevista' && <div className="ai-daily-limit" role="status">
                <strong>1 entrevista por día</strong>
                <p>5 preguntas y una devolución final. Se renueva al cambiar el día en Santiago. Puedes retomarla hoy; un fallo de Gemini no consume tu práctica.</p>
                {dailyInterview && <p>{dailyInterview.finalizada ? 'Ya completaste la entrevista de hoy. Mañana tendrás otra disponible.' : `Entrevista de hoy iniciada · ${dailyInterview.turnos}/6 turnos.`}</p>}
                {dailyInterview && !interviewId && !dailyInterview.finalizada && <button type="button" className="ai-text-button" disabled={busy} onClick={resumeInterview}>Retomar entrevista de hoy</button>}
              </div>}
              {!messages.length && !busy && <div className="ai-chat-welcome"><span aria-hidden="true">❧</span><h3>¿Qué preparamos hoy?</h3></div>}
              <div className="ai-context">
                <button type="button" className="ai-context-toggle" disabled={busy} aria-expanded={setupOpen} aria-controls="ai-context-fields" onClick={() => setSetupOpen(!setupOpen)}>
                  <span>{mode === "presentacion" ? "Borrador de presentación" : jobs.find((job) => String(job.id) === jobId)?.titulo || "Selecciona una oferta"}</span>{setupOpen ? <FiChevronUp aria-hidden="true" /> : <FiChevronDown aria-hidden="true" />}
                </button>
                <div id="ai-context-fields" hidden={!setupOpen} className="ai-context-fields">
                  {mode === "presentacion" ? <>
                    <label htmlFor="ai-draft">Tu presentación sin datos personales</label>
                    <textarea id="ai-draft" rows={4} value={draft} required maxLength={5000} disabled={busy} aria-describedby="ai-draft-help"
                      onChange={(e) => {setDraft(e.target.value); resetConversation();}} placeholder="Soy egresado de Informática y desarrollé un proyecto con Python…" />
                    <p id="ai-draft-help" className="ai-help">Revísala antes de enviarla. Las sugerencias no cambian tu perfil. Editar el borrador inicia una nueva conversación.</p>
                    {profile?.presentacion && <button className="ai-text-button" type="button" disabled={busy} onClick={() => {setDraft(anonymousDraft(profile)); resetConversation();}}>Usar mi presentación como borrador</button>}
                  </> : <>
                    <label htmlFor="ai-job">Elige una oferta activa</label>
                    <select id="ai-job" value={jobId} required disabled={busy || checking || (mode === 'entrevista' && !!interviewId)} onChange={(e) => {setJobId(e.target.value); resetConversation();}}>
                      <option value="">Selecciona una oferta</option>
                      {jobs.map((job) => <option key={job.id} value={job.id}>{job.titulo} · {job.nombre_empresa}</option>)}
                    </select>
                    <p className="ai-help">{!checking && !jobs.length ? "No hay ofertas disponibles en este momento." : mode === 'postulacion' ? 'Consulta requisitos, qué habilidades reforzar y dónde obtener certificaciones.' : "Recibirás una pregunta por turno y comentarios para mejorar. Es una práctica, no una entrevista con la empresa."}</p>
                    {mode === 'postulacion' && <button type="button" className="ai-text-button" disabled={busy} onClick={() => {setMessage('Recomiéndame sitios gratuitos para obtener certificaciones que me ayuden a prepararme para esta oferta. Distingue qué credencial obtendría y qué habilidad reforzaría.'); messageRef.current?.focus();}}>Pedir sitios para certificarme</button>}
                  </>}
                </div>
              </div>
              <section className="ai-conversation" role="log" aria-live="polite" aria-relevant="additions" aria-label="Conversación con Gemini">
                {messages.map((item, index) => <article key={index} className={`ai-message ai-message-${item.role}`}>
                  <strong>{item.role === "user" ? "Tú" : "BranchIT · Gemini"}</strong><p>{item.text}</p>
                  {item.incomplete && <small>La respuesta quedó incompleta. Puedes pedir que continúe.</small>}
                  {item.recursos?.length > 0 && <details className="ai-certification-resources">
                    <summary>Sitios para certificarte · {item.recursos.length} opciones</summary>
                    <ul>{item.recursos.map(resource => <li key={resource.url}>
                      <a href={resource.url} target="_blank" rel="noopener noreferrer">{resource.nombre} ↗<span className="sr-only"> (abre en otra pestaña)</span></a>
                      <p>{resource.motivo}</p>
                      <small>Curso: {resource.curso}. {resource.credencial}.</small>
                      <small>{resource.nota}</small>
                    </li>)}</ul>
                    <small>Revisión de referencias: {item.recursos[0].revision}. Confirma las condiciones en el sitio antes de inscribirte.</small>
                  </details>}
                </article>)}
                {busy && <><article className="ai-message ai-message-user"><strong>Tú</strong><p>{pendingText}</p></article>
                  <article className="ai-message ai-message-model"><strong>BranchIT · Gemini</strong><p role="status" className="ai-thinking">Preparando una respuesta…</p></article></>}
                <span ref={lastMessageRef} />
              </section>
            </div>
            <footer className="ai-chat-composer">
              {error && <p ref={errorRef} tabIndex={-1} role="alert" className="mensaje-error">{error}</p>}
              <details className="ai-privacy"><summary>Antes de conversar · privacidad</summary><p id="ai-sharing">Google recibirá el texto y la conversación y, al consultar una oferta o practicar entrevistas, su contenido. La entrevista se guarda cifrada en BranchIT para retomarla y controlar el uso diario. El servicio gratuito puede usar lo enviado para mejorar sus productos. Usa únicamente texto ficticio o anonimizado, sin nombres, contactos ni información confidencial. Revisa el borrador incluso después de copiarlo.</p></details>
              <label className="ai-consent"><input type="checkbox" checked={consent} required disabled={busy} onChange={(e) => setConsent(e.target.checked)} />Confirmo que el contenido es ficticio o anonimizado y quiero enviarlo a Gemini.</label>
              <label className="sr-only" htmlFor="graduate-ai-message">{messages.length ? "Tu mensaje" : "Tu consulta opcional"}</label>
              <div className="ai-input-box">
                <textarea ref={messageRef} id="graduate-ai-message" rows={2} value={message} onChange={(e) => setMessage(e.target.value)} maxLength={5000} disabled={busy}
                  aria-describedby="ai-keyboard-help" onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                      event.preventDefault(); event.currentTarget.form.requestSubmit();
                    }
                  }}
                  placeholder={messages.length ? "Escribe tu mensaje…" : mode === "presentacion" ? "¿En qué quieres mejorar? (opcional)" : "¿Qué te gustaría practicar? (opcional)"} />
                <button type="submit" className="ai-send" disabled={busy || checking || !available || !consent || (!!messages.length && !message.trim()) || (mode === 'entrevista' && !!dailyInterview && (!interviewId || dailyInterview.finalizada))}
                  aria-label={messages.length ? "Enviar mensaje" : mode === "presentacion" ? "Revisar presentación" : mode === 'postulacion' ? 'Consultar requisitos' : "Comenzar entrevista"} title={messages.length ? "Enviar mensaje" : "Comenzar conversación"}><FiSend aria-hidden="true" /></button>
              </div>
              <p className="ai-composer-note">{!messages.length ? "Pulsa enviar para comenzar. " : ""}Gemini puede equivocarse. Revisa sus sugerencias.</p>
              <span id="ai-keyboard-help" className="sr-only">Enter para enviar. Mayúsculas y Enter para añadir una línea.</span>
            </footer>
          </form>
        </div>
      </dialog>
    </>
  );
}
