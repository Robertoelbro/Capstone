from pathlib import Path
p=Path('frontend/src/pages/Auth.jsx'); s=p.read_text(encoding='utf-8')
s=s.replace('  FiBriefcase,\n','').replace('  FiCheck,\n','').replace('  FiLayers,\n','')
s=s.replace('export default function Auth()', 'import { ValidatedForm, SearchField, PhoneField, RutField } from "../Components/FormFields";\nimport { careers, industries } from "../data/catalogs";\n\nexport default function Auth()')
a=s.index('      <aside className="auth-story">'); b=s.index('      <div className="auth-form-panel">',a); s=s[:a]+s[b:]
a=s.index('        <span className="eyebrow">');b=s.index('        {registering && (',a)
s=s[:a]+'        <h1>{registering ? "Crear cuenta" : "Iniciar sesión"}</h1>\n'+s[b:]
s=s.replace('<form onSubmit={submit}', '<ValidatedForm key={`${registering}-${role}`} onSubmit={submit}').replace('</form>','</ValidatedForm>')
a=s.index('          {registering && <p id="register-help"');b=s.index('\n          {registering &&',a+20)
s=s[:a]+'          {registering && <p id="register-help" className="muted">* Obligatorio. Contraseña: al menos 8 caracteres.</p>}'+s[b:]
a=s.index('                  <label>\n                    Carrera de egreso'); b=s.index('                  <label>\n                    Año de egreso',a)
s=s[:a]+'                  <SearchField label="Carrera de egreso" name="carrera" options={careers} required />\n'+s[b:]
s=s.replace('type="number"\n                      min="1900"\n                      max="2100"','type="text" inputMode="numeric" pattern="(19|20)[0-9]{2}|2100" maxLength={4}')
a=s.index('                <label>\n                  Giro comercial');b=s.index('\n              </>',a)
s=s[:a]+'                <SearchField label="Giro comercial" name="rubro" options={industries} required />'+s[b:]
a=s.index('                <label>RUT ');b=s.index('\n              </div>',a)
s=s[:a]+'                <RutField label={role === "empresa" ? "RUT de la empresa" : "RUT personal"} />\n                <PhoneField required />'+s[b:]
s=s.replace('className="auth-layout"','className="auth-layout auth-layout-compact"')
p.write_text(s,encoding='utf-8')
p=Path('frontend/src/pages/OfertasEmpresa.jsx');s=p.read_text(encoding='utf-8')
s=s.replace('const OFERTA_VACIA', 'import { ValidatedForm, MoneyField, SearchField } from "../Components/FormFields";\nimport { careers } from "../data/catalogs";\n\nconst OFERTA_VACIA')
s=s.replace('  categoria: "General",','  sueldo: "", funciones: "", perfiles_deseados: [], condiciones_laborales: "", adaptada_discapacidad: "",\n  categoria: "General",',1)
s=s.replace('      categoria: oferta.categoria', '      sueldo: oferta.sueldo || "", funciones: oferta.funciones || "", perfiles_deseados: oferta.perfiles_deseados || [], condiciones_laborales: oferta.condiciones_laborales || "", adaptada_discapacidad: oferta.adaptada_discapacidad == null ? "" : String(oferta.adaptada_discapacidad),\n      categoria: oferta.categoria')
s=s.replace('        ...base,','        ...base,\n        sueldo: Number(base.sueldo),\n        adaptada_discapacidad: base.adaptada_discapacidad === "true",')
s=s.replace('      <form\n','      <ValidatedForm\n        key={editandoId || "new"}\n').replace('      </form>','      </ValidatedForm>').replace('maxWidth: 560','maxWidth: 880')
s=s.replace('<label htmlFor="descripcion">Descripción</label>','<label htmlFor="descripcion">Información del cargo</label>')
needle='          <QuestionEditor'
a=s.index(needle)
s=s[:a]+'''          <MoneyField value={form.sueldo} onChange={(v) => actualizar("sueldo", v)} />
          <label className="editor-field">Funciones del cargo<textarea required maxLength={10000} rows={4} value={form.funciones} onChange={(e) => actualizar("funciones", e.target.value)} /></label>
          <fieldset>
            <legend>Perfiles deseados *</legend>
            <div className="desired-careers">{form.perfiles_deseados.map((v) => <button type="button" key={v} aria-label={`Quitar ${v}`} onClick={() => actualizar("perfiles_deseados", form.perfiles_deseados.filter((item) => item !== v))}>{v} ×</button>)}</div>
            {form.perfiles_deseados.length < 20 && <SearchField key={form.perfiles_deseados.length} label="Añadir carrera" options={careers} required={!form.perfiles_deseados.length} onChange={(v) => { if (v && !form.perfiles_deseados.includes(v)) actualizar("perfiles_deseados", [...form.perfiles_deseados, v]); }} />}
          </fieldset>
          <label className="editor-field">Condiciones laborales<textarea required rows={4} maxLength={10000} value={form.condiciones_laborales} onChange={(e) => actualizar("condiciones_laborales", e.target.value)} /></label>
          <label className="editor-field">¿El cargo contempla adaptaciones para personas con discapacidad?
            <select required value={form.adaptada_discapacidad} onChange={(e) => actualizar("adaptada_discapacidad", e.target.value)}>
              <option value="">Seleccionar</option><option value="true">Sí</option><option value="false">No</option>
            </select>
          </label>
''' +s[a:]
p.write_text(s,encoding='utf-8')
p=Path('frontend/src/Components/QuestionEditor.jsx');s=p.read_text(encoding='utf-8')
a=s.index('      <p className="muted">');b=s.index('      {questions.map',a);s=s[:a]+s[b:]
s=s.replace('opciones: [] })','opciones: ["seleccion", "seleccion_multiple"].includes(e.target.value) ? ["", ""] : [] })')
s=s.replace('<option value="texto">Texto corto</option>','<option value="texto">Texto corto (200 caracteres)</option>').replace('<option value="parrafo">Texto largo</option>','<option value="parrafo">Texto largo (3.000 caracteres)</option>')
s=s.replace('<option value="seleccion">Selección</option>','<option value="seleccion">Una opción</option>\n              <option value="seleccion_multiple">Varias opciones</option>')
a=s.index('          {q.tipo === "seleccion"');b=s.index('          <label className="consent">',a)
s=s[:a]+'''          {["seleccion", "seleccion_multiple"].includes(q.tipo) && (
            <div className="choice-options">
              {q.opciones.map((option, optionIndex) => <div className="choice-option" key={optionIndex}>
                <label className="editor-field">Opción {optionIndex + 1}<input required maxLength={100} value={option} onChange={(e) => update(q.id, { opciones: q.opciones.map((v, i) => i === optionIndex ? e.target.value : v) })} /></label>
                <button type="button" disabled={q.opciones.length <= 2} aria-label={`Quitar opción ${optionIndex + 1} de pregunta ${index + 1}`} onClick={() => update(q.id, { opciones: q.opciones.filter((_, i) => i !== optionIndex) })}>Quitar</button>
              </div>)}
              <button type="button" className="boton boton-secundario" disabled={q.opciones.length >= 15} onClick={() => update(q.id, { opciones: [...q.opciones, ""] })}>Agregar opción</button>
            </div>
          )}
''' +s[b:]
p.write_text(s,encoding='utf-8')
