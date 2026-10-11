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
    ["Tu historia", !!profile?.presentacion],
    ["Tu formación", !!profile?.carrera],
    ["Una foto tuya", !!(p.foto_id || profile?.foto_url)],
    ["Tus habilidades", !!p.habilidades.length],
    ["Tu primer proyecto", !!p.proyectos.length],
    ["Certificaciones", !!p.certificaciones.length],
    ["Preséntate en video", !!(p.video_id || p.video_url)],
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
