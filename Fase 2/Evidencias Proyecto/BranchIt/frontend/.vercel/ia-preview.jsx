import React from 'react';
import {createRoot} from 'react-dom/client';
import GraduateAssistant from '../src/Components/GraduateAssistant';
import '../src/index.css';
import '../src/garden.css';
import '../src/accessibility.css';
createRoot(document.getElementById('root')).render(<div className="app-shell has-graduate-assistant"><main className="contenedor" style={{paddingTop:48}}><span className="eyebrow">VISTA LOCAL DEL COMPONENTE</span><h1 style={{fontSize:32,fontWeight:700}}>Tu próximo paso empieza aquí.</h1><p>Modo IA · BranchIT</p><a href="#contenido">Enlace de prueba de foco</a><section id="contenido">Tu espacio para crecer.</section></main><GraduateAssistant /></div>);
