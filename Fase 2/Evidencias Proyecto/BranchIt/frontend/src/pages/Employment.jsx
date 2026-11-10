import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import WorkspaceNav from "../Components/WorkspaceNav";
import { ValidatedForm } from "../Components/FormFields";
import { Asset, UploadField } from "../Components/Media";
import "./Account.css";

function formValue(data) {
  return { situacion: data.situacion, busqueda_activa: data.busqueda_activa,
    empresa: data.empresa || "", cargo: data.cargo || "", fecha_inicio: data.fecha_inicio || "",
    postulacion_id: data.postulacion_id ? String(data.postulacion_id) : "" };
}
function dateLabel(value) {
  return value ? new Intl.DateTimeFormat("es-CL", { dateStyle: "long" }).format(new Date(`${value}T12:00:00`)) : "No registrada";
}
export default function Employment() {
  const [form, setForm] = useState(null), [saved, setSaved] = useState(null);
  const [applications, setApplications] = useState([]);
  const [busy, setBusy] = useState(false), [uploading, setUploading] = useState(false);
  const [releaseFile, setReleaseFile] = useState(null);
  const [error, setError] = useState(""), [message, setMessage] = useState("");
  const feedback = useRef(null);
  useEffect(() => {
    let active = true;
    Promise.all([api.employment(), api.myApplications()]).then(([data, items]) => {
      if (active) { setForm(formValue(data)); setSaved(data); setApplications(items); }
    }).catch((err) => { if (active) setError(err.message); });
    return () => { active = false; };
  }, []);
  useEffect(() => { if (error || message) feedback.current?.focus(); }, [error, message]);
  function update(key, value) { setMessage(""); setForm((previous) => ({ ...previous, [key]: value })); }
  async function save(event) {
    event.preventDefault();
    const formElement = event.currentTarget;
    setBusy(true); setError(""); setMessage("");
    try {
      const working = form.situacion === "trabajando";
      const result = await api.saveEmployment({ ...form,
        busqueda_activa: !working && form.busqueda_activa,
        empresa: working ? form.empresa.trim() || null : null,
        cargo: working ? form.cargo.trim() || null : null,
        fecha_inicio: working ? form.fecha_inicio || null : null,
        postulacion_id: working && form.postulacion_id ? Number(form.postulacion_id) : null });
      setSaved(result); setForm(formValue(result));
      const confirmation = formElement.elements.namedItem("confirmar_contratacion");
      if (confirmation) confirmation.checked = false;
      setMessage(result.puede_postular ? "Seguimiento guardado. Tu búsqueda está activa." : "Seguimiento guardado. Las nuevas postulaciones están bloqueadas.");
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  async function release(event) {
    event.preventDefault();
    if (!releaseFile || uploading) return;
    const data = Object.fromEntries(new FormData(event.currentTarget));
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await api.releaseEmployment({ archivo_id: releaseFile,
        fecha_fin: data.fecha_fin, motivo: data.motivo,
        ...(!saved.fecha_inicio ? { fecha_inicio: data.fecha_inicio } : {}) });
      setSaved(result); setForm(formValue(result)); setReleaseFile(null);
      setMessage(result.puede_postular ? "Finiquito registrado. Puedes volver a postular." : "Finiquito registrado. Alcanzaste el límite de un año de experiencia y no puedes enviar nuevas postulaciones.");
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }
  const today = new Date();
  const maxDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  return <section className="contenedor dashboard account-page">
    <WorkspaceNav /><h1>Mi seguimiento laboral</h1>
    <p className="muted">Tus antecedentes laborales y documentos son privados; no aparecen en el portafolio público.</p>
    {(error || message) && <p ref={feedback} tabIndex={-1} role={error ? "alert" : "status"} className={error ? "mensaje-error" : "mensaje-exito"}>{error || message}</p>}
    {!form && !error && <p role="status">Cargando seguimiento…</p>}
    {saved && form && <div className="account-grid"><div>
      {saved.requiere_finiquito ? <>
        <article className="tarjeta employment-summary"><h2>Contratación registrada</h2>
          <dl className="employment-details"><dt>Empresa</dt><dd>{saved.empresa || "No indicada"}</dd><dt>Cargo</dt><dd>{saved.cargo || "No indicado"}</dd><dt>Inicio</dt><dd>{dateLabel(saved.fecha_inicio)}</dd></dl>
          <p>Para revisar tu acceso a nuevas postulaciones, presenta el finiquito al terminar este empleo. Cambiar o reabrir una convocatoria no elimina esta contratación.</p>
        </article>
        <ValidatedForm className="tarjeta auth-form" onSubmit={release}><h2>Presentar finiquito</h2>
          <p>Demostración: se valida el formato PDF, no su autenticidad.</p>
          <fieldset className="account-fields" disabled={busy}>
            <UploadField kind="finiquito" label="Finiquito en PDF" value={releaseFile} onChange={setReleaseFile} onBusy={setUploading} />
            {!saved.fecha_inicio && <div className="campo"><label htmlFor="release-start">Fecha de inicio del empleo</label><input id="release-start" name="fecha_inicio" type="date" required max={maxDate} /></div>}
            <div className="campo"><label htmlFor="release-end">Fecha de término</label><input id="release-end" name="fecha_fin" type="date" required min={saved.fecha_inicio || undefined} max={maxDate} /></div>
            <div className="campo"><label htmlFor="release-reason">Motivo del término</label><select id="release-reason" name="motivo" required defaultValue=""><option value="" disabled>Selecciona un motivo</option><option value="renuncia">Renuncia</option><option value="despido">Despido</option></select></div>
            <label className="consent"><input type="checkbox" required />Confirmo el término de este empleo y la fecha indicada.</label>
            <button className="boton boton-primario" disabled={busy || uploading || !releaseFile}>{busy ? "Registrando…" : "Registrar finiquito"}</button>
          </fieldset>
        </ValidatedForm>
      </> : saved.limite_experiencia ? <article className="tarjeta"><h2>Límite de experiencia alcanzado</h2>
        <p>Alcanzaste un año de experiencia en la contratación registrada. No se habilitan nuevas postulaciones, incluso con una suscripción.</p>
        <p>Puedes conservar tu portafolio, consultar y compartir ofertas y seguir preparándote con IA.</p>
      </article> : <ValidatedForm className="tarjeta auth-form" onSubmit={save}><h2>Tu situación actual</h2>
        <fieldset className="account-fields" disabled={busy}>
          <label htmlFor="employment-status">Situación laboral</label><select id="employment-status" required value={form.situacion} onChange={(e) => { update("situacion", e.target.value); update("busqueda_activa", false); }}><option value="buscando">Buscando una oportunidad</option><option value="trabajando">Fui contratado y estoy trabajando</option></select>
          {form.situacion === "trabajando" ? <>
            <p className="employment-notice">Se bloquearán nuevas postulaciones hasta presentar un finiquito. Si el empleo alcanza un año, el bloqueo será permanente.</p>
            <div className="campo"><label htmlFor="employment-company">Empresa (opcional)</label><input id="employment-company" maxLength={150} value={form.empresa} onChange={(e) => update("empresa", e.target.value)} /></div>
            <div className="campo"><label htmlFor="employment-role">Cargo (opcional)</label><input id="employment-role" maxLength={150} value={form.cargo} onChange={(e) => update("cargo", e.target.value)} /></div>
            <div className="campo"><label htmlFor="employment-date">Fecha de inicio</label><input id="employment-date" type="date" required max={maxDate} value={form.fecha_inicio} onChange={(e) => update("fecha_inicio", e.target.value)} /></div>
            <div className="campo"><label htmlFor="employment-application">Vincular una postulación (opcional)</label><select id="employment-application" value={form.postulacion_id} onChange={(e) => update("postulacion_id", e.target.value)}><option value="">Sin vincular; también puede ser un empleo externo</option>{applications.map((item) => <option key={item.id} value={item.id}>{item.titulo} · {item.nombre_empresa}</option>)}</select></div>
            <label className="consent"><input name="confirmar_contratacion" type="checkbox" required />Confirmo esta contratación y entiendo el bloqueo de nuevas postulaciones.</label>
          </> : <label className="consent"><input type="checkbox" checked={form.busqueda_activa} onChange={(e) => update("busqueda_activa", e.target.checked)} />Mantener activa mi búsqueda y permitir nuevas postulaciones</label>}
          <button className="boton boton-primario" disabled={busy}>{busy ? "Guardando…" : "Guardar seguimiento"}</button>
        </fieldset>
      </ValidatedForm>}
    </div><aside className="tarjeta employment-summary"><h2>Mi acceso</h2>
      <p className="employment-state">{saved.puede_postular ? "Puedes postular" : "Nuevas postulaciones bloqueadas"}</p>
      <p>Antes de un año de experiencia, registrar el finiquito permite volver a postular. Al alcanzar un año se mantiene el bloqueo.</p>
      {saved.finiquito_id && <Asset id={saved.finiquito_id} type="document" label="Ver documento presentado" />}
      <div className="employment-links"><Link to="/ofertas">Consultar ofertas</Link><Link to="/mis-postulaciones">Mis postulaciones</Link></div>
    </aside></div>}
  </section>;
}
