import { useEffect, useState } from "react";
import { api, getToken } from "../api";

export default function MediaLibrary() {
  const [items, setItems] = useState([]),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  async function refresh() {
    try {
      setItems(await api.mediaLibrary());
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => {
    refresh();
  }, []);
  async function remove(id) {
    if (
      !confirm(
        "¿Eliminar este archivo permanentemente? Primero quítalo del perfil y guarda los cambios.",
      )
    )
      return;
    setBusy(true);
    setError("");
    try {
      const r = await fetch("/api/media-manage", {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ id }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error);
      await refresh();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <details className="editor-section">
      <summary>Biblioteca de archivos · administrar espacio</summary>
      <p>
        Hasta 100 MB y 40 archivos. Quitar un archivo del perfil no lo borra de
        esta biblioteca. Guarda el perfil antes de eliminar archivos.
      </p>
      <button type="button" className="text-link" onClick={refresh}>
        Actualizar lista
      </button>
      {error && (
        <p role="alert" className="mensaje-error">
          {error}
        </p>
      )}
      {items.map((item) => (
        <div className="library-row" key={item.id}>
          <span>
            {item.nombre}{" "}
            <small>
              {(item.tamano / 1024 / 1024).toFixed(2)} MB · {item.tipo}
            </small>
          </span>
          <button type="button" disabled={busy} onClick={() => remove(item.id)}>
            Eliminar
          </button>
        </div>
      ))}
      {!items.length && <p>Todavía no has subido archivos.</p>}
    </details>
  );
}
