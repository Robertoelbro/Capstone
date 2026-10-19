# Mapa tecnológico de BranchIT

Generado el 19 de octubre de 2026 a partir de las dependencias y configuración actuales del proyecto. Inspirado en la referencia visual proporcionada por el usuario, con BranchIT al centro y bloques por área.

Archivos:
- `branchit-mapa-tecnologico.png`: imagen para presentaciones.
- `branchit-mapa-tecnologico.svg`: vector editable y ampliable sin pérdida de calidad.

El mapa muestra herramientas principales y auxiliares usadas directamente, no todas las dependencias transitivas de Python y Node. El código de la interfaz está escrito en JavaScript/JSX. FastAPI es la API principal; las funciones JavaScript de Vercel se ocupan de los archivos. PostgreSQL guarda datos y metadatos en Neon; Vercel Blob guarda los archivos. SQLite se usa en pruebas, no como base de producción. Gemini se consume mediante su API; no se entrena un modelo propio.

WCAG 2.1 es un lineamiento de accesibilidad aplicado a la interfaz, no una biblioteca ni un servicio. Los sitios recomendados para certificarse son recursos externos y no forman parte del stack de ejecución.

Las líneas del mapa indican pertenencia al proyecto, no flujos de red. El flujo principal se muestra en la nota inferior.
