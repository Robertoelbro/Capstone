import {
  ValidatedForm,
  SearchField,
  PhoneField,
} from "../Components/FormFields";
import { careers } from "../data/catalogs";
import { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { FiEdit3, FiEye, FiPlus, FiTrash2, FiCopy } from "react-icons/fi";
import { useSession } from "../session";
import { api } from "../api";
import { emptyPortfolio } from "../portfolio";
import GraduateLayout from "../Components/GraduateLayout";
import PortfolioView from "../Components/PortfolioView";
import { UploadField } from "../Components/Media";
import MediaLibrary from "../Components/MediaLibrary";

function Field({
  label,
  value,
  onChange,
  type = "text",
  maxLength = 255,
  required = false,
  options,
}) {
  return (
    <label className="editor-field">
      <span>{label}</span>
      {options ? (
        <select value={value} onChange={(e) => onChange(e.target.value)}>
          {options.map((v) => (
            <option key={v}>{v}</option>
          ))}
        </select>
      ) : type === "textarea" ? (
        <textarea
          rows={4}
          value={value ?? ""}
          maxLength={maxLength}
          onChange={(e) => onChange(e.target.value)}
        />
      ) : (
        <input
          type={type === "number" ? "text" : type}
          inputMode={type === "number" ? "numeric" : undefined}
          pattern={type === "number" ? "[0-9]{4}" : undefined}
          value={value ?? ""}
          maxLength={maxLength}
          required={required}
          onChange={(e) => onChange(e.target.value)}
        />
      )}
    </label>
  );
}
Field.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
  type: PropTypes.string,
  maxLength: PropTypes.number,
  required: PropTypes.bool,
  options: PropTypes.array,
};

