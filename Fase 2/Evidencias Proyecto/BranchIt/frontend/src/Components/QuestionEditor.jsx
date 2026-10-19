import PropTypes from "prop-types";

export default function QuestionEditor({ questions, onChange }) {
  const update = (id, values) =>
    onChange(questions.map((q) => (q.id === id ? { ...q, ...values } : q)));
  return (
    <fieldset className="question-editor">
      <legend>Preguntas para postular</legend>
      {questions.map((q, index) => (
        <div className="question-row" key={q.id}>
          <div className="section-heading">
            <strong>Pregunta {index + 1}</strong>
            <button
              type="button"
              className="text-danger"
              onClick={() =>
                onChange(questions.filter((item) => item.id !== q.id))
              }
            >
              Quitar pregunta {index + 1}
            </button>
          </div>
          <div className="campo">
            <label htmlFor={`label_${q.id}`}>Pregunta</label>
            <input
              id={`label_${q.id}`}
              value={q.etiqueta}
              required
              maxLength={160}
              onChange={(e) => update(q.id, { etiqueta: e.target.value })}
            />
          </div>
          <div className="campo">
            <label htmlFor={`type_${q.id}`}>Tipo de respuesta</label>
            <select
              id={`type_${q.id}`}
              value={q.tipo}
              onChange={(e) =>
                update(q.id, {
                  tipo: e.target.value,
                  opciones: ["seleccion", "seleccion_multiple"].includes(
                    e.target.value,
                  )
                    ? ["", ""]
                    : [],
                })
              }
            >
              <option value="texto">Texto corto (200 caracteres)</option>
              <option value="parrafo">Texto largo (3.000 caracteres)</option>
              <option value="numero">Número</option>
              <option value="seleccion">Una opción</option>
              <option value="seleccion_multiple">Varias opciones</option>
            </select>
          </div>
          {["seleccion", "seleccion_multiple"].includes(q.tipo) && (
            <div className="choice-options">
              {q.opciones.map((option, optionIndex) => (
                <div className="choice-option" key={optionIndex}>
                  <label className="editor-field">
                    Opción {optionIndex + 1}
                    <input
                      required
                      maxLength={100}
                      value={option}
                      ref={(node) =>
                        node?.setCustomValidity(
                          option && !option.trim()
                            ? "Escribe una opción."
                            : option.trim() &&
                              q.opciones.some(
                                (v, i) =>
                                  i !== optionIndex &&
                                  v.trim().toLocaleLowerCase() ===
                                    option.trim().toLocaleLowerCase(),
                              )
                            ? "Las opciones deben ser distintas."
                            : "",
                        )
                      }
                      onChange={(e) =>
                        update(q.id, {
                          opciones: q.opciones.map((v, i) =>
                            i === optionIndex ? e.target.value : v,
                          ),
                        })
                      }
                    />
                  </label>
                  <button
                    type="button"
                    disabled={q.opciones.length <= 2}
                    aria-label={`Quitar opción ${optionIndex + 1} de pregunta ${
                      index + 1
                    }`}
                    onClick={() =>
                      update(q.id, {
                        opciones: q.opciones.filter(
                          (_, i) => i !== optionIndex,
                        ),
                      })
                    }
                  >
                    Quitar
                  </button>
                </div>
              ))}
              <button
                type="button"
                className="boton boton-secundario"
                disabled={q.opciones.length >= 15}
                onClick={() => update(q.id, { opciones: [...q.opciones, ""] })}
              >
                Agregar opción
              </button>
            </div>
          )}
          <label className="consent">
            <input
              type="checkbox"
              checked={q.obligatoria}
              onChange={(e) => update(q.id, { obligatoria: e.target.checked })}
            />
            Respuesta obligatoria
          </label>
        </div>
      ))}
      <button
        type="button"
        className="boton boton-secundario"
        disabled={questions.length >= 10}
        onClick={() =>
          onChange([
            ...questions,
            {
              id: `q_${crypto.randomUUID()}`,
              etiqueta: "",
              tipo: "texto",
              obligatoria: true,
              opciones: [],
            },
          ])
        }
      >
        Agregar pregunta
      </button>
    </fieldset>
  );
}
QuestionEditor.propTypes = {
  questions: PropTypes.arrayOf(PropTypes.object).isRequired,
  onChange: PropTypes.func.isRequired,
};
