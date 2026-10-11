import { useEffect, useState, useId } from "react";
import PropTypes from "prop-types";
import { upload } from "@vercel/blob/client";
import { api, getToken } from "../api";

export function Asset({ id, type = "image", alt = "", label = "Ver archivo" }) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let alive = true;
    setUrl("");
    setError("");
    fetch(`/api/media-read?id=${encodeURIComponent(id)}`, {
      headers: getToken() ? { Authorization: `Bearer ${getToken()}` } : {},
    })
      .then(async (r) => {
        if (!r.ok) throw new Error("Archivo no disponible");
        return r.json();
      })
      .then((data) => {
        if (alive) setUrl(data.url);
      })
      .catch(() => {
        if (alive) setError("No pudimos cargar este archivo.");
      });
    return () => {
      alive = false;
    };
  }, [id, retry]);
  if (error)
    return (
      <span className="media-error">
        {error}{" "}
        <button type="button" onClick={() => setRetry((n) => n + 1)}>
          Reintentar
        </button>
      </span>
    );
  if (!url)
    return (
      <span className="media-loading" role="status">
        Cargando archivo…
      </span>
    );
  if (type === "video")
    return (
      <video
        controls
        preload="metadata"
        src={url}
        onError={() => setError("El video no se pudo reproducir.")}
        aria-label={alt}
      />
    );
  if (type === "document")
    return (
      <a className="text-link" href={url} target="_blank" rel="noreferrer">
        {label} ↗
      </a>
    );
  return (
    <img
      src={url}
      alt={alt}
      loading="lazy"
      onError={() => setError("La imagen no se pudo cargar.")}
    />
  );
}
Asset.propTypes = {
  id: PropTypes.string.isRequired,
  type: PropTypes.string,
  alt: PropTypes.string,
  label: PropTypes.string,
};

const limits = {
  foto: 3,
  qr: 3,
  certificado: 5,
  presentacion: 15,
  proyecto: 30,
};
const accept = {
  foto: "image/jpeg,image/png,image/webp",
  qr: "image/jpeg,image/png,image/webp",
  certificado: "application/pdf,image/jpeg,image/png,image/webp",
  presentacion: "video/mp4,video/webm",
  proyecto: "video/mp4,video/webm",
};
function duration(file) {
  return new Promise((resolve, reject) => {
    const video = document.createElement("video");
    const url = URL.createObjectURL(file);
    const timer = setTimeout(() => finish(null), 10000);
    function finish(value) {
      clearTimeout(timer);
      URL.revokeObjectURL(url);
      video.removeAttribute("src");
      if (value) resolve(value);
      else
        reject(
          new Error("No pudimos leer la duración del video. Usa MP4 o WebM."),
        );
    }
    video.preload = "metadata";
    video.onloadedmetadata = () =>
      finish(Number.isFinite(video.duration) ? video.duration : null);
    video.onerror = () => finish(null);
    video.src = url;
  });
}
export function UploadField({ kind, value, onChange, label, onBusy }) {
  const inputId = useId();
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [progress, setProgress] = useState(0);
  async function select(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setError("");
    setBusy(true);
    onBusy?.(true);
    setProgress(0);
    try {
      if (!accept[kind].split(",").includes(file.type))
        throw new Error("Formato no admitido.");
      if (file.size > limits[kind] * 1024 * 1024)
        throw new Error(
          `El archivo debe pesar como máximo ${limits[kind]} MB.`,
        );
      const seconds =
        kind === "presentacion" || kind === "proyecto"
          ? await duration(file)
          : null;
      if (seconds && seconds > (kind === "presentacion" ? 60 : 180))
        throw new Error(
          `El video debe durar como máximo ${
            kind === "presentacion" ? "1 minuto" : "3 minutos"
          }.`,
        );
      const asset = await api.reserveMedia({
        tipo: kind,
        nombre: file.name,
        mime: file.type,
        tamano: file.size,
        duracion: seconds,
      });
      await upload(asset.pathname, file, {
        access: "private",
        handleUploadUrl: "/api/media-upload",
        clientPayload: JSON.stringify({ id: asset.id }),
        headers: { Authorization: `Bearer ${getToken()}` },
        multipart: file.size > 4 * 1024 * 1024,
        onUploadProgress: (p) => setProgress(Math.round(p.percentage)),
      });
      const verified = await fetch("/api/media-manage", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ id: asset.id }),
      });
      if (!verified.ok) {
        const result = await verified.json();
        throw new Error(result.error || "No se pudo validar el archivo.");
      }
      onChange(asset.id);
    } catch (err) {
      setError(err.message || "No se pudo subir el archivo.");
    } finally {
      setBusy(false);
      onBusy?.(false);
      event.target.value = "";
    }
  }
  return (
    <div className="upload-field">
      <label htmlFor={inputId}>{label}</label>
      <input
        id={inputId}
        type="file"
        accept={accept[kind]}
        disabled={busy}
        onChange={select}
      />
      <small>
        Máximo {limits[kind]} MB
        {kind === "presentacion"
          ? " · 60 segundos"
          : kind === "proyecto"
          ? " · 3 minutos"
          : ""}
        .{" "}
        {kind === "certificado"
          ? "PDF o imagen"
          : kind === "presentacion" || kind === "proyecto"
          ? "MP4 o WebM"
          : "JPG, PNG o WebP"}
        .
      </small>
      {busy && <p role="status">Subiendo… {progress}%</p>}
      {value && (
        <div className="upload-selected">
          <span>Archivo adjunto ✓</span>
          <button type="button" onClick={() => onChange(null)}>
            Quitar del perfil
          </button>
        </div>
      )}
      {error && (
        <p className="mensaje-error" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
UploadField.propTypes = {
  kind: PropTypes.string.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
  onBusy: PropTypes.func,
};
