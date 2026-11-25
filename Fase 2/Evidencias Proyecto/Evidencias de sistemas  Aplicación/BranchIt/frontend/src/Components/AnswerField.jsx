import { useState } from "react";
import PropTypes from "prop-types";

export default function AnswerField({ question: q }) {
  const [selected, setSelected] = useState([]);
  const [text, setText] = useState("");
  const name = `answer_${q.id}`;
  const multiple = q.tipo === "seleccion_multiple";
  const limit = q.tipo === "parrafo" ? 3000 : q.tipo === "numero" ? 100 : 200;
  if (multiple)
    return (
      <fieldset className="campo">
        <legend>
          {q.etiqueta}
          {q.obligatoria ? " *" : " (opcional)"}
        </legend>
        {q.opciones.map((option, i) => (
          <label className="consent" key={option}>
            <input
              type="checkbox"
              name={name}
              value={option}
              ref={(node) => {
                if (i === 0) {
                  node?.setCustomValidity(
                    q.obligatoria && !selected.length
                      ? "Selecciona al menos una opción."
                      : "",
                  );
                  if (!q.obligatoria || selected.length)
                    node?.removeAttribute("aria-invalid");
                }
              }}
              checked={selected.includes(option)}
              onChange={(e) =>
                setSelected((old) =>
                  e.target.checked
                    ? [...old, option]
                    : old.filter((v) => v !== option),
                )
              }
            />
            {option}
          </label>
        ))}
      </fieldset>
    );
  return (
    <div className="campo">
      <label htmlFor={name}>
        {q.etiqueta}
        {q.obligatoria ? "" : " (opcional)"}
      </label>
      {q.tipo === "seleccion" ? (
        <select id={name} name={name} required={q.obligatoria}>
          <option value="">Seleccionar</option>
          {q.opciones.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
      ) : (
        <>
          {q.tipo === "parrafo" ? (
            <textarea
              id={name}
              name={name}
              required={q.obligatoria}
              rows={4}
              maxLength={limit}
              value={text}
              aria-describedby={`${name}-limit`}
              onChange={(e) => setText(e.target.value)}
            />
          ) : (
            <input
              id={name}
              name={name}
              required={q.obligatoria}
              type="text"
              inputMode={q.tipo === "numero" ? "decimal" : undefined}
              pattern={
                q.tipo === "numero" ? "-?[0-9]+([.,][0-9]+)?" : undefined
              }
              maxLength={limit}
              value={text}
              aria-describedby={
                q.tipo === "numero" ? undefined : `${name}-limit`
              }
              onChange={(e) => setText(e.target.value)}
            />
          )}
          {q.tipo !== "numero" && (
            <small id={`${name}-limit`}>
              {text.length.toLocaleString("es-CL")} /{" "}
              {limit.toLocaleString("es-CL")} caracteres
            </small>
          )}
        </>
      )}
    </div>
  );
}
AnswerField.propTypes = { question: PropTypes.object.isRequired };
