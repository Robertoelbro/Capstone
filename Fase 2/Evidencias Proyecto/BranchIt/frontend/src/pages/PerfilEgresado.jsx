import { useEffect, useState } from "react";
import { useSession } from "../session";
import { api } from "../api";
import WorkspaceNav from "../Components/WorkspaceNav";

const CAMPOS_VACIOS = {
  nombre: "",
  apellido: "",
  carrera: "",
  anio_egreso: "",
  presentacion: "",
  linkedin_url: "",
  foto_url: "",
};

export default function PerfilEgresado() {
  const { user } = useSession();
  const usuarioId = user.id;

  const [form, setForm] = useState(CAMPOS_VACIOS);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(false);
  const [savedPresentation, setSavedPresentation] = useState("");

  useEffect(() => {
    if (!usuarioId) {
      setError("Inicia sesión para continuar.");
      setCargando(false);
      return;
    }
    api
      .obtenerPerfilEgresado(usuarioId)
      .then((perfil) => {
        setSavedPresentation(perfil.presentacion || "");
        setForm({
          nombre: perfil.nombre || "",
          apellido: perfil.apellido || "",
          carrera: perfil.carrera || "",
          anio_egreso: perfil.anio_egreso || "",
          presentacion: perfil.presentacion || "",
          linkedin_url: perfil.linkedin_url || "",
          foto_url: perfil.foto_url || "",
        });
      })
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false));
  }, [usuarioId]);

  function actualizar(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
    setExito(false);
  }

  async function guardar(e) {
    e.preventDefault();
    setGuardando(true);
    setError(null);
    try {
      const datos = {
        ...form,
        anio_egreso: form.anio_egreso ? Number(form.anio_egreso) : null,
      };
      await api.actualizarPerfilEgresado(usuarioId, datos);
      setSavedPresentation(datos.presentacion);
      setExito(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardando(false);
    }
  }

  async function eliminarPresentacion() {
    if (
      !confirm(
        "¿Eliminar tu presentación? Tu cuenta y tus demás datos se conservarán.",
      )
    )
      return;
    setGuardando(true);
    setError(null);
    setExito(false);
    try {
      await api.eliminarPresentacion(usuarioId);
      setForm((value) => ({ ...value, presentacion: "" }));
      setSavedPresentation("");
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardando(false);
    }
  }

  if (cargando) return <p className="contenedor">Cargando perfil…</p>;

  return (
    <div className="contenedor" style={{ maxWidth: 560 }}>
      <WorkspaceNav />
      <h1>Mi presentación</h1>
      <p style={{ color: "var(--color-muted)" }}>
        Esta información es la que verán las empresas en tu perfil.
      </p>

      <form onSubmit={guardar} className="tarjeta">
        <fieldset disabled={guardando}>
          <div className="campo">
            <label htmlFor="nombre">Nombre</label>
            <input
              id="nombre"
              required
              maxLength={100}
              value={form.nombre}
              onChange={(e) => actualizar("nombre", e.target.value)}
            />
          </div>
          <div className="campo">
            <label htmlFor="apellido">Apellido</label>
            <input
              id="apellido"
              required
              maxLength={100}
              value={form.apellido}
              onChange={(e) => actualizar("apellido", e.target.value)}
            />
          </div>
          <div className="campo">
            <label htmlFor="carrera">Carrera</label>
            <input
              id="carrera"
              value={form.carrera}
              onChange={(e) => actualizar("carrera", e.target.value)}
            />
          </div>
          <div className="campo">
            <label htmlFor="anio">Año de egreso</label>
            <input
              id="anio"
              type="number"
              value={form.anio_egreso}
              onChange={(e) => actualizar("anio_egreso", e.target.value)}
            />
          </div>
          <div className="campo">
            <label htmlFor="presentacion">Presentación</label>
            <textarea
              id="presentacion"
              rows={4}
              maxLength={5000}
              value={form.presentacion}
              onChange={(e) => actualizar("presentacion", e.target.value)}
            />
          </div>
          <div className="campo">
            <label htmlFor="linkedin">LinkedIn</label>
            <input
              id="linkedin"
              type="url"
              maxLength={255}
              value={form.linkedin_url}
              onChange={(e) => actualizar("linkedin_url", e.target.value)}
            />
          </div>
          <div className="campo">
            <label htmlFor="foto">URL de foto</label>
            <input
              id="foto"
              type="url"
              maxLength={255}
              value={form.foto_url}
              onChange={(e) => actualizar("foto_url", e.target.value)}
            />
          </div>

          {error && <p className="mensaje-error">{error}</p>}
          {exito && <p className="mensaje-exito">Perfil actualizado.</p>}

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button
              type="submit"
              className="boton boton-primario"
              disabled={guardando}
            >
              {guardando ? "Guardando…" : "Guardar cambios"}
            </button>
            <button
              type="button"
              className="boton boton-peligro"
              onClick={eliminarPresentacion}
              disabled={!savedPresentation || guardando}
            >
              Eliminar presentación
            </button>
          </div>
        </fieldset>
      </form>
      <article className="tarjeta presentation-preview">
        <h2>Tu presentación guardada</h2>
        <p>
          {savedPresentation ||
            "Aún no has creado una presentación. Cuéntales a las empresas sobre tu formación y tus intereses."}
        </p>
      </article>
    </div>
  );
}
