import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";

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
  const [params] = useSearchParams();
  const usuarioId = params.get("usuario_id");

  const [form, setForm] = useState(CAMPOS_VACIOS);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState(null);
  const [exito, setExito] = useState(false);

  useEffect(() => {
    if (!usuarioId) {
      setError("Falta indicar tu usuario (usuario_id) en la URL.");
      setCargando(false);
      return;
    }
    api
      .obtenerPerfilEgresado(usuarioId)
      .then((perfil) =>
        setForm({
          nombre: perfil.nombre || "",
          apellido: perfil.apellido || "",
          carrera: perfil.carrera || "",
          anio_egreso: perfil.anio_egreso || "",
          presentacion: perfil.presentacion || "",
          linkedin_url: perfil.linkedin_url || "",
          foto_url: perfil.foto_url || "",
        })
      )
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
      setExito(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardando(false);
    }
  }

  async function eliminarCuenta() {
    if (!confirm("¿Eliminar tu cuenta de forma permanente?")) return;
    try {
      await api.eliminarCuentaEgresado(usuarioId);
      window.location.href = "/";
    } catch (err) {
      setError(err.message);
    }
  }

  if (cargando) return <p className="contenedor">Cargando perfil…</p>;

  return (
    <div className="contenedor" style={{ maxWidth: 560 }}>
      <h1>Mi presentación</h1>
      <p style={{ color: "var(--color-muted)" }}>
        Esta información es la que verán las empresas en tu perfil.
      </p>

      <form onSubmit={guardar} className="tarjeta">
        <div className="campo">
          <label htmlFor="nombre">Nombre</label>
          <input
            id="nombre"
            value={form.nombre}
            onChange={(e) => actualizar("nombre", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="apellido">Apellido</label>
          <input
            id="apellido"
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
            value={form.presentacion}
            onChange={(e) => actualizar("presentacion", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="linkedin">LinkedIn</label>
          <input
            id="linkedin"
            value={form.linkedin_url}
            onChange={(e) => actualizar("linkedin_url", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="foto">URL de foto</label>
          <input
            id="foto"
            value={form.foto_url}
            onChange={(e) => actualizar("foto_url", e.target.value)}
          />
        </div>

        {error && <p className="mensaje-error">{error}</p>}
        {exito && <p className="mensaje-exito">Perfil actualizado.</p>}

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button type="submit" className="boton boton-primario" disabled={guardando}>
            {guardando ? "Guardando…" : "Guardar cambios"}
          </button>
          <button type="button" className="boton boton-peligro" onClick={eliminarCuenta}>
            Eliminar cuenta
          </button>
        </div>
      </form>
    </div>
  );
}
