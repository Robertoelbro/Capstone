# Sprints 4, 5 y 6

Alcance tomado de la sección 8 de la guía APT entregada por el usuario.
La revisión inicial se realizó antes de implementar estos sprints y está en
[VERIFICACION_PREVIA.md](VERIFICACION_PREVIA.md).

| Sprint | Egresado | Empresa | Verificación |
| --- | --- | --- | --- |
| [4](sprint_4/README.md) | Login y hub con resumen, presentación y postulaciones | Login y hub con ofertas abiertas y postulaciones recibidas | Login de ambos roles y navegación en navegador |
| [5](sprint_5/README.md) | Crear, leer, editar y eliminar presentación; consultar ofertas | Crear, leer, editar, cerrar y eliminar ofertas sin postulaciones | Pruebas API y creación/edición visual |
| [6](sprint_6/README.md) | Formulario dinámico, consentimiento, envío e historial | Preguntas por oferta y consulta privada de postulantes | Recorrido completo y pruebas de seguridad |

## Resultado de validación

- `npm run lint`: aprobado.
- `npm run build`: aprobado.
- `python -m unittest discover -s tests -v`: 16 pruebas aprobadas.
- Migración de una base con datos previos a `0002_postulaciones`, comparación
  del esquema con los modelos y reversión a `0001`: aprobadas en SQLite aislado.
- SQL generado para PostgreSQL: comprobado sin conectarse a una base real.
- Navegador: login de egresado, guardar presentación, abrir oferta, responder
  preguntas, enviar postulación; login de empresa, ver los antecedentes,
  crear una oferta con selección personalizada, cerrarla y cerrar sesión.
- Las capturas en cada carpeta son evidencias de una sesión con datos ficticios.

## Pendiente del entorno real

PostgreSQL local no estaba disponible. Estas evidencias certifican el código
y el recorrido en una base temporal, no una ejecución contra PostgreSQL ni un
despliegue. Antes de usar datos reales hay que iniciar/configurar PostgreSQL,
conservar las claves y ejecutar `alembic upgrade head` desde `backend`.

## Vista de prueba reproducible

Terminal 1, desde `backend`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe scripts/preview_sprints.py
```

Terminal 2, desde `frontend`:

```powershell
$env:VITE_API_URL='http://127.0.0.1:8001'
$env:VITE_DEMO_MODE='true'
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

Abrir `http://127.0.0.1:5174`. Cuentas ficticias y exclusivas de esta vista:

| Rol | Correo | Contraseña de prueba |
| --- | --- | --- |
| Egresado | egresado@example.com | EgresadoDemo2026! |
| Empresa | empresa@example.com | EmpresaDemo2026! |

El script usa una base SQLite temporal, claves aleatorias de proceso y escucha
solo en loopback. No modifica `.env` ni PostgreSQL. Los datos desaparecen al
cerrar el proceso normalmente. No utilizar este script para producción.

## Fuera de alcance

IA, seguimiento de contratación, recuperación de contraseña, cierre definitivo
de cuentas y hosting corresponden a otras tareas o sprints. Las postulaciones
tienen estado «recibida»; no se simulan decisiones de contratación.
