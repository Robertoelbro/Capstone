import { useState } from "react";
import PropTypes from "prop-types";

export default function ShareJob({ job }) {
  const [message, setMessage] = useState("");
  const [fallback, setFallback] = useState(false);
  const [busy, setBusy] = useState(false);
  const url = `${window.location.origin}/ofertas/${encodeURIComponent(job.id)}`;
  async function share() {
    setBusy(true);
    setMessage("");
    try {
      if (navigator.share) {
        await navigator.share({ title: job.titulo, text: `${job.titulo} · ${job.nombre_empresa}`, url });
      } else if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(url);
        setMessage("Enlace copiado.");
      } else {
        setFallback(true);
      }
    } catch (err) {
      if (err.name !== "AbortError") setFallback(true);
    } finally {
      setBusy(false);
    }
  }
  return <div className="share-job">
    <button type="button" className="text-link" onClick={share} disabled={busy} aria-label={`Compartir oferta: ${job.titulo}`}>{busy ? "Compartiendo…" : "Compartir oferta"}</button>
    {message && <span role="status">{message}</span>}
    {fallback && <label>Enlace de la oferta<input aria-label={`Enlace para compartir ${job.titulo}`} value={url} readOnly onFocus={(e) => e.target.select()} /></label>}
  </div>;
}
ShareJob.propTypes = { job: PropTypes.object.isRequired };
