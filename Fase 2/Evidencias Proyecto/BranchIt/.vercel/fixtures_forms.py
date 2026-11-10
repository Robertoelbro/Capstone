from pathlib import Path
fields="'sueldo':850000,'funciones':'Desarrollar y mantener proyectos del equipo.','perfiles_deseados':['Ingeniería en Informática'],'condiciones_laborales':'Jornada completa, contrato de trabajo.','adaptada_discapacidad':True,"
p=Path('backend/tests/test_flows.py');s=p.read_text(encoding='utf-8');s=s.replace("payload = {'titulo': 'Desarrollador junior'", "payload = {"+fields+"'titulo': 'Desarrollador junior'");p.write_text(s,encoding='utf-8')
p=Path('backend/tests/test_sprints.py');s=p.read_text(encoding='utf-8').replace("payload = {'titulo': 'Primer empleo'","payload = {"+fields+"'titulo': 'Primer empleo'");p.write_text(s,encoding='utf-8')
p=Path('backend/tests/test_assistant.py');s=p.read_text(encoding='utf-8').replace("'titulo':'Backend junior'",fields+"'titulo':'Backend junior'");p.write_text(s,encoding='utf-8')
