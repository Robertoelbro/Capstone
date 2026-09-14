import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";

export default function HubEgresado() {
  const [params] = useSearchParams();
  const usuarioId = params.get("usuario_id");

  const [ofertas, setOfertas] = useState([]);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    if (!usuarioId) {
      setError("Falta indicar tu usuario (usuario_id) en la URL.");
      setCargando(false);
      return;
    }
    api
      .ofertasParaEgresado(usuarioId)
      .then(setOfertas)
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false));
  }, [usuarioId]);

  return (
    <div className="contenedor">
      <h1>Ofertas de empleo</h1>

      {cargando && <p>Cargando ofertas…</p>}
      {error && <p className="mensaje-error">{error}</p>}

      {!cargando && !error && ofertas.length === 0 && (
        <p style={{ color: "var(--color-muted)" }}>
          Todavía no hay ofertas publicadas.
        </p>
      )}

      <div style={{ display: "grid", gap: "1rem" }}>
        {ofertas.map((oferta) => (
          <article key={oferta.id} className="tarjeta">
            <h2 style={{ fontSize: "1.15rem" }}>{oferta.titulo}</h2>
            <p style={{ color: "var(--color-muted)", margin: "0 0 0.5rem" }}>
              {oferta.nombre_empresa}
              {oferta.ubicacion ? ` · ${oferta.ubicacion}` : ""}
              {oferta.modalidad ? ` · ${oferta.modalidad}` : ""}
            </p>
            <p>{oferta.descripcion}</p>
            {oferta.requisitos && (
              <p>
                <strong>Requisitos:</strong> {oferta.requisitos}
              </p>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}
