from pathlib import Path
p=Path('frontend/src/Components/GraduateAssistant.jsx');s=p.read_text(encoding='utf8');s=s.replace('FiSend, FiX','FiSend, FiX, FiEyeOff, FiPlus, FiChevronDown, FiChevronUp');s=s.replace('  const [open, setOpen] = useState(false);','''  const [open, setOpen] = useState(false);
  const [hidden, setHidden] = useState(() => {
    try { return sessionStorage.getItem(`branchit-ai-hidden-${user.id}`) === "true"; }
    catch { return false; }
  });
  const [setupOpen, setSetupOpen] = useState(true);
  const [pendingText, setPendingText] = useState("");''');s=s.replace('  useEffect(() => { if (open && messages.length) lastMessageRef.current?.scrollIntoView({block: "nearest"}); }, [messages.length, open]);','''  useEffect(() => {
    if (open && (messages.length || busy)) lastMessageRef.current?.scrollIntoView({block: "nearest"});
  }, [messages.length, busy, open]);
  useEffect(() => {
    function fromNavigation() {
      setHidden(false);
      try { sessionStorage.removeItem(`branchit-ai-hidden-${user.id}`); } catch { /* Storage may be unavailable. */ }
      dialogRef.current.showModal();
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
  }''');s=s.replace('setMessages([]); setMessage(""); setError(""); setConsent(false);','setMessages([]); setMessage(""); setError(""); setConsent(false); setSetupOpen(true);');s=s.replace('    const text = message.trim()', '''    if (mode === "presentacion" && !draft.trim()) { setSetupOpen(true); setError("Añade un borrador de tu presentación antes de enviarlo."); return; }
    if (mode === "entrevista" && !jobId) { setSetupOpen(true); setError("Selecciona una oferta antes de comenzar la práctica."); return; }
    const text = message.trim()''');s=s.replace('    setBusy(true); setError("");','    setBusy(true); setPendingText(text); setSetupOpen(false); setError("");');s=s.replace('finally { setBusy(false); }','finally { setBusy(false); setPendingText(""); }');s=s[:s.index('  return (')]+'''  return (
    <>
      {!hidden && <div className="ai-launcher-group">
        <button ref={launcherRef} className="ai-launcher" type="button" aria-haspopup="dialog"
          aria-expanded={open} aria-controls="graduate-ai-dialog" onClick={showAssistant}>
          <span className="ai-launcher-icon" aria-hidden="true"><FiMessageCircle /></span>
          <span><strong>Modo IA</strong><small>Tu próximo impulso</small></span>
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
              <p id="graduate-ai-status" role="status" className="ai-availability">{checking ? "Conectando…" : available ? "Gemini · Tu espacio para crecer" : "Conexión pendiente con Gemini"}</p>
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
              </div>
              {!messages.length && !busy && <div className="ai-chat-welcome"><span aria-hidden="true">❧</span><h3>¿Qué preparamos hoy?</h3><p>{mode === "presentacion" ? "Démosle forma a lo que quieres contar de ti." : "Practiquemos tu próximo paso, una pregunta a la vez."}</p></div>}
              <div className="ai-context">
                <button type="button" className="ai-context-toggle" disabled={busy} aria-expanded={setupOpen} aria-controls="ai-context-fields" onClick={() => setSetupOpen(!setupOpen)}>
                  <span>{mode === "presentacion" ? "Borrador de presentación" : "Oferta seleccionada"}</span>{setupOpen ? <FiChevronUp aria-hidden="true" /> : <FiChevronDown aria-hidden="true" />}
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
                    <select id="ai-job" value={jobId} required disabled={busy || checking} onChange={(e) => {setJobId(e.target.value); resetConversation();}}>
                      <option value="">Selecciona una oferta</option>
                      {jobs.map((job) => <option key={job.id} value={job.id}>{job.titulo} · {job.nombre_empresa}</option>)}
                    </select>
                    <p className="ai-help">{!checking && !jobs.length ? "No hay ofertas disponibles en este momento." : "Recibirás una pregunta por turno y comentarios para mejorar. Es una práctica, no una entrevista con la empresa."}</p>
                  </>}
                </div>
              </div>
              <section className="ai-conversation" role="log" aria-live="polite" aria-relevant="additions" aria-label="Conversación con Gemini">
                {messages.map((item, index) => <article key={index} className={`ai-message ai-message-${item.role}`}>
                  <strong>{item.role === "user" ? "Tú" : "BranchIT · Gemini"}</strong><p>{item.text}</p>
                  {item.incomplete && <small>La respuesta quedó incompleta. Puedes pedir que continúe.</small>}
                </article>)}
                {busy && <><article className="ai-message ai-message-user"><strong>Tú</strong><p>{pendingText}</p></article>
                  <article className="ai-message ai-message-model"><strong>BranchIT · Gemini</strong><p role="status" className="ai-thinking">Preparando una respuesta…</p></article></>}
                <span ref={lastMessageRef} />
              </section>
            </div>
            <footer className="ai-chat-composer">
              {error && <p ref={errorRef} tabIndex={-1} role="alert" className="mensaje-error">{error}</p>}
              <details className="ai-privacy"><summary>Antes de conversar · privacidad</summary><p id="ai-sharing">Google recibirá el texto y la conversación y, al practicar entrevistas, el contenido de la oferta. El servicio gratuito puede usar lo enviado para mejorar sus productos. Usa únicamente texto ficticio o anonimizado, sin nombres, contactos ni información confidencial. Revisa el borrador incluso después de copiarlo.</p></details>
              <label className="ai-consent"><input type="checkbox" checked={consent} required disabled={busy} onChange={(e) => setConsent(e.target.checked)} />Confirmo que el contenido es ficticio o anonimizado y quiero enviarlo a Gemini.</label>
              <label className="sr-only" htmlFor="graduate-ai-message">{messages.length ? "Tu mensaje" : "Tu consulta opcional"}</label>
              <div className="ai-input-box">
                <textarea id="graduate-ai-message" rows={2} value={message} onChange={(e) => setMessage(e.target.value)} maxLength={5000} disabled={busy}
                  placeholder={messages.length ? "Escribe tu mensaje…" : mode === "presentacion" ? "¿En qué quieres mejorar? (opcional)" : "¿Qué te gustaría practicar? (opcional)"} />
                <button type="submit" className="ai-send" disabled={busy || checking || !available || !consent}
                  aria-label={messages.length ? "Enviar mensaje" : mode === "presentacion" ? "Revisar presentación" : "Comenzar entrevista"} title={messages.length ? "Enviar mensaje" : "Comenzar conversación"}><FiSend aria-hidden="true" /></button>
              </div>
              <p className="ai-composer-note">{!messages.length ? "Pulsa enviar para comenzar. " : ""}Gemini puede equivocarse. Revisa sus sugerencias.</p>
            </footer>
          </form>
        </div>
      </dialog>
    </>
  );
}
''';p.write_text(s,encoding='utf8')
p=Path('frontend/src/Components/Header/Header.jsx');s=p.read_text(encoding='utf8');s=s.replace('<NavLink to={panelPath(user)}>Mi panel</NavLink>','''<NavLink to={panelPath(user)}>Mi panel</NavLink>
              {user.tipo === "egresado" && <button id="graduate-ai-nav" type="button" className="nav-ai-button" onClick={() => window.dispatchEvent(new Event("branchit-open-ai"))}>Modo IA</button>}''');p.write_text(s,encoding='utf8')
