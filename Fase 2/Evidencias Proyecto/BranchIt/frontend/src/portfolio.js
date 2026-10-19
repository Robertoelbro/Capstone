export const emptyPortfolio = {
  titular: "",
  ubicacion: "",
  contacto_email: "",
  contacto_telefono: "",
  disponibilidad: "Sin definir",
  foto_id: null,
  video_id: null,
  video_url: "",
  github_url: "",
  titulo_url: "",
  experiencia_laboral: [],
  habilidades: [],
  certificaciones: [],
  proyectos: [],
  publico: false,
  mostrar_email: false,
  mostrar_telefono: false,
  tema: "bosque",
};
export function growth(profile) {
  const p = { ...emptyPortfolio, ...profile?.portfolio };
  const steps = [
    ["Presentación", !!profile?.presentacion],
    ["Carrera", !!profile?.carrera],
    ["Foto", !!(p.foto_id || profile?.foto_url)],
    ["Habilidades", !!p.habilidades.length],
    ["Proyecto", !!p.proyectos.length],
    ["Certificaciones", !!p.certificaciones.length],
    ["Video de presentación", !!(p.video_id || p.video_url)],
    ["Disponibilidad", p.disponibilidad !== "Sin definir"],
  ];
  return {
    steps,
    percent: Math.round(
      (steps.filter(([, done]) => done).length / steps.length) * 100,
    ),
  };
}
export const normalize = (value) =>
  (value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
