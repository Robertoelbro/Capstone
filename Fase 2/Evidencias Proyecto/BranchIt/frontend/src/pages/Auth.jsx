import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import {
  FiArrowRight,
  FiBriefcase,
  FiCheck,
  FiEye,
  FiEyeOff,
  FiLayers,
} from "react-icons/fi";
import { api } from "../api";
import { panelPath, useSession } from "../session";

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
    <section className="auth-layout">
      <aside className="auth-story">
        <span className="eyebrow light">
          <FiLayers /> TU PRÓXIMO PASO EMPIEZA AQUÍ
        </span>
        <h1>
          Tu talento merece
          <br />
          su primera
          <br />
          <span>oportunidad.</span>
        </h1>
        <p>
          Conecta lo que aprendiste con lo que quieres llegar a ser. En
          BranchIT, tu carrera está por comenzar.
        </p>
        <div className="story-points">
          <p>
            <FiCheck /> Ofertas para dar tus primeros pasos
          </p>
          <p>
            <FiCheck /> Un perfil que muestra tu potencial
          </p>
          <p>
            <FiCheck /> Empresas que buscan talento nuevo
          </p>
        </div>
        <div className="story-note">
          <FiBriefcase size={24} />
          <div>
            <strong>Grandes carreras, pequeños comienzos.</strong>
            <span>Construye el tuyo con BranchIT.</span>
          </div>
        </div>
      </aside>
      <div className="auth-form-panel">
        <span className="eyebrow">
          {registering ? "EMPECEMOS" : "QUÉ BUENO VERTE DE NUEVO"}
        </span>
        <h2>{registering ? "Crea tu cuenta" : "Inicia sesión"}</h2>
        <p className="muted">
          {registering
            ? "Encuentra tu lugar en el mundo laboral."
            : "Continúa construyendo tu próximo paso profesional."}
        </p>
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
        <form onSubmit={submit} className="auth-form">
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
                  <label>
                    Carrera <span>(opcional)</span>
                    <input
                      name="carrera"
                      maxLength={150}
                      placeholder="Ej. Ingeniería en Informática"
                    />
                  </label>
                  <label>
                    Año de egreso <span>(opcional)</span>
                    <input
                      name="anio_egreso"
                      type="number"
                      min="1900"
                      max="2100"
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
                <label>
                  Rubro <span>(opcional)</span>
                  <input
                    name="rubro"
                    maxLength={150}
                    placeholder="Ej. Tecnología"
                  />
                </label>
              </>
            ))}
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
            <p className="mensaje-error" role="alert">
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
        </form>
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
