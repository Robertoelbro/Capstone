from pathlib import Path
import re
for filename in ['index.css','garden.css']:
 p=Path('frontend/src')/filename;s=p.read_text(encoding='utf8')
 s=re.sub(r'font-size:\s*(\d+)px',lambda m:'font-size: '+('.875rem' if int(m[1])<14 else str(int(m[1])/16)+'rem'),s)
 # Darken muted text only; keep pale lettering used on dark backgrounds.
 def tone(m):
  h=m[1];v=[int(h[i:i+2],16)/255 for i in (0,2,4)]
  lum=sum(w*(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4) for w,c in zip([.2126,.7152,.0722],v))
  return 'color: #53634b' if .19<lum<.5 else m[0]
 s=re.sub(r'(?<![-\w])color: #(\w{6})(?!\w)',tone,s)
 p.write_text(s,encoding='utf8')
p=Path('frontend/src/App.jsx');s=p.read_text(encoding='utf8');s='import { useEffect, useRef } from "react";\n'+s;s=s.replace('  const location = useLocation();\n  return (','''  const location = useLocation();
  const previousPath = useRef(location.pathname);
  useEffect(() => {
    const titles = {
      "/": "Buscar empleo", "/ofertas": "Ofertas de empleo",
      "/iniciar-sesion": "Iniciar sesión", "/registro": "Registro de egresado",
      "/registro/empresa": "Registro de empresa", "/perfil-empresa": "Mi empresa",
      "/perfil-egresado": "Mi presentación", "/hub-empresa": "Panel de empresa",
      "/hub-egresado": "Panel de egresado", "/mis-postulaciones": "Mis postulaciones",
      "/ofertas-empresa": "Gestionar ofertas",
    };
    const title = titles[location.pathname] || (location.pathname.startsWith("/p/") ? "Portafolio profesional" : location.pathname.endsWith("/postular") ? "Postular a una oferta" : location.pathname.endsWith("/postulaciones") ? "Postulaciones recibidas" : "Página no encontrada");
    document.title = `${title} | BranchIT`;
    if (previousPath.current !== location.pathname) {
      document.getElementById("contenido")?.focus();
      previousPath.current = location.pathname;
    }
  }, [location.pathname]);
  return (''');s=s.replace('<main id="contenido">','<main id="contenido" tabIndex={-1}>');p.write_text(s,encoding='utf8')
p=Path('frontend/src/Components/Header/Header.jsx');s=p.read_text(encoding='utf8').replace('{ useState }','{ useState, useRef }');s=s.replace('  const { user, logout }', '  const menuButton = useRef(null);\n  const { user, logout }');s=s.replace('<nav className="contenedor nav-bar" aria-label="Navegación principal">','''<nav className="contenedor nav-bar" aria-label="Navegación principal" onKeyDown={(event) => {
        if (event.key === "Escape" && open) { setOpen(false); menuButton.current?.focus(); }
      }}>''');s=s.replace('className="mobile-toggle"','className="mobile-toggle"\n          ref={menuButton}\n          aria-controls="navigation-links"');s=s.replace('className={`nav-links','id="navigation-links"\n          className={`nav-links');p.write_text(s,encoding='utf8')
p=Path('frontend/src/pages/Home.jsx');s=p.read_text(encoding='utf8');s=s.replace('<span className="sr-only">Cargo o empresa</span>','<span className="search-label">Cargo o empresa</span>').replace('<span className="sr-only">Ciudad o región</span>','<span className="search-label">Ciudad o región</span>').replace('<span className="sr-only">Modalidad</span>','<span className="search-label">Modalidad</span>');s=s.replace('<span className="results-count">','<span className="results-count" role="status" aria-atomic="true">');s=s.replace('aria-expanded={selected === job.id}','aria-expanded={selected === job.id}\n                aria-controls={`job-detail-${job.id}`}\n                aria-label={`${selected === job.id ? "Cerrar detalle" : "Ver oportunidad"}: ${job.titulo}`}');s=s.replace('<div className="job-expanded">','<div className="job-expanded" id={`job-detail-${job.id}`}>');s=s.replace('.scrollIntoView({ behavior: "smooth" });','.scrollIntoView({ behavior: "auto" });');p.write_text(s,encoding='utf8')
p=Path('frontend/src/pages/Auth.jsx');s=p.read_text(encoding='utf8').replace('{ useState }','{ useState, useRef, useEffect }');s=s.replace('  const navigate = useNavigate();','''  const navigate = useNavigate();
  const errorRef = useRef(null);
  useEffect(() => { if (error) errorRef.current?.focus(); }, [error]);''');s=s.replace('<form onSubmit={submit} className="auth-form">','''<form onSubmit={submit} className="auth-form" aria-describedby={registering ? "register-help" : undefined} aria-busy={busy}>
          {registering && <p id="register-help" className="muted">Todos los campos son obligatorios salvo los marcados como opcionales. RUT con dígito verificador; teléfono de 8 a 15 dígitos. Contraseña de al menos 8 caracteres.</p>}''');s=s.replace('<p className="mensaje-error" role="alert">','<p ref={errorRef} tabIndex={-1} className="mensaje-error" role="alert">');s=s.replace('name="fecha_identidad" type="date"','name="fecha_identidad" autoComplete={role === "egresado" ? "bday" : "off"} type="date"');p.write_text(s,encoding='utf8')
