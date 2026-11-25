"""Explainable rule-based suggestions, not an AI ranking or hiring assessment."""
import unicodedata
import re

AREAS = {
    'Tecnología': ['informatica','computacion','software','programacion','ciberseguridad','analista programador','sistemas','redes','telecomunicaciones'],
    'Salud': ['enfermeria','medicina','kinesiologia','nutricion','odontologia','terapia ocupacional','salud','fonoaudiologia','tecnologia medica','obstetricia'],
    'Administración y finanzas': ['administracion','contabilidad','contador','finanzas','ingenieria comercial','auditoria','recursos humanos'],
    'Diseño y comunicación': ['diseno','publicidad','periodismo','comunicacion','audiovisual','artes visuales','marketing'],
    'Educación': ['pedagogia','educacion','parvulos','educador','bibliotecologia'],
    'Ingeniería y construcción': ['construccion','arquitectura','ingenieria civil','ingenieria mecanica','electricidad','ingenieria electrica'],
    'Logística y operaciones': ['logistica','comercio exterior','transporte','ingenieria industrial','operaciones'],
    'Turismo y gastronomía': ['turismo','gastronomia','hoteleria','cocina'],
    'Ciencias sociales': ['psicologia','trabajo social','sociologia','derecho','antropologia'],
    'Medioambiente y agro': ['agronomia','medioambiente','ambiental','forestal','veterinaria','biologia'],
}

def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value or '') if not unicodedata.combining(c)).lower()

def career_area(career):
    value = normalize(career)
    # Prefer the most specific phrase. Civil informática belongs to technology.
    if any(word in value for word in AREAS['Tecnología']): return 'Tecnología'
    matches = [(len(word), area) for area, words in AREAS.items() for word in words if word in value]
    return max(matches)[1] if matches else None

def job_area(job):
    if job.categoria in AREAS: return job.categoria
    return career_area(job.titulo + ' ' + (job.requisitos or ''))

def recommendation(job, career):
    area = career_area(career)
    desired = job.perfiles_deseados or []
    profile_match = bool(career and desired and any(
        normalize(career).strip() == normalize(profile).strip() or
        (area and career_area(profile) == area) for profile in desired))
    match = profile_match if desired else bool(area and job_area(job) == area)
    if profile_match:
        return {'afin': True, 'motivo': 'Tu carrera coincide con los perfiles o áreas solicitadas.', 'area_carrera': area}
    return {'afin':match, 'motivo':f'Coincide con el área de tu carrera: {area}.' if match else
            'Explora esta oportunidad y revisa sus requisitos.', 'area_carrera':area}
