import { useState } from "react";
import PropTypes from "prop-types";
import { api } from "../api";
import { ValidatedForm } from "./FormFields";

export default function JobClosure({ job, onSaved }) {
  const [open, setOpen] = useState(false),
    [items, setItems] = useState([]),
    [choice, setChoice] = useState("");
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  async function show() {
    setOpen(true);
    setBusy(true);
    setError("");
    try {
      const values = await api.applicants(job.id);
      setItems(values);
      setChoice(values.find((v) => v.seleccionada)?.id?.toString() || "");
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.closeJob(job.id, choice === "none" ? null : Number(choice));
      await onSaved();
      setOpen(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="job-closure">
      {!open ? (
        <button type="button" className="boton boton-secundario" onClick={show}>
          {job.activa ? "Cerrar convocatoria" : "Ver o cambiar selección"}
        </button>
      ) : (
        <ValidatedForm onSubmit={submit}>
          <fieldset disabled={busy}>
            <legend>
              {job.activa ? "Cerrar convocatoria" : "Selección de candidato"}
            </legend>
            <label className="editor-field">
              Candidato seleccionado
              <select
                required
                value={choice}
                onChange={(e) => setChoice(e.target.value)}
              >
                <option value="">Seleccionar</option>
                <option value="none">Cerrar sin seleccionar candidato</option>
                {items.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.datos.nombre} {item.datos.apellido} ·{" "}
                    {item.datos.email}
                  </option>
                ))}
              </select>
            </label>
            <p className="muted">
              La selección es privada. Los egresados solo verán que la
              convocatoria está cerrada.
            </p>
            <div className="offer-actions">
              <button className="boton boton-primario">
                {busy
                  ? "Guardando…"
                  : job.activa
                  ? "Confirmar cierre"
                  : "Guardar selección"}
              </button>
              <button
                type="button"
                className="boton boton-secundario"
                onClick={() => setOpen(false)}
              >
                Cancelar
              </button>
            </div>
          </fieldset>
        </ValidatedForm>
      )}
      {error && (
        <p className="mensaje-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
JobClosure.propTypes = {
  job: PropTypes.object.isRequired,
  onSaved: PropTypes.func.isRequired,
};