export default function PerfilEgresado() {
  const { user } = useSession();
  const [profile, setProfile] = useState(null),
    [form, setForm] = useState(null),
    [editing, setEditing] = useState(false);
  const [error, setError] = useState(""),
    [success, setSuccess] = useState(""),
    [saving, setSaving] = useState(false),
    [uploads, setUploads] = useState(0),
    [dirty, setDirty] = useState(false);
  useEffect(() => {
    let active = true;
    api
      .obtenerPerfilEgresado(user.id)
      .then((p) => {
        if (active) {
          setProfile(p);
          setForm({ ...p, portfolio: { ...emptyPortfolio, ...p.portfolio } });
        }
      })
      .catch((e) => {
        if (active) setError(e.message);
      });
    return () => {
      active = false;
    };
  }, [user.id]);
  useEffect(() => {
    if (!dirty) return;
    const warn = (e) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty]);
  function base(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
    setDirty(true);
    setSuccess("");
  }
  function update(key, value) {
    setForm((f) => ({ ...f, portfolio: { ...f.portfolio, [key]: value } }));
    setDirty(true);
    setSuccess("");
  }
  function item(kind, index, key, value) {
    update(
      kind,
      form.portfolio[kind].map((v, i) =>
        i === index ? { ...v, [key]: value } : v,
      ),
    );
  }
  function remove(kind, index) {
    update(
      kind,
      form.portfolio[kind].filter((_, i) => i !== index),
    );
  }
  function busy(value) {
    setUploads((n) => n + (value ? 1 : -1));
  }
  async function save(e) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const {
        nombre,
        apellido,
        carrera,
        anio_egreso,
        presentacion,
        linkedin_url,
        foto_url,
        portfolio,
      } = form;
      const clean = {
        ...portfolio,
        proyectos: portfolio.proyectos.map((p) => ({
          ...p,
          tecnologias: p.tecnologias.map((t) => t.trim()).filter(Boolean),
        })),
      };
      const result = await api.actualizarPerfilEgresado(user.id, {
        nombre,
        apellido,
        carrera,
        anio_egreso: anio_egreso ? Number(anio_egreso) : null,
        presentacion: presentacion || "",
        linkedin_url: linkedin_url || "",
        foto_url: foto_url || "",
        portfolio: clean,
      });
      setProfile(result);
      setForm({
        ...result,
        portfolio: { ...emptyPortfolio, ...result.portfolio },
      });
      setDirty(false);
      setSuccess("Cambios guardados.");
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }
  async function copy() {
    try {
      await navigator.clipboard.writeText(
        `${window.location.origin}/p/${user.id}`,
      );
      setSuccess("Enlace copiado.");
    } catch {
      setError("Selecciona y copia el enlace que aparece debajo.");
    }
  }
  if (!form)
    return (
      <div className="contenedor">
        {error ? (
          <p role="alert">{error}</p>
        ) : (
          <p role="status">Preparando tu espacio…</p>
        )}
      </div>
    );
  const p = form.portfolio;
  const field = (key, label, type = "text", maxLength = 255) => (
    <Field
      label={label}
      value={p[key]}
      type={type === "number" ? "text" : type}
      inputMode={type === "number" ? "numeric" : undefined}
      pattern={type === "number" ? "[0-9]{4}" : undefined}
      maxLength={maxLength}
      onChange={(v) => update(key, v)}
    />
  );
  const upload = (kind, key, label) => (
    <UploadField
      kind={kind}
      value={p[key]}
      label={label}
      onChange={(v) => update(key, v)}
      onBusy={busy}
    />
  );
  return (
    <GraduateLayout profile={profile}>
      <div className="portfolio-toolbar">
        <div>
          <h2>Mi portafolio</h2>
        </div>
        <div className="view-switch">
          <button
            aria-pressed={!editing}
            disabled={uploads > 0}
            onClick={() => setEditing(false)}
          >
            <FiEye />
            Vista previa
          </button>
          <button aria-pressed={editing} onClick={() => setEditing(true)}>
            <FiEdit3 />
            Editar perfil
          </button>
        </div>
      </div>
      {success && (
        <p className="mensaje-exito" role="status">
          {success}
        </p>
      )}
      {error && (
        <p className="mensaje-error" role="alert">
          {error}
        </p>
      )}
      <div className="publish-summary">
        <span>
          {profile.portfolio?.publico
            ? "● Portafolio publicado"
            : "○ Portafolio privado"}
          {dirty ? " · Tienes cambios sin guardar" : ""}
        </span>
        {profile.portfolio?.publico && (
          <>
            <button type="button" onClick={copy}>
              <FiCopy />
              Copiar enlace
            </button>
            <a href={`/p/${user.id}`} target="_blank" rel="noreferrer">
              {window.location.origin}/p/{user.id}
            </a>
          </>
        )}
      </div>
      {!editing ? (
        <>
          <p className="preview-notice">
            Vista previa de tus cambios. Los datos de contacto solo se muestran
            al público si los habilitas.
          </p>
          <PortfolioView profile={form} editing />
        </>
      ) : (
        <ValidatedForm className="portfolio-editor" onSubmit={save}>
          <fieldset disabled={saving}>
            <section className="editor-section">
              <h2>Perfil</h2>
              <div className="editor-grid">
                <Field
                  label="Nombre"
                  value={form.nombre}
                  required
                  maxLength={100}
                  onChange={(v) => base("nombre", v)}
                />
                <Field
                  label="Apellido"
                  value={form.apellido}
                  required
                  maxLength={100}
                  onChange={(v) => base("apellido", v)}
                />
                <SearchField
                  label="Carrera"
                  options={careers}
                  value={form.carrera || ""}
                  onChange={(v) => base("carrera", v)}
                />
                <Field
                  label="Año de egreso"
                  type="number"
                  value={form.anio_egreso}
                  onChange={(v) => base("anio_egreso", v)}
                />
                {field("titular", "Titular profesional", "text", 160)}
                {field("titulo_url", "Enlace al título profesional", "url", 1000)}
                {field("ubicacion", "Ciudad o región", "text", 120)}
              </div>
              <Field
                label="Presentación"
                type="textarea"
                maxLength={5000}
                value={form.presentacion}
                onChange={(v) => base("presentacion", v)}
              />
              <div className="editor-grid">
                {upload("foto", "foto_id", "Subir foto de perfil")}
              </div>
            </section>
            <section className="editor-section">
              <h2>Experiencia laboral</h2>
              <p className="field-help">Incluye trabajos que no requieran título: ventas, cocina, cine u otros.</p>
              {p.experiencia_laboral.map((work, i) => <fieldset className="tarjeta" key={i}>
                <legend>Experiencia {i + 1}</legend>
                <div className="editor-grid">
                  <Field label="Cargo *" value={work.cargo} required maxLength={120} onChange={v => item('experiencia_laboral', i, 'cargo', v)} />
                  <Field label="Empresa o lugar" value={work.empresa} maxLength={150} onChange={v => item('experiencia_laboral', i, 'empresa', v)} />
                  <Field label="Fecha de inicio *" type="date" required value={work.inicio} onChange={v => item('experiencia_laboral', i, 'inicio', v)} />
                  <Field label="Fecha de término (vacío si continúas)" type="date" value={work.fin || ''} onChange={v => item('experiencia_laboral', i, 'fin', v || null)} />
                </div>
                <Field label="Funciones y aprendizajes" type="textarea" value={work.descripcion} maxLength={2000} onChange={v => item('experiencia_laboral', i, 'descripcion', v)} />
                <button type="button" className="text-link" onClick={() => remove('experiencia_laboral', i)}>Eliminar experiencia {i + 1}</button>
              </fieldset>)}
              <button type="button" className="boton boton-secundario" disabled={p.experiencia_laboral.length >= 20} onClick={() => update('experiencia_laboral', [...p.experiencia_laboral, { cargo: '', empresa: '', inicio: '', fin: null, descripcion: '' }])}>Añadir experiencia laboral</button>
            </section>
            <section className="editor-section">
              <h2>Video de presentación</h2>
              <div className="editor-grid">
                {upload(
                  "presentacion",
                  "video_id",
                  "Subir presentación de hasta 1 minuto",
                )}
                {field(
                  "video_url",
                  "O enlace de presentación (YouTube, Vimeo u otro)",
                  "url",
                  1000,
                )}
              </div>
              <small>
                Verifica que los videos externos duren como máximo 1 minuto. El
                archivo subido tendrá prioridad.
              </small>
            </section>
            <section className="editor-section">
              <h2>Habilidades</h2>
              {p.habilidades.map((skill, i) => (
                <div className="editor-item skill-editor" key={i}>
                  <Field
                    label="Habilidad"
                    value={skill.nombre}
                    required
                    maxLength={120}
                    onChange={(v) => item("habilidades", i, "nombre", v)}
                  />
                  <Field
                    label="Nivel"
                    value={skill.nivel}
                    options={["Aprendiendo", "Intermedio", "Avanzado"]}
                    onChange={(v) => item("habilidades", i, "nivel", v)}
                  />
                  <button
                    type="button"
                    className="remove-item"
                    onClick={() => remove("habilidades", i)}
                    aria-label={`Quitar habilidad ${i + 1}`}
                  >
                    <FiTrash2 />
                  </button>
                </div>
              ))}
              <button
                className="add-item"
                type="button"
                disabled={p.habilidades.length >= 20}
                onClick={() =>
                  update("habilidades", [
                    ...p.habilidades,
                    { nombre: "", nivel: "Aprendiendo" },
                  ])
                }
              >
                <FiPlus />
                Añadir habilidad
              </button>
            </section>
            <section className="editor-section">
              <h2>Certificaciones</h2>
              {p.certificaciones.map((cert, i) => (
                <div className="editor-item" key={i}>
                  <div className="item-heading">
                    <h3>Certificación {i + 1}</h3>
                    <button
                      type="button"
                      onClick={() => remove("certificaciones", i)}
                      aria-label={`Quitar certificación ${i + 1}`}
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                  <div className="editor-grid">
                    <Field
                      label="Nombre de la certificación"
                      value={cert.nombre}
                      required
                      maxLength={120}
                      onChange={(v) => item("certificaciones", i, "nombre", v)}
                    />
                    <Field
                      label="Institución que la emite"
                      value={cert.entidad}
                      maxLength={150}
                      onChange={(v) => item("certificaciones", i, "entidad", v)}
                    />
                    <Field
                      label="Enlace para verificar la certificación"
                      type="url"
                      maxLength={1000}
                      value={cert.url}
                      onChange={(v) => item("certificaciones", i, "url", v)}
                    />
                    <UploadField
                      kind="certificado"
                      label="O subir certificado"
                      value={cert.archivo_id}
                      onBusy={busy}
                      onChange={(v) =>
                        item("certificaciones", i, "archivo_id", v)
                      }
                    />
                  </div>
                  <small>Añade al menos un enlace o archivo.</small>
                </div>
              ))}
              <button
                type="button"
                className="add-item"
                disabled={p.certificaciones.length >= 12}
                onClick={() =>
                  update("certificaciones", [
                    ...p.certificaciones,
                    { nombre: "", entidad: "", url: "", archivo_id: null },
                  ])
                }
              >
                <FiPlus />
                Añadir certificación
              </button>
            </section>
            <section className="editor-section">
              <h2>Proyectos</h2>
              {p.proyectos.map((project, i) => (
                <div className="editor-item" key={i}>
                  <div className="item-heading">
                    <h3>Proyecto {i + 1}</h3>
                    <button
                      type="button"
                      onClick={() => remove("proyectos", i)}
                      aria-label={`Quitar proyecto ${i + 1}`}
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                  <div className="editor-grid">
                    <Field
                      label="Nombre del proyecto"
                      required
                      maxLength={120}
                      value={project.titulo}
                      onChange={(v) => item("proyectos", i, "titulo", v)}
                    />
                    <Field
                      label="Tipo de proyecto"
                      value={project.tipo}
                      options={["Académico", "Personal"]}
                      onChange={(v) => item("proyectos", i, "tipo", v)}
                    />
                  </div>
                  <Field
                    label="Descripción del proyecto"
                    type="textarea"
                    maxLength={2000}
                    value={project.descripcion}
                    onChange={(v) => item("proyectos", i, "descripcion", v)}
                  />
                  <Field
                    label="Herramientas o tecnologías (separadas por coma)"
                    value={project.tecnologias.join(",")}
                    onChange={(v) =>
                      item(
                        "proyectos",
                        i,
                        "tecnologias",
                        v.split(",").slice(0, 12),
                      )
                    }
                  />
                  <div className="editor-grid">
                    {[
                      ["github_url", "Repositorio GitHub"],
                      ["proyecto_url", "Enlace para ver el proyecto"],
                      ["video_url", "Enlace de video demo"],
                    ].map(([key, label]) => (
                      <Field
                        key={key}
                        label={label}
                        type="url"
                        maxLength={1000}
                        value={project[key]}
                        onChange={(v) => item("proyectos", i, key, v)}
                      />
                    ))}
                    <UploadField
                      kind="proyecto"
                      label="Subir video demo"
                      value={project.video_id}
                      onBusy={busy}
                      onChange={(v) => item("proyectos", i, "video_id", v)}
                    />
                    <UploadField
                      kind="qr"
                      label="Subir imagen QR del proyecto"
                      value={project.qr_id}
                      onBusy={busy}
                      onChange={(v) => item("proyectos", i, "qr_id", v)}
                    />
                  </div>
                </div>
              ))}
              <button
                type="button"
                className="add-item"
                disabled={p.proyectos.length >= 12}
                onClick={() =>
                  update("proyectos", [
                    ...p.proyectos,
                    {
                      titulo: "",
                      descripcion: "",
                      tipo: "Académico",
                      tecnologias: [],
                      github_url: "",
                      proyecto_url: "",
                      video_url: "",
                      video_id: null,
                      qr_id: null,
                    },
                  ])
                }
              >
                <FiPlus />
                Añadir proyecto
              </button>
            </section>
            <section className="editor-section">
              <h2>Contacto y disponibilidad</h2>
              <div className="editor-grid">
                {field(
                  "contacto_email",
                  "Correo de contacto (no cambia tu acceso)",
                  "email",
                )}
                <PhoneField
                  label="Teléfono de contacto"
                  value={p.contacto_telefono}
                  onChange={(v) => update("contacto_telefono", v)}
                />
                <Field
                  label="Disponibilidad"
                  value={p.disponibilidad}
                  options={[
                    "Sin definir",
                    "Inmediata",
                    "En 2 semanas",
                    "En 1 mes",
                    "A convenir",
                    "No disponible",
                  ]}
                  onChange={(v) => update("disponibilidad", v)}
                />
                {field("github_url", "Tu GitHub", "url", 1000)}
                <Field
                  label="Tu LinkedIn"
                  type="url"
                  value={form.linkedin_url}
                  onChange={(v) => base("linkedin_url", v)}
                />
              </div>
            </section>
            <section className="editor-section publication-settings">
              <h2>Apariencia y privacidad</h2>
              <div className="theme-options">
                {[
                  ["bosque", "Bosque"],
                  ["arcilla", "Arcilla"],
                  ["oceano", "Océano"],
                ].map(([value, label]) => (
                  <button
                    type="button"
                    key={value}
                    className={`theme-choice theme-${value}`}
                    aria-pressed={p.tema === value}
                    onClick={() => update("tema", value)}
                  >
                    <i />
                    {label}
                  </button>
                ))}
              </div>
              {[
                ["publico", "Publicar portafolio y archivos"],
                ["mostrar_email", "Mostrar correo público"],
                ["mostrar_telefono", "Mostrar teléfono público"],
              ].map(([key, label]) => (
                <label className="check-line" key={key}>
                  <input
                    type="checkbox"
                    checked={p[key]}
                    onChange={(e) => update(key, e.target.checked)}
                  />
                  {label}
                </label>
              ))}
              <details>
                <summary>Privacidad de los archivos</summary>
                <p>
                  Al despublicar se oculta tu perfil. Los enlaces de archivos ya
                  abiertos pueden durar hasta 5 minutos. Los enlaces externos
                  dependen de la privacidad de su servicio.
                </p>
              </details>
            </section>
            <MediaLibrary />
            <div className="editor-save">
              <span>
                {uploads
                  ? "Espera a que terminen las subidas."
                  : dirty
                  ? "Hay cambios sin guardar."
                  : "Todo está al día."}
              </span>
              <button
                className="boton boton-primario"
                disabled={saving || uploads > 0}
              >
                {saving ? "Guardando…" : "Guardar mi portafolio"}
              </button>
            </div>
          </fieldset>
        </ValidatedForm>
      )}
    </GraduateLayout>
  );
}
