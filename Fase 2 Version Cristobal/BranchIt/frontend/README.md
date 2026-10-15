<<<<<<< Updated upstream
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.
=======
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
>>>>>>> Stashed changes
