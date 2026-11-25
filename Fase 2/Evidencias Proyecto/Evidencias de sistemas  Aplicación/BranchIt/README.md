# BranchIT · Aplicación

- `frontend/`: interfaz React y funciones de archivos de Vercel.
- `backend/`: API FastAPI, modelos, migraciones, scripts y pruebas.
- [Documentación técnica](docs/DESPLIEGUE_VERCEL.md): ejecución, variables y despliegue.
- [Sprints y evidencias](sprints/README.md).
- [Documentación académica](../Evidencias%20de%20documentacion/README.md).
- [Base de datos y diagrama](../Base%20de%20datos/README.md).
- [Presentación de avance](../Presentacion%20Proyecto.pptx).

Para Vercel, las raíces siguen siendo `Fase 2/Evidencias Proyecto/BranchIt/frontend` y `Fase 2/Evidencias Proyecto/BranchIt/backend`. Las migraciones se mantienen en `backend/migrations`.

Las dependencias, variables privadas y temporales no son entregables académicos y siguen fuera de Git según las reglas existentes.

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
