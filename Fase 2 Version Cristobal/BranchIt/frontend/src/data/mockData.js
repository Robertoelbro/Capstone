// Datos de ejemplo para maquetar las pantallas (Home y Perfil).
// Cuando el backend exponga estos recursos reales (ofertas, proyectos,
// conexiones, etc.), este archivo se reemplaza por llamadas a la API,
// igual como ya se hizo con el registro de usuarios.

export const usuarioActual = {
  nombre: "Usuario",
  titulo: "Ingeniero en Informática | Recién Egresado",
  ubicacion: "Santiago, Chile",
  bio: "Apasionado por la tecnología y los datos. Siempre aprendiendo y buscando nuevos desafíos.",
  crecimiento: 35,
};

export const recomendacionesIA = [
  { id: 1, cargo: "Practica Backend", empresa: "Falabella" },
  { id: 2, cargo: "Analista Junior", empresa: "BCI" },
  { id: 3, cargo: "QA Junior", empresa: "Globant" },
];

export const compatibilidadIA = 92;

export const proyectosComunidad = [
  {
    id: 1,
    titulo: "Sistema de Inventario",
    autor: "Juan Perez",
    descripcion:
      "Aplicación web para gestión de inventario con roles y reportes en tiempo real.",
    tags: ["Python", "React", "PostgreSQL"],
    vistas: 12,
    likes: 4,
  },
  {
    id: 2,
    titulo: "App Tareas Colaborativas",
    autor: "Valentina Rojas",
    descripcion:
      "Organiza tareas en equipo con tableros kanban y notificaciones.",
    tags: ["JavaScript", "NodeJS", "MongoDB"],
    vistas: 8,
    likes: 3,
  },
];

export const tipsCrecimiento = [
  { id: 1, titulo: "Completa tu perfil", detalle: "35% Completado" },
  { id: 2, titulo: "Añade habilidades", detalle: "+5% Crecimiento" },
  { id: 3, titulo: "Sube un proyecto", detalle: "+10% de crecimiento" },
];

export const actividadReciente = [
  { id: 1, titulo: "Red Salud UC CHRISTUS", detalle: "Revisó tu postulación", cuando: "Hoy" },
  { id: 2, titulo: "Papa Johns", detalle: "Vio tu perfil", cuando: "Ayer" },
  { id: 3, titulo: "GoToPoint", detalle: "Te envió un mensaje", cuando: "18 de agosto" },
];

export const ofertasRecomendadas = [
  {
    id: 1,
    inicial: "B",
    color: "bg-blue-600",
    cargo: "Desarrollador Junior Full Stack",
    empresa: "Betterfly",
    ubicacion: "Santiago, RM",
    modalidad: "Remoto",
  },
  {
    id: 2,
    inicial: "W",
    color: "bg-violet-600",
    cargo: "Analista de Datos Junior",
    empresa: "WOM",
    ubicacion: "Providencia, RM",
    modalidad: "Híbrido",
  },
  {
    id: 3,
    inicial: "M",
    color: "bg-amber-500",
    cargo: "Práctica Marketing Digital",
    empresa: "Mercado Pago",
    ubicacion: "Santiago, RM",
    modalidad: "Presencial",
  },
];

export const habilidades = [
  { id: 1, nombre: "Python", nivel: 90, etiqueta: "Avanzado" },
  { id: 2, nombre: "JavaScript", nivel: 65, etiqueta: "Intermedio" },
  { id: 3, nombre: "SQL", nivel: 60, etiqueta: "Intermedio" },
  { id: 4, nombre: "React", nivel: 60, etiqueta: "Intermedio" },
  { id: 5, nombre: "Git", nivel: 60, etiqueta: "Intermedio" },
];

export const estadisticas = [
  { id: 1, valor: 15, etiqueta: "Conexiones" },
  { id: 2, valor: 2, etiqueta: "Proyectos" },
  { id: 3, valor: 8, etiqueta: "Habilidades" },
];

export const guardadosTotal = 3;

export const ramasArbol = [
  { id: "educacion", titulo: "Educación", detalle: "Ingeniería civil informática · 2023" },
  { id: "proyectos", titulo: "Proyectos", detalle: "2 proyectos publicados" },
  { id: "habilidades", titulo: "Habilidades", detalle: "6 habilidades registradas" },
  { id: "conexiones", titulo: "Conexiones", detalle: "15 conexiones" },
];

export const misProyectos = [
  {
    id: 1,
    titulo: "Sistema de inventario",
    descripcion: "Aplicación Web para gestión de inventario con roles y reportes en tiempo real.",
    tags: ["Python", "React", "PostgreSQL"],
  },
  {
    id: 2,
    titulo: "App Tareas Colaborativas",
    descripcion: "Organización tareas en equipo con tableros Kanban y notificaciones.",
    tags: ["JavaScript", "NodeJS", "MongoDB"],
  },
];
