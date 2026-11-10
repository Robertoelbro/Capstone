import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";

const OFERTA_VACIA = {
  titulo: "",
  descripcion: "",
  requisitos: "",
  ubicacion: "",
  modalidad: "",
};

export default function OfertasEmpresa() {
  const [params] = useSearchParams();
  const usuarioId = params.get("usuario_id");

  const [ofertas, setOfertas] = useState([]);
  const [form, setForm] = useState(OFERTA_VACIA);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  function cargarOfertas() {
    return api
      .listarMisOfertas(usuarioId)
      .then(setOfertas)
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    if (!usuarioId) {
      setError("Falta indicar tu usuario (usuario_id) en la URL.");
      setCargando(false);
      return;
    }
    cargarOfertas().finally(() => setCargando(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuarioId]);

  function actualizar(campo, valor) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  function editar(oferta) {
    setEditandoId(oferta.id);
    setForm({
      titulo: oferta.titulo,
      descripcion: oferta.descripcion,
      requisitos: oferta.requisitos || "",
      ubicacion: oferta.ubicacion || "",
      modalidad: oferta.modalidad || "",
    });
  }

  function cancelarEdicion() {
    setEditandoId(null);
    setForm(OFERTA_VACIA);
  }

  async function enviar(e) {
    e.preventDefault();
    setError(null);
    try {
      if (editandoId) {
        await api.actualizarOferta(usuarioId, editandoId, form);
      } else {
        await api.crearOferta(usuarioId, form);
      }
      cancelarEdicion();
      await cargarOfertas();
    } catch (err) {
      setError(err.message);
    }
  }

  async function eliminar(ofertaId) {
    if (!confirm("¿Eliminar esta oferta?")) return;
    try {
      await api.eliminarOferta(usuarioId, ofertaId);
      await cargarOfertas();
    } catch (err) {
      setError(err.message);
    }
  }

  if (cargando) return <p className="contenedor">Cargando…</p>;

  return (
    <div className="contenedor">
      <h1>Mis ofertas de empleo</h1>

      <form onSubmit={enviar} className="tarjeta" style={{ maxWidth: 560, marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.1rem" }}>
          {editandoId ? "Editar oferta" : "Publicar nueva oferta"}
        </h2>

        <div className="campo">
          <label htmlFor="titulo">Título del cargo</label>
          <input
            id="titulo"
            required
            value={form.titulo}
            onChange={(e) => actualizar("titulo", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="descripcion">Descripción</label>
          <textarea
            id="descripcion"
            required
            rows={3}
            value={form.descripcion}
            onChange={(e) => actualizar("descripcion", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="requisitos">Requisitos</label>
          <textarea
            id="requisitos"
            rows={2}
            value={form.requisitos}
            onChange={(e) => actualizar("requisitos", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="ubicacion">Ubicación</label>
          <input
            id="ubicacion"
            value={form.ubicacion}
            onChange={(e) => actualizar("ubicacion", e.target.value)}
          />
        </div>
        <div className="campo">
          <label htmlFor="modalidad">Modalidad</label>
          <select
            id="modalidad"
            value={form.modalidad}
            onChange={(e) => actualizar("modalidad", e.target.value)}
          >
            <option value="">Selecciona una opción</option>
            <option value="presencial">Presencial</option>
            <option value="remoto">Remoto</option>
            <option value="hibrido">Híbrido</option>
          </select>
        </div>

        {error && <p className="mensaje-error">{error}</p>}

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button type="submit" className="boton boton-primario">
            {editandoId ? "Guardar cambios" : "Publicar oferta"}
          </button>
          {editandoId && (
            <button type="button" className="boton boton-secundario" onClick={cancelarEdicion}>
              Cancelar
            </button>
          )}
        </div>
      </form>

      <div style={{ display: "grid", gap: "1rem" }}>
        {ofertas.length === 0 && (
          <p style={{ color: "var(--color-muted)" }}>Aún no has publicado ofertas.</p>
        )}
        {ofertas.map((oferta) => (
          <article key={oferta.id} className="tarjeta">
            <h3 style={{ fontSize: "1.1rem", margin: 0 }}>{oferta.titulo}</h3>
            <p style={{ color: "var(--color-muted)" }}>
              {oferta.ubicacion} {oferta.modalidad ? `· ${oferta.modalidad}` : ""}
              {!oferta.activa && " · inactiva"}
            </p>
            <p>{oferta.descripcion}</p>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button className="boton boton-secundario" onClick={() => editar(oferta)}>
                Editar
              </button>
              <button className="boton boton-peligro" onClick={() => eliminar(oferta.id)}>
                Eliminar
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
