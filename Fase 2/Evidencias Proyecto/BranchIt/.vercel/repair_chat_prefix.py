from pathlib import Path
import subprocess
p=Path('frontend/src/Components/GraduateAssistant.jsx')
current=p.read_text(encoding='utf8')
original=subprocess.check_output(['git','show','HEAD:Fase 2/Evidencias Proyecto/BranchIt/frontend/src/Components/GraduateAssistant.jsx']).decode('utf8')
head=original.rsplit('\n  return (',1)[0]
head=head.replace('FiSend, FiX','FiSend, FiX, FiEyeOff, FiPlus, FiChevronDown, FiChevronUp')
head=head.replace('  const [open, setOpen] = useState(false);','''  const [open, setOpen] = useState(false);
  const [hidden, setHidden] = useState(() => {
    try { return sessionStorage.getItem(`branchit-ai-hidden-${user.id}`) === "true"; }
    catch { return false; }
  });
  const [setupOpen, setSetupOpen] = useState(true);
  const [pendingText, setPendingText] = useState("");''')
head=head.replace('  const lastMessageRef = useRef(null);','''  const lastMessageRef = useRef(null);
  const messageRef = useRef(null);
  const sendingRef = useRef(false);''')
line='  useEffect(() => { if (open && messages.length) lastMessageRef.current?.scrollIntoView({block: "nearest"}); }, [messages.length, open]);'
assert line in head
head=head.replace(line,'''  useEffect(() => {
    if (open && (messages.length || busy)) lastMessageRef.current?.scrollIntoView({block: "nearest"});
  }, [messages.length, busy, open]);
  useEffect(() => {
    if (!busy && sendingRef.current) {
      sendingRef.current = false;
      if (open && !error) messageRef.current?.focus();
    }
  }, [busy, open, error]);
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
  }''')
head=head.replace('setMessages([]); setMessage(""); setError(""); setConsent(false);','setMessages([]); setMessage(""); setError(""); setConsent(false); setSetupOpen(true);')
head=head.replace('    const text = message.trim()', '''    if (mode === "presentacion" && !draft.trim()) { setSetupOpen(true); setError("Añade un borrador de tu presentación antes de enviarlo."); return; }
    if (mode === "entrevista" && !jobId) { setSetupOpen(true); setError("Selecciona una oferta antes de comenzar la práctica."); return; }
    const text = message.trim()''')
head=head.replace('    setBusy(true); setError("");','    sendingRef.current = true;\n    setBusy(true); setPendingText(text); setSetupOpen(false); setError("");')
head=head.replace('finally { setBusy(false); }','finally { setBusy(false); setPendingText(""); }')
body=current[current.index('    <>\n      {!hidden'):]
p.write_text(head+'\n  return (\n'+body,encoding='utf8')
