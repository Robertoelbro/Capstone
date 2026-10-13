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
    const fieldNames = { email: "Correo electrónico", password: "Contraseña", rut: "RUT", telefono: "Teléfono", fecha_identidad: "Fecha", carrera: "Carrera", rubro: "Giro comercial", nombre: "Nombre", apellido: "Apellido", nombre_empresa: "Nombre de empresa" };
    const message = Array.isArray(cuerpo.detail)
      ? cuerpo.detail.map((item) => {
          const field = item.loc?.filter((part) => part !== "body").join(" · ");
          const label = fieldNames[field] || field || "Formulario";
          const detail = item.msg?.startsWith("Value error, ")
            ? item.msg.slice(13) : "Revisa este campo: es obligatorio y debe tener un formato válido.";
          return `${label}: ${detail}`;
        }).join(" ")
      : cuerpo.detail;
    throw new Error(
      message || "No pudimos completar la solicitud. Inténtalo nuevamente.",
    );
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  companyProfile: (id) => solicitud(`/empresas/${id}/perfil`),
  saveCompanyProfile: (id, data) => solicitud(`/empresas/${id}/perfil`, {method: "PUT", body: JSON.stringify(data)}),
  changePassword: (data) => solicitud("/auth/password", {method: "POST", body: JSON.stringify(data)}),
  recommendations: (id) => solicitud(`/egresados/${id}/recomendaciones`),
  publicPortfolio: (id) => solicitud(`/portfolio/${id}`),
  savePortfolio: (data) =>
    solicitud("/portfolio/me", { method: "PUT", body: JSON.stringify(data) }),
  reserveMedia: (data) =>
    solicitud("/media/reserve", { method: "POST", body: JSON.stringify(data) }),
  mediaLibrary: () => solicitud("/media/library"),
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
