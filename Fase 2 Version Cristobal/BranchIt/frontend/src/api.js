const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function solicitud(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    const cuerpo = await res.json().catch(() => ({}));
    throw new Error(cuerpo.detail || `Error ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  registrarEgresado: (datos) =>
    solicitud("/auth/registro/egresado", { method: "POST", body: JSON.stringify(datos) }),

  registrarEmpresa: (datos) =>
    solicitud("/auth/registro/empresa", { method: "POST", body: JSON.stringify(datos) }),

  obtenerPerfilEgresado: (usuarioId) => solicitud(`/egresados/${usuarioId}`),

  actualizarPerfilEgresado: (usuarioId, datos) =>
    solicitud(`/egresados/${usuarioId}`, { method: "PUT", body: JSON.stringify(datos) }),

  eliminarCuentaEgresado: (usuarioId) =>
    solicitud(`/egresados/${usuarioId}`, { method: "DELETE" }),

  ofertasParaEgresado: (usuarioId) => solicitud(`/egresados/${usuarioId}/ofertas`),

  listarMisOfertas: (usuarioId) => solicitud(`/empresas/${usuarioId}/ofertas`),

  crearOferta: (usuarioId, datos) =>
    solicitud(`/empresas/${usuarioId}/ofertas`, { method: "POST", body: JSON.stringify(datos) }),

  actualizarOferta: (usuarioId, ofertaId, datos) =>
    solicitud(`/empresas/${usuarioId}/ofertas/${ofertaId}`, {
      method: "PUT",
      body: JSON.stringify(datos),
    }),

  eliminarOferta: (usuarioId, ofertaId) =>
    solicitud(`/empresas/${usuarioId}/ofertas/${ofertaId}`, { method: "DELETE" }),
};
