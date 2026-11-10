# BranchIt — Frontend

Plataforma que conecta a egresados con empresas que publican ofertas de empleo.
Proyecto de título, DuocUC.

## Pantallas disponibles

- **Inicio** (`/`): resumen "Para ti" con recomendaciones de BranchIt IA,
  proyectos destacados de la comunidad, actividad reciente y ofertas
  recomendadas.
- **Perfil** (`/perfil`): árbol profesional (educación, proyectos,
  habilidades, conexiones), habilidades, estadísticas y proyectos propios.
- El resto de los accesos del menú (Explorar empleos, Mis conexiones,
  Mensajes, Guardados, Notificaciones) muestran una pantalla "Próximamente"
  hasta que se diseñen esas vistas.

## Cómo correrlo

```
npm install
npm run dev
```

Se abre en `http://localhost:5173`.

## Nota sobre los datos

Las pantallas usan datos de ejemplo (`src/data/mockData.js`) para poder
mostrar el diseño completo. Todavía no están conectadas al backend —
eso es trabajo pendiente, igual como ya se hizo para el registro de
usuarios en el otro branch del backend.
