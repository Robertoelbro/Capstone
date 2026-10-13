# Accesibilidad de BranchIT

Objetivo: WCAG 2.1 nivel AA. Esta revisión es parcial y no constituye una
certificación ni una declaración de conformidad de todas las páginas.
Referencia normativa: https://www.w3.org/TR/WCAG21/

## Cambios implementados

- Tipografía en rem; textos pequeños ampliados a 0,875 rem como mínimo en las
  hojas principales. WCAG no prescribe un tamaño mínimo: la ampliación facilita
  la lectura y el uso de las preferencias tipográficas del navegador.
- Colores secundarios más oscuros, foco de teclado con contorno y halo, bordes
  de campos visibles y enlaces de texto subrayados en los formularios.
- Buscador con etiquetas visibles; resultados anunciados como estado.
- Títulos por ruta, foco en contenido al navegar, destino enfocable para el
  enlace de salto, menú móvil con aria-controls y cierre con Escape.
- Errores de registro enfocados y anunciados; mensajes de validación identifican
  el campo. Instrucciones de registro, propósito de fecha de nacimiento y
  asociación de indicaciones de formato/tamaño con el selector de archivos.
- Ajustes de reflujo y soporte para movimiento reducido y colores forzados.

Criterios relacionados: 1.3.1, 1.3.5, 1.4.3, 1.4.4, 1.4.10, 1.4.11,
2.1.1, 2.4.1, 2.4.2, 2.4.3, 2.4.7, 3.3.1, 3.3.2 y 4.1.3.

## Verificaciones realizadas

- Compilación Vite y ESLint.
- Portada y registro a 320 píxeles: sin desbordamiento horizontal observado.
- Apertura del menú con Enter y cierre con Escape, devolviendo el foco al botón.
- Enlace de salto mueve el foco al contenido; navegación actualiza título y foco.
- Campos del registro con etiquetas asociadas y documento en español.

## Pendiente antes de afirmar conformidad AA

- Recorrer todos los flujos autenticados con NVDA/Firefox y VoiceOver/Safari.
- Medir contraste de todos los estados y temas, incluyendo texto sobre imágenes
  o degradados; una revisión de colores CSS no acredita todos los casos.
- Revisar zoom al 200 %, reflujo a 400 % y espaciado de texto personalizado en
  cada pantalla, incluidas ofertas extensas, bibliotecas y portafolios.
- Validar errores, acciones dinámicas y conservación del foco con tecnologías
  de asistencia; revisar vencimiento de sesión y conservación de formularios.
- Videos: implementar y verificar subtítulos y audiodescripción cuando
  corresponda. Los controles nativos del reproductor no satisfacen por sí solos
  los criterios de contenido multimedia. Revisar también documentos adjuntos.

No se modificaron CORS, la base de datos ni la configuración de despliegue.
