# Vista previa de Cristóbal

Origen: origin/Cristobal, commit b855856420b7a2c879ff868dff1652a88b3d67ca.

Copia local aislada, sin integración ni publicación en el branch remoto. Se resolvieron conflictos de Git en 10 archivos: se conservó la propuesta visual nueva del frontend y la configuración con routers/metadata del backend. Se añadieron las validaciones PropTypes faltantes y se comprobó la sintaxis de los archivos Python, el lint y la compilación del frontend.

Inicio: http://127.0.0.1:5180/
Perfil: http://127.0.0.1:5180/perfil

Es una maqueta con datos de ejemplo. No se ejecutó su backend ni se conectó a Neon. Los botones sin lógica y secciones Próximamente conservan el comportamiento de la propuesta original.

Para iniciarla nuevamente desde esta carpeta:

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5180 --strictPort
```

La carpeta node_modules es una unión a las dependencias ya instaladas del frontend principal. No ejecutar npm install en esta copia mientras se use esa unión. El package-lock conflictivo original no se copió. Esta carpeta está dentro de .vercel, ignorada por Git; no se despliega con el proyecto.
