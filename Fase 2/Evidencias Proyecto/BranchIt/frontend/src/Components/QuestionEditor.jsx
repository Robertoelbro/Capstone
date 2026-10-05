import PropTypes from "prop-types";

export default function QuestionEditor({ questions, onChange }) {
  const update = (id, values) =>
    onChange(questions.map((q) => (q.id === id ? { ...q, ...values } : q)));
  return (
    <fieldset className="question-editor">
      <legend>Preguntas para postular</legend>
      <p className="muted">
        Agrega hasta 10 preguntas relacionadas con el cargo. Evita solicitar
        datos sensibles que no sean necesarios para evaluar la postulación.
      </p>
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
                update(q.id, { tipo: e.target.value, opciones: [] })
              }
            >
              <option value="texto">Texto corto</option>
              <option value="parrafo">Texto largo</option>
              <option value="numero">Número</option>
              <option value="seleccion">Selección</option>
            </select>
          </div>
          {q.tipo === "seleccion" && (
            <div className="campo">
              <label htmlFor={`options_${q.id}`}>
                Opciones (una por línea, entre 2 y 15)
              </label>
              <textarea
                id={`options_${q.id}`}
                value={q.opciones.join("\n")}
                required
                rows={3}
                onChange={(e) =>
                  update(q.id, { opciones: e.target.value.split("\n") })
                }
              />
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
