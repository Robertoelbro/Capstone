import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, setToken } from "../api";
import { useSession } from "../session";
import WorkspaceNav from "../Components/WorkspaceNav";
import { ValidatedForm } from "../Components/FormFields";
import "./Account.css";

export default function Account() {
  const { user, deactivate } = useSession();
  const navigate = useNavigate();
  const [passwordBusy, setPasswordBusy] = useState(false);
  const [deactivateBusy, setDeactivateBusy] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [deactivateError, setDeactivateError] = useState("");
  const [message, setMessage] = useState("");
  const passwordFeedback = useRef(null);
  const deactivateFeedback = useRef(null);
  useEffect(() => { if (passwordError || message) passwordFeedback.current?.focus(); }, [passwordError, message]);
  useEffect(() => { if (deactivateError) deactivateFeedback.current?.focus(); }, [deactivateError]);
  async function changePassword(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form));
    setPasswordError("");
    setMessage("");
    if (data.password !== data.confirm) {
      setPasswordError("Las contraseñas no coinciden.");
      return;
    }
    if (new TextEncoder().encode(data.password).length > 72) {
      setPasswordError("La contraseña admite un máximo de 72 bytes. Usa una más corta.");
      return;
    }
    setPasswordBusy(true);
    try {
      const session = await api.changePassword({ password_actual: data.password_actual, password: data.password });
      setToken(session.access_token);
      form.reset();
      setMessage("Contraseña actualizada. Las sesiones anteriores se cerraron; puedes continuar aquí.");
    } catch (err) {
      setPasswordError(err.message);
    } finally {
      setPasswordBusy(false);
    }
  }
  async function deactivateAccount(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const password = new FormData(form).get("password_actual");
    setDeactivateBusy(true);
    setDeactivateError("");
    try {
      await deactivate(password);
      navigate("/iniciar-sesion", { replace: true, state: { deactivated: true } });
    } catch (err) {
      setDeactivateError(err.message);
      form.querySelector('input[type="password"]')?.focus();
    } finally {
      setDeactivateBusy(false);
    }
  }
  return (
    <section className="contenedor dashboard account-page">
      <WorkspaceNav />
      <h1>Cuenta y seguridad</h1>
      <div className="account-grid">
        <ValidatedForm className="tarjeta auth-form" onSubmit={changePassword}>
          <h2>Cambiar contraseña</h2>
          <fieldset className="account-fields" disabled={passwordBusy || deactivateBusy}>
            <label htmlFor="account-current-password">Contraseña actual</label>
            <input id="account-current-password" name="password_actual" type="password" autoComplete="current-password" required maxLength={72} />
            <label htmlFor="account-new-password">Nueva contraseña</label>
            <input id="account-new-password" name="password" type="password" autoComplete="new-password" required minLength={8} maxLength={72} />
            <label htmlFor="account-confirm-password">Confirma la nueva contraseña</label>
            <input id="account-confirm-password" name="confirm" type="password" autoComplete="new-password" required minLength={8} maxLength={72} />
            {(passwordError || message) && <p ref={passwordFeedback} tabIndex={-1} role={passwordError ? "alert" : "status"} className={passwordError ? "mensaje-error" : "mensaje-exito"}>{passwordError || message}</p>}
            <button className="boton boton-primario" disabled={passwordBusy || deactivateBusy}>{passwordBusy ? "Actualizando…" : "Actualizar contraseña"}</button>
          </fieldset>
        </ValidatedForm>
        <ValidatedForm className="tarjeta auth-form account-deactivation" onSubmit={deactivateAccount}>
          <h2>Desactivar mi cuenta</h2>
          <p id="deactivate-consequences">Se cerrarán todas tus sesiones y no podrás iniciar sesión. {user.tipo === "empresa" ? "Tus ofertas se cerrarán y dejarán de recibir postulaciones." : "Tu portafolio dejará de ser público y no podrás enviar postulaciones."} Los datos se conservan; esto no elimina la cuenta ni incluye una reactivación automática.</p>
          <fieldset className="account-fields" disabled={deactivateBusy || passwordBusy}>
            <label htmlFor="deactivate-password">Contraseña actual</label>
            <input id="deactivate-password" name="password_actual" type="password" autoComplete="current-password" required maxLength={72} aria-describedby="deactivate-consequences" />
            <label className="consent"><input name="confirmar_desactivacion" type="checkbox" required />Confirmo que quiero desactivar mi cuenta.</label>
            {deactivateError && <p ref={deactivateFeedback} tabIndex={-1} role="alert" className="mensaje-error">{deactivateError}</p>}
            <button className="boton account-danger-button" disabled={deactivateBusy || passwordBusy}>{deactivateBusy ? "Desactivando…" : "Desactivar mi cuenta"}</button>
          </fieldset>
        </ValidatedForm>
      </div>
    </section>
  );
}
