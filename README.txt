BranchIt

BranchIt es una plataforma online de postulaciones laborales enfocada en los profesionales sin experiencia en sus respectivas áreas, donde las empresas pueden generar ofertas laborales a las que los demás usuarios (no empresas) pueden postular. Adicionalmente se le hace entrega a los profesionales de un chatbot potenciado por IA para que puedan hacer práctica de entrevistas laborales y estar mejor preparados para estas situaciones.

Para la elaboración de BranchIt se utilizaron diversas tecnologías, dentro de estas se encuentran Vercel, Neon, API Google Gemini, HTML, CSS, JavaScript, FastAPI y Node.js.

Para poder ejecutar el servicio de forma local hay que seguir las siguientes instrucciones:

Primero, levantar Backend:

	Set-Location -LiteralPath "...\Evidencias Proyecto\BranchIt\backend"

	..venv\Scripts\python.exe -m pip install -r requirements-dev.txt

	..venv\Scripts\python.exe scripts/preview_sprints.py

Segundo, levantar Frontend

	Set-Location -LiteralPath "...\Evidencias Proyecto\BranchIt\frontend"

	$env:VITE_API_URL='http://127.0.0.1:8001/'
	$env:VITE_DEMO_MODE='true'

	npm.cmd run dev -- --host 127.0.0.1 --port 5174 --strictPort

Realizando ambos levantamientos se puede acceder al servicio.

El equipo de desarrollo corresponde a Cristóbal Lara, Roberto Orrego y Matías Werner. Donde Cristóbal y Matías están designados como desarrolladores y Roberto es Scrum Master y Product Owner.

Para el desarrollo del proyecto se utilizó la metodología Scrum repartiendo el trabajo de desarrollo en distintos sprints, siguiendo a la vez una arquitectura de tres capas, teniendo capa de presentación (frontend), capa de negocio (backend) y la capa de datos (base de datos SQL).