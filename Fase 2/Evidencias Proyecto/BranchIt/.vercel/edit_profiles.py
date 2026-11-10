from pathlib import Path
p=Path('backend/app/routers/portfolio.py');s=p.read_text().replace('PerfilEgresado, ArchivoPortfolio, Usuario','PerfilEgresado, PerfilEmpresa, ArchivoPortfolio, Usuario');s=s.replace("    own_profile(user, db)\n    limits", "    if user.tipo.value == 'empresa' and data.tipo != 'foto':\n        raise HTTPException(403, 'Las empresas pueden subir fotos de perfil.')\n    limits");s=s.replace('    own_profile(user, db)\n    return', '    return');s=s.replace("    public = profile and", "    company = db.query(PerfilEmpresa).filter_by(usuario_id=asset.usuario_id).first()\n    if remove and company and company.foto_id == asset_id:\n        raise HTTPException(409, 'Quita la foto del perfil y guarda antes de eliminarla.')\n    public = profile and");s=s.replace('    profile = own_profile(user, db)\n    asset = db.get', "    profile = db.query(PerfilEgresado).filter_by(usuario_id=user.id).first()\n    company = db.query(PerfilEmpresa).filter_by(usuario_id=user.id).first()\n    asset = db.get");s=s.replace("    if asset_id in {r[0] for r in media_references(profile.portfolio or {})}:", "    if (profile and asset_id in {r[0] for r in media_references(profile.portfolio or {})}) or (company and company.foto_id == asset_id):");p.write_text(s)
p=Path('frontend/src/pages/Auth.jsx');s=p.read_text().replace('Carrera <span>(opcional)</span>','Carrera de egreso').replace('name="carrera"','name="carrera"\n                      required').replace('Rubro <span>(opcional)</span>','Giro comercial').replace('name="rubro"','name="rubro"\n                    required');needle='''          <label>
            Correo electrónico''';s=s.replace(needle,'''          {registering && (
            <>
              <div className="form-row">
                <label>RUT {role === "empresa" ? "de la empresa" : "personal"}
                  <input name="rut" required maxLength={12} placeholder="12.345.678-5" autoComplete="off" />
                </label>
                <label>Teléfono
                  <input name="telefono" type="tel" required minLength={8} maxLength={30} autoComplete="tel" placeholder="+56 9 1234 5678" />
                </label>
              </div>
              <label>{role === "empresa" ? "Fecha de creación de la empresa" : "Fecha de nacimiento"}
                <input key={role} name="fecha_identidad" type="date" required max={new Date().toLocaleDateString("en-CA")} />
              </label>
            </>
          )}
'''+needle);p.write_text(s)
p=Path('frontend/src/Components/Header/Header.jsx');s=p.read_text().replace('className="brand" to="/"','className="brand" to={user ? panelPath(user) : "/"}');s=s.replace('<NavLink to="/">Buscar empleo</NavLink>','{user?.tipo !== "empresa" && <NavLink to="/">Buscar empleo</NavLink>}');p.write_text(s)
p=Path('frontend/src/Components/Footer/Footer.jsx');s=p.read_text().replace('export default function Footer() {','import { panelPath, useSession } from "../../session";\nexport default function Footer() {\n  const { user } = useSession();');s=s.replace('to="/" className="brand"','to={user ? panelPath(user) : "/"} className="brand"');s=s.replace('<Link to="/">Buscar empleo</Link>', '{user?.tipo === "empresa" ? <Link to="/perfil-empresa">Mi empresa</Link> : <Link to="/">Buscar empleo</Link>}');p.write_text(s)
p=Path('frontend/src/Components/WorkspaceNav.jsx');s=p.read_text().replace('<NavLink to="/ofertas-empresa">Gestionar ofertas</NavLink>','<>\n        <NavLink to="/ofertas-empresa">Gestionar ofertas</NavLink>\n        <NavLink to="/perfil-empresa">Mi empresa</NavLink>\n        </>');p.write_text(s)
p=Path('frontend/src/App.jsx');s=p.read_text().replace('import Home from', 'import PerfilEmpresa from "./pages/PerfilEmpresa";\nimport Home from');s=s.replace('<Route path="/p/:id"', '<Route path="/perfil-empresa" element={<Protected role="empresa"><PerfilEmpresa /></Protected>} />\n          <Route path="/p/:id"');p.write_text(s)
p=Path('frontend/src/pages/Home.jsx');s=p.read_text().replace('{ Link }','{ Link, Navigate }');s=s.replace('  return (\n    <>','  if (user?.tipo === "empresa") return <Navigate to="/hub-empresa" replace />;\n  return (\n    <>',1);p.write_text(s)
p=Path('frontend/src/api.js');s=p.read_text().replace('export const api = {','''export const api = {
  companyProfile: (id) => solicitud(`/empresas/${id}/perfil`),
  saveCompanyProfile: (id, data) => solicitud(`/empresas/${id}/perfil`, {method: "PUT", body: JSON.stringify(data)}),
  changePassword: (data) => solicitud("/auth/password", {method: "POST", body: JSON.stringify(data)}),''');p.write_text(s)
