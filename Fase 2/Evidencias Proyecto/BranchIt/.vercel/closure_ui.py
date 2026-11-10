from pathlib import Path
p=Path('frontend/src/Components/FormFields.jsx');s=p.read_text(encoding='utf-8');s='import CountryPrefix from "./CountryPrefix";\n'+s
s=s.replace('const countries = getCountries()', 'const countries = getCountries()')
a=s.index('function splitPhone(value)');s=s[:a]+'''const phoneOptions = [{value:"CL-mobile", code:"CL", name:"Chile móvil", prefix:"+569"}, ...countries.map((item) => ({value:item.code, code:item.code, name:names.of(item.code), prefix:`+${getCountryCallingCode(item.code)}`}))];
'''+s[a:]
a=s.index('        <select\n          aria-label="País y prefijo telefónico"');b=s.index('        <input',a)
s=s[:a]+'        <CountryPrefix value={country} options={phoneOptions} onChange={(next) => change(next, number)} />\n'+s[b:];p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/OfertasEmpresa.jsx');s=p.read_text(encoding='utf-8');s=s.replace('import { Link }', 'import PropTypes from "prop-types";\nimport JobClosure from "../Components/JobClosure";\nimport { Link, useNavigate, useLocation }')
s=s.replace('export default function OfertasEmpresa() {','export default function OfertasEmpresa({ creating = false }) {\n  const navigate = useNavigate();\n  const location = useLocation();')
s=s.replace('useState("");\n  const [careerCandidate','useState(location.state?.message || "");\n  const [careerCandidate',1)
s=s.replace('      await cargarOfertas();\n    } catch (err) {', '      await cargarOfertas();\n      if (creating) navigate("/ofertas-empresa", {state:{message:"Oferta publicada."}});\n    } catch (err) {',1)
s=s.replace('<h1>Mis ofertas de empleo</h1>','<h1>{creating ? "Crear oferta laboral" : "Ofertas creadas"}</h1>\n      {!creating && !editandoId && <Link className="boton boton-primario" to="/ofertas-empresa/nueva">Crear oferta laboral</Link>}\n      {error && !editandoId && !creating && <p className="mensaje-error" role="alert">{error}</p>}')
s=s.replace('      <ValidatedForm\n','      {(creating || editandoId) && <ValidatedForm\n',1).replace('      </ValidatedForm>','      </ValidatedForm>}',1)
s=s.replace('      <div style={{ display: "grid", gap: "1rem" }}>','      {!creating && <div style={{ display: "grid", gap: "1rem", marginTop:"1.5rem" }}>')
s=s.replace('{!oferta.activa && " · inactiva"}','{oferta.activa ? " · Convocatoria abierta" : " · Convocatoria cerrada"}')
s=s.replace('<div style={{ display: "flex", gap: "0.5rem" }}>','<div className="offer-actions">')
s=s.replace('            </div>\n          </article>','            </div>\n            <JobClosure job={oferta} onSaved={async () => { await cargarOfertas(); setSuccess("Convocatoria cerrada. Selección guardada de forma privada."); }} />\n          </article>')
s=s.replace('      </div>\n    </div>','      </div>}\n    </div>')
s+='\nOfertasEmpresa.propTypes = { creating: PropTypes.bool };\n';p.write_text(s,encoding='utf-8')
p=Path('frontend/src/App.jsx');s=p.read_text(encoding='utf-8').replace('"/ofertas-empresa": "Gestionar ofertas",','"/ofertas-empresa": "Ofertas creadas", "/ofertas-empresa/nueva": "Crear oferta laboral",');s=s.replace('          <Route\n            path="/ofertas-empresa"','          <Route path="/ofertas-empresa/nueva" element={<Protected role="empresa"><OfertasEmpresa key="create" creating /></Protected>} />\n          <Route\n            path="/ofertas-empresa"');s=s.replace('<OfertasEmpresa />','<OfertasEmpresa key="list" />');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/Components/WorkspaceNav.jsx');s=p.read_text(encoding='utf-8');s=s.replace('<NavLink to="/ofertas-empresa">Gestionar ofertas</NavLink>','<NavLink to="/ofertas-empresa/nueva">Crear oferta laboral</NavLink>\n        <NavLink to="/ofertas-empresa" end>Ver ofertas creadas</NavLink>');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/Dashboard.jsx');s=p.read_text(encoding='utf-8').replace('to={company ? "/ofertas-empresa" : "/perfil-egresado"}','to={company ? "/ofertas-empresa/nueva" : "/perfil-egresado"}').replace('"Gestionar ofertas"','"Crear oferta laboral"').replace('"Ver mis ofertas"','"Ver ofertas creadas"');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/api.js');s=p.read_text(encoding='utf-8').replace('  applicants: (id)', '  closeJob: (id, postulacion_id) => solicitud(`/api/employment/jobs/${id}/closure`, {method:"PUT",body:JSON.stringify({postulacion_id})}),\n  applicants: (id)');p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/Applications.jsx');s=p.read_text(encoding='utf-8').replace('<span className="status-badge">Recibida</span>','<span className="status-badge">{!item.oferta_activa ? "Convocatoria cerrada" : "Recibida"}</span>\n            {jobId && item.seleccionada && <span className="status-badge">Candidato seleccionado</span>}');p.write_text(s,encoding='utf-8')
