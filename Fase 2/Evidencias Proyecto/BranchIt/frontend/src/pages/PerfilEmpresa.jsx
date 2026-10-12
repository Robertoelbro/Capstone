import { useEffect, useState } from "react";
import { api, setToken } from "../api";
import { useSession } from "../session";
import WorkspaceNav from "../Components/WorkspaceNav";
import { Asset, UploadField } from "../Components/Media";
import MediaLibrary from "../Components/MediaLibrary";

export default function PerfilEmpresa() {
  const { user } = useSession();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [passwordBusy, setPasswordBusy] = useState(false);
  useEffect(() => {
    let alive = true;
    api.companyProfile(user.id).then((data) => {
      if (alive) setProfile(data);
    }).catch((e) => { if (alive) setError(e.message); });
    return () => { alive = false; };
  }, [user.id]);
  async function save(event) {
    event.preventDefault();
    setBusy(true); setError(""); setMessage("");
    try {
      setProfile(await api.saveCompanyProfile(user.id, {
        nombre_empresa: profile.nombre_empresa,
        descripcion: profile.descripcion || "",
        foto_id: profile.foto_id || null,
      }));
      setMessage("La información de tu empresa está actualizada.");
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function changePassword(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    setPasswordError(""); setPasswordMessage("");
    if (data.password !== data.confirm) {
      setPasswordError("Las contraseñas no coinciden."); return;
    }
    delete data.confirm;
    setPasswordBusy(true);
    try {
      const session = await api.changePassword(data);
      setToken(session.access_token);
      form.reset();
      setPasswordMessage("Contraseña actualizada. Las sesiones anteriores se cerraron; puedes continuar aquí.");
    } catch (e) { setPasswordError(e.message); }
    finally { setPasswordBusy(false); }
  }
  return (
    <section className="contenedor dashboard company-profile">
      <WorkspaceNav />
      <div className="dashboard-heading">
        <span className="eyebrow">LAS RAÍCES DE TU EMPRESA</span>
        <h1>Mi empresa</h1>
        <p className="muted">Cuenta quiénes son y qué quieren construir con nuevos talentos.</p>
      </div>
      {error && <p className="mensaje-error" role="alert">{error}</p>}
      {!profile && !error && <p role="status">Cargando tu empresa…</p>}
      {profile && <div className="company-profile-grid">
        <form className="tarjeta auth-form" onSubmit={save}>
          <h2>Presentación de la empresa</h2>
          <div className="company-photo">
            {profile.foto_id ? <Asset id={profile.foto_id} alt={`Foto de ${profile.nombre_empresa}`} /> : <span aria-label="Sin foto">✿</span>}
          </div>
          <UploadField kind="foto" label="Foto o logo de la empresa" value={profile.foto_id} onBusy={setUploading}
            onChange={(foto_id) => setProfile((p) => ({ ...p, foto_id }))} />
          <label>Nombre de la empresa
            <input required maxLength={150} value={profile.nombre_empresa} onChange={(e) => setProfile({ ...profile, nombre_empresa: e.target.value })} />
          </label>
          <label>Resumen de empresa
            <textarea rows={6} maxLength={5000} value={profile.descripcion || ""} onChange={(e) => setProfile({ ...profile, descripcion: e.target.value })} placeholder="Qué hacen, qué los inspira y cómo es trabajar con ustedes…" />
          </label>
          <p className="muted">Giro comercial: {profile.rubro || "Sin información"}</p>
          {message && <p className="mensaje-exito" role="status">{message}</p>}
          <button className="boton boton-primario" disabled={busy || uploading}>{busy ? "Guardando…" : "Guardar información"}</button>
          <MediaLibrary />
        </form>
        <form className="tarjeta auth-form" onSubmit={changePassword}>
          <h2>Cambiar contraseña</h2>
          <p className="muted">Confirma tu contraseña actual para proteger el acceso a tu empresa.</p>
          <label>Contraseña actual<input name="password_actual" type="password" autoComplete="current-password" required maxLength={72} /></label>
          <label>Nueva contraseña<input name="password" type="password" autoComplete="new-password" required minLength={8} maxLength={72} /></label>
          <label>Confirma la nueva contraseña<input name="confirm" type="password" autoComplete="new-password" required minLength={8} maxLength={72} /></label>
          {passwordError && <p className="mensaje-error" role="alert">{passwordError}</p>}
          {passwordMessage && <p className="mensaje-exito" role="status">{passwordMessage}</p>}
          <button className="boton boton-secundario" disabled={passwordBusy}>{passwordBusy ? "Actualizando…" : "Actualizar contraseña"}</button>
        </form>
      </div>}
    </section>
  );
}
