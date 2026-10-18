import { useEffect, useState } from "react";
import { useSession } from "../session";
import { api } from "../api";
import { Link } from "react-router-dom";
import WorkspaceNav from "../Components/WorkspaceNav";
import QuestionEditor from "../Components/QuestionEditor";

import {
  ValidatedForm,
  MoneyField,
  SearchField,
} from "../Components/FormFields";
import { careers } from "../data/catalogs";

const OFERTA_VACIA = {
  sueldo: "",
  funciones: "",
  perfiles_deseados: [],
  condiciones_laborales: "",
  adaptada_discapacidad: "",
  categoria: "General",
  titulo: "",
  descripcion: "",
  requisitos: "",
  ubicacion: "",
  modalidad: "",
  preguntas: [],
  activa: true,
};

export default function OfertasEmpresa() {
  const { user } = useSession();
  const usuarioId = user.id;

  const [ofertas, setOfertas] = useState([]);
  const [form, setForm] = useState(OFERTA_VACIA);
  const [editandoId, setEditandoId] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState("");
  const [careerCandidate, setCareerCandidate] = useState("");

  function cargarOfertas() {
    return api
      .listarMisOfertas(usuarioId)
      .then(setOfertas)
      .catch((err) => setError(err.message));
  }

  useEffect(() => {
    if (!usuarioId) {
      setError("Inicia sesión para continuar.");
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
    setCareerCandidate("");
    setEditandoId(oferta.id);
    setForm({
      sueldo: oferta.sueldo || "",
      funciones: oferta.funciones || "",
      perfiles_deseados: oferta.perfiles_deseados || [],
      condiciones_laborales: oferta.condiciones_laborales || "",
      adaptada_discapacidad:
        oferta.adaptada_discapacidad == null
          ? ""
          : String(oferta.adaptada_discapacidad),
      categoria: oferta.categoria || "General",
      titulo: oferta.titulo,
      descripcion: oferta.descripcion,
      requisitos: oferta.requisitos || "",
      ubicacion: oferta.ubicacion || "",
      modalidad: oferta.modalidad || "",
      preguntas: oferta.preguntas,
      activa: oferta.activa,
    });
  }

  function cancelarEdicion() {
    setCareerCandidate("");
    setEditandoId(null);
    setForm(OFERTA_VACIA);
  }

  async function enviar(e) {
    e.preventDefault();
    setError(null);
    setSuccess("");
    setBusy(true);
    try {
      const { activa, ...base } = form;
      const payload = {
        ...base,
        sueldo: Number(base.sueldo),
        perfiles_deseados: [
          ...new Set([
            ...base.perfiles_deseados,
            ...(careerCandidate ? [careerCandidate] : []),
          ]),
        ],
        adaptada_discapacidad: base.adaptada_discapacidad === "true",
        preguntas: base.preguntas.map((q) => ({
          ...q,
          opciones: q.opciones.map((v) => v.trim()).filter(Boolean),
        })),
      };
      if (editandoId) {
        await api.actualizarOferta(usuarioId, editandoId, {
          ...payload,
          activa,
        });
      } else {
        await api.crearOferta(usuarioId, payload);
      }
      setSuccess(editandoId ? "Oferta actualizada." : "Oferta publicada.");
      cancelarEdicion();
      await cargarOfertas();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function eliminar(ofertaId) {
    if (!confirm("¿Eliminar esta oferta?")) return;
    setError(null);
    setBusy(true);
    setSuccess("");
    try {
      await api.eliminarOferta(usuarioId, ofertaId);
      await cargarOfertas();
      if (editandoId === ofertaId) cancelarEdicion();
      setSuccess("Oferta eliminada.");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (cargando) return <p className="contenedor">Cargando…</p>;

  return (
    <div className="contenedor">
      <WorkspaceNav />
      <h1>Mis ofertas de empleo</h1>
      {success && (
        <p className="mensaje-exito" role="status">
          {success}
        </p>
      )}

      <ValidatedForm
        key={editandoId || "new"}
        onSubmit={enviar}
        className="tarjeta"
        style={{ maxWidth: 880, marginBottom: "2rem" }}
      >
        <fieldset disabled={busy}>
          <h2 style={{ fontSize: "1.1rem" }}>
            {editandoId ? "Editar oferta" : "Publicar nueva oferta"}
          </h2>

          <div className="campo">
            <label htmlFor="titulo">Título del cargo</label>
            <input
              id="titulo"
              required
              maxLength={150}
              value={form.titulo}
              onChange={(e) => actualizar("titulo", e.target.value)}
            />
          </div>

          <div className="campo">
            <label htmlFor="categoria">Categoría de la oferta</label>
            <select
              id="categoria"
              value={form.categoria}
              onChange={(e) => actualizar("categoria", e.target.value)}
            >
              {[
                "General",
                "Tecnología",
                "Salud",
                "Administración y finanzas",
                "Diseño y comunicación",
                "Educación",
                "Ingeniería y construcción",
                "Logística y operaciones",
                "Turismo y gastronomía",
                "Ciencias sociales",
                "Medioambiente y agro",
              ].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="campo">
            <label htmlFor="descripcion">Información del cargo</label>
            <textarea
              id="descripcion"
              required
              rows={3}
              value={form.descripcion}
              onChange={(e) => actualizar("descripcion", e.target.value)}
            />
          </div>
          <MoneyField
            value={form.sueldo}
            onChange={(v) => actualizar("sueldo", v)}
          />
          <label className="editor-field">
            Funciones del cargo
            <textarea
              required
              maxLength={10000}
              rows={4}
              value={form.funciones}
              onChange={(e) => actualizar("funciones", e.target.value)}
            />
          </label>
          <fieldset>
            <legend>Perfiles deseados *</legend>
            <div className="desired-careers">
              {form.perfiles_deseados.map((v) => (
                <button
                  type="button"
                  key={v}
                  aria-label={`Quitar ${v}`}
                  onClick={() =>
                    actualizar(
                      "perfiles_deseados",
                      form.perfiles_deseados.filter((item) => item !== v),
                    )
                  }
                >
                  {v} ×
                </button>
              ))}
            </div>
            {form.perfiles_deseados.length < 20 && (
              <>
                <SearchField
                  key={`${editandoId}-${form.perfiles_deseados.length}`}
                  label="Añadir carrera"
                  options={careers}
                  required={!form.perfiles_deseados.length}
                  onChange={setCareerCandidate}
                />
                <button
                  type="button"
                  className="boton boton-secundario"
                  disabled={!careerCandidate}
                  onClick={() => {
                    if (!form.perfiles_deseados.includes(careerCandidate))
                      actualizar("perfiles_deseados", [
                        ...form.perfiles_deseados,
                        careerCandidate,
                      ]);
                    setCareerCandidate("");
                  }}
                >
                  Agregar perfil
                </button>
              </>
            )}
          </fieldset>
          <label className="editor-field">
            Condiciones laborales
            <textarea
              required
              rows={4}
              maxLength={10000}
              value={form.condiciones_laborales}
              onChange={(e) =>
                actualizar("condiciones_laborales", e.target.value)
              }
            />
          </label>
          <label className="editor-field">
            ¿El cargo contempla adaptaciones para personas con discapacidad?
            <select
              required
              value={form.adaptada_discapacidad}
              onChange={(e) =>
                actualizar("adaptada_discapacidad", e.target.value)
              }
            >
              <option value="">Seleccionar</option>
              <option value="true">Sí</option>
              <option value="false">No</option>
            </select>
          </label>
          {editandoId && (
            <label className="consent">
              <input
                type="checkbox"
                checked={form.activa}
                onChange={(e) => actualizar("activa", e.target.checked)}
              />
              Recibir nuevas postulaciones
            </label>
          )}
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

          <QuestionEditor
            questions={form.preguntas}
            onChange={(value) => actualizar("preguntas", value)}
          />

          {error && (
            <p className="mensaje-error" role="alert">
              {error}
            </p>
          )}

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button type="submit" className="boton boton-primario">
              {busy
                ? "Guardando…"
                : editandoId
                ? "Guardar cambios"
                : "Publicar oferta"}
            </button>
            {editandoId && (
              <button
                type="button"
                className="boton boton-secundario"
                onClick={cancelarEdicion}
              >
                Cancelar
              </button>
            )}
          </div>
        </fieldset>
      </ValidatedForm>

      <div style={{ display: "grid", gap: "1rem" }}>
        {ofertas.length === 0 && (
          <p style={{ color: "var(--color-muted)" }}>
            Aún no has publicado ofertas.
          </p>
        )}
        {ofertas.map((oferta) => (
          <article key={oferta.id} className="tarjeta">
            <h3 style={{ fontSize: "1.1rem", margin: 0 }}>{oferta.titulo}</h3>
            <p style={{ color: "var(--color-muted)" }}>
              {oferta.ubicacion}{" "}
              {oferta.modalidad ? `· ${oferta.modalidad}` : ""}
              {!oferta.activa && " · inactiva"}
            </p>
            <p>{oferta.descripcion}</p>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                className="boton boton-secundario"
                disabled={busy}
                onClick={() => editar(oferta)}
              >
                Editar
              </button>
              <button
                className="boton boton-peligro"
                disabled={busy}
                onClick={() => eliminar(oferta.id)}
              >
                Eliminar
              </button>
              <Link
                className="boton boton-secundario"
                to={`/ofertas-empresa/${oferta.id}/postulaciones`}
              >
                Ver postulantes
              </Link>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
