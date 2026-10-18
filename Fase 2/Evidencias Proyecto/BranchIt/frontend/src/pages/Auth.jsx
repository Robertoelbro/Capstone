import { useState, useRef, useEffect } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { FiArrowRight, FiEye, FiEyeOff } from "react-icons/fi";
import { api } from "../api";
import { panelPath, useSession } from "../session";

import {
  ValidatedForm,
  SearchField,
  PhoneField,
  RutField,
} from "../Components/FormFields";
import { careers, industries } from "../data/catalogs";

export default function Auth() {
  const location = useLocation();
  const registering = location.pathname.startsWith("/registro");
  const [role, setRole] = useState(
    location.pathname.endsWith("/empresa") ? "empresa" : "egresado",
  );
  const [visible, setVisible] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const { user, login } = useSession();
  const navigate = useNavigate();
  const errorRef = useRef(null);
  useEffect(() => {
    if (error) errorRef.current?.focus();
  }, [error]);
  if (user) return <Navigate to={panelPath(user)} replace />;

  async function submit(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    setError("");
    if (registering && data.password !== data.confirm) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    if (new TextEncoder().encode(data.password).length > 72) {
      setError(
        "La contraseña es demasiado larga; utiliza como máximo 72 bytes.",
      );
      return;
    }
    setBusy(true);
    try {
      if (registering) {
        delete data.confirm;
        if (data.anio_egreso) data.anio_egreso = Number(data.anio_egreso);
        else delete data.anio_egreso;
        await (role === "empresa"
          ? api.registrarEmpresa(data)
          : api.registrarEgresado(data));
        navigate("/iniciar-sesion", {
          replace: true,
          state: { registered: true, email: data.email },
        });
      } else {
        const account = await login(data);
        navigate(panelPath(account), { replace: true });
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="auth-layout auth-layout-compact">
      <div className="auth-form-panel">
        <h1>{registering ? "Crear cuenta" : "Iniciar sesión"}</h1>
        {registering && (
          <div className="role-tabs" aria-label="Tipo de cuenta">
            <button
              type="button"
              aria-pressed={role === "egresado"}
              onClick={() => setRole("egresado")}
            >
              Soy egresado/a
            </button>
            <button
              type="button"
              aria-pressed={role === "empresa"}
              onClick={() => setRole("empresa")}
            >
              Soy empresa
            </button>
          </div>
        )}
        {!registering && location.state?.registered && (
          <p className="mensaje-exito" role="status">
            Tu cuenta está creada. Inicia sesión para continuar.
          </p>
        )}
        <ValidatedForm
          key={`${registering}-${role}`}
          onSubmit={submit}
          className="auth-form"
          aria-describedby={registering ? "register-help" : undefined}
          aria-busy={busy}
        >
          {registering && (
            <p id="register-help" className="muted">
              * Obligatorio. Contraseña: al menos 8 caracteres.
            </p>
          )}
          {registering &&
            (role === "egresado" ? (
              <>
                <div className="form-row">
                  <label>
                    Nombre
                    <input
                      name="nombre"
                      autoComplete="given-name"
                      required
                      maxLength={100}
                      placeholder="Tu nombre"
                    />
                  </label>
                  <label>
                    Apellido
                    <input
                      name="apellido"
                      autoComplete="family-name"
                      required
                      maxLength={100}
                      placeholder="Tu apellido"
                    />
                  </label>
                </div>
                <div className="form-row">
                  <SearchField
                    label="Carrera de egreso"
                    name="carrera"
                    options={careers}
                    required
                  />
                  <label>
                    Año de egreso <span>(opcional)</span>
                    <input
                      name="anio_egreso"
                      type="text"
                      inputMode="numeric"
                      pattern="(19|20)[0-9]{2}|2100"
                      maxLength={4}
                      placeholder="2026"
                    />
                  </label>
                </div>
              </>
            ) : (
              <>
                <label>
                  Nombre de la empresa
                  <input
                    name="nombre_empresa"
                    autoComplete="organization"
                    required
                    maxLength={150}
                    placeholder="Nombre de tu empresa"
                  />
                </label>
                <SearchField
                  label="Giro comercial"
                  name="rubro"
                  options={industries}
                  required
                />
              </>
            ))}
          {registering && (
            <>
              <div className="form-row">
                <RutField
                  label={
                    role === "empresa" ? "RUT de la empresa" : "RUT personal"
                  }
                />
                <PhoneField required />
              </div>
              <label>
                {role === "empresa"
                  ? "Fecha de creación de la empresa"
                  : "Fecha de nacimiento"}
                <input
                  key={role}
                  name="fecha_identidad"
                  autoComplete={role === "egresado" ? "bday" : "off"}
                  type="date"
                  required
                  max={new Date().toLocaleDateString("en-CA")}
                />
              </label>
            </>
          )}
          <label>
            Correo electrónico
            <input
              name="email"
              type="email"
              autoComplete="email"
              defaultValue={location.state?.email || ""}
              required
              maxLength={255}
              placeholder="nombre@correo.cl"
            />
          </label>
          <label>
            Contraseña
            <div className="password-field">
              <input
                name="password"
                type={visible ? "text" : "password"}
                autoComplete={registering ? "new-password" : "current-password"}
                minLength={registering ? 8 : 1}
                maxLength={72}
                required
                placeholder={
                  registering
                    ? "Al menos 8 caracteres"
                    : "Ingresa tu contraseña"
                }
              />
              <button
                type="button"
                aria-label={
                  visible ? "Ocultar contraseña" : "Mostrar contraseña"
                }
                aria-pressed={visible}
                onClick={() => setVisible(!visible)}
              >
                {visible ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>
          </label>
          {registering && (
            <label>
              Confirma tu contraseña
              <input
                name="confirm"
                type={visible ? "text" : "password"}
                autoComplete="new-password"
                minLength={8}
                maxLength={72}
                required
                placeholder="Repite tu contraseña"
              />
            </label>
          )}
          {error && (
            <p
              ref={errorRef}
              tabIndex={-1}
              className="mensaje-error"
              role="alert"
            >
              {error}
            </p>
          )}
          <button className="boton boton-primario auth-submit" disabled={busy}>
            {busy
              ? "Un momento…"
              : registering
              ? "Crear mi cuenta"
              : "Iniciar sesión"}
            <FiArrowRight />
          </button>
        </ValidatedForm>
        <p className="auth-switch">
          {registering
            ? "¿Ya tienes una cuenta?"
            : "¿Aún no tienes una cuenta?"}{" "}
          <Link to={registering ? "/iniciar-sesion" : "/registro"}>
            {registering ? "Inicia sesión" : "Regístrate gratis"}
          </Link>
        </p>
        <Link className="back-home" to="/">
          ← Volver a las ofertas
        </Link>
      </div>
    </section>
  );
}
