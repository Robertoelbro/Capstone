const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const getToken = () => sessionStorage.getItem("branchit-token");
export const setToken = (token) =>
  sessionStorage.setItem("branchit-token", token);
export const clearToken = () => sessionStorage.removeItem("branchit-token");

async function solicitud(path, options = {}) {
  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
      },
      ...options,
    });
  } catch {
    throw new Error(
      "No pudimos conectar con BranchIT. Inténtalo nuevamente en unos momentos.",
    );
  }

  if (!res.ok) {
    const cuerpo = await res.json().catch(() => ({}));
    if (res.status === 401 && path !== "/auth/login")
      window.dispatchEvent(new Event("session-expired"));
    const message = Array.isArray(cuerpo.detail)
      ? "Revisa los campos ingresados. Hay datos incompletos o fuera del formato permitido."
      : cuerpo.detail;
    throw new Error(
      message || "No pudimos completar la solicitud. Inténtalo nuevamente.",
    );
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  logout: () => solicitud("/auth/logout", { method: "POST" }),
  companySummary: (id) => solicitud(`/empresas/${id}/resumen`),
  job: (id) => solicitud(`/api/employment/jobs/${id}`),
  apply: (data) =>
    solicitud("/api/employment/applications", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  myApplications: () => solicitud("/api/employment/applications/me"),
  applicants: (id) => solicitud(`/api/employment/jobs/${id}/applications`),
  crearPresentacion: (id, presentacion) =>
    solicitud(`/egresados/${id}/presentacion`, {
      method: "POST",
      body: JSON.stringify({ presentacion }),
    }),
  eliminarPresentacion: (id) =>
    solicitud(`/egresados/${id}/presentacion`, { method: "DELETE" }),
  login: (data) =>
    solicitud("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  me: () => solicitud("/auth/me"),
  jobs: () => solicitud("/api/employment/jobs"),
  registrarEgresado: (datos) =>
    solicitud("/auth/registro/egresado", {
      method: "POST",
      body: JSON.stringify(datos),
    }),

  registrarEmpresa: (datos) =>
    solicitud("/auth/registro/empresa", {
      method: "POST",
      body: JSON.stringify(datos),
    }),

  obtenerPerfilEgresado: (usuarioId) => solicitud(`/egresados/${usuarioId}`),

  actualizarPerfilEgresado: (usuarioId, datos) =>
    solicitud(`/egresados/${usuarioId}`, {
      method: "PUT",
      body: JSON.stringify(datos),
    }),

  eliminarCuentaEgresado: (usuarioId) =>
    solicitud(`/egresados/${usuarioId}`, { method: "DELETE" }),

  ofertasParaEgresado: (usuarioId) =>
    solicitud(`/egresados/${usuarioId}/ofertas`),

  listarMisOfertas: (usuarioId) => solicitud(`/empresas/${usuarioId}/ofertas`),

  crearOferta: (usuarioId, datos) =>
    solicitud(`/empresas/${usuarioId}/ofertas`, {
      method: "POST",
      body: JSON.stringify(datos),
    }),

  actualizarOferta: (usuarioId, ofertaId, datos) =>
    solicitud(`/empresas/${usuarioId}/ofertas/${ofertaId}`, {
      method: "PUT",
      body: JSON.stringify(datos),
    }),

  eliminarOferta: (usuarioId, ofertaId) =>
    solicitud(`/empresas/${usuarioId}/ofertas/${ofertaId}`, {
      method: "DELETE",
    }),
};
