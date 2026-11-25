"""Reviewed official resources. URLs are supplied by the server, never invented by the model."""
from .careers import normalize
import re

CATALOG = (
    {
        'nombre': 'freeCodeCamp', 'url': 'https://www.freecodecamp.org/learn/',
        'temas': ['python', 'javascript', 'react', 'sql', 'programacion', 'desarrollo web', 'html', 'css', 'c#', 'backend', 'frontend'],
        'curso': 'Gratuito', 'credencial': 'Certificaciones gratuitas de su plataforma',
        'nota': 'Completa los requisitos de cada certificación. No equivale a un título profesional.',
        'fuente': 'https://github.com/freeCodeCamp/freeCodeCamp/blob/main/README.md',
    },
    {
        'nombre': 'IBM SkillsBuild', 'url': 'https://skillsbuild.org/adult-learners',
        'temas': ['inteligencia artificial', 'datos', 'ciberseguridad', 'tecnologia', 'digital', 'comunicacion', 'habilidades profesionales'],
        'curso': 'Gratuito', 'credencial': 'Credenciales digitales en los itinerarios que las ofrecen',
        'nota': 'Revisa qué itinerarios otorgan credencial y sus requisitos de finalización.',
        'fuente': 'https://skillsbuild.org/adult-learners',
    },
    {
        'nombre': 'HP LIFE', 'url': 'https://www.life-global.org/',
        'temas': ['negocios', 'administracion', 'finanzas', 'marketing', 'ventas', 'emprendimiento', 'comunicacion', 'presentaciones', 'atencion al cliente'],
        'curso': 'Gratuito', 'credencial': 'Certificado de finalización gratuito',
        'nota': 'Es un certificado de finalización de curso, no una licencia ni una certificación profesional regulada.',
        'fuente': 'https://www.life-global.org/',
    },
)


def recommend_certifications(text):
    value = normalize(text)
    ranked = []
    for index, resource in enumerate(CATALOG):
        matches = [topic for topic in resource['temas']
                   if re.search(r'(?<!\w)' + re.escape(topic) + r'(?!\w)', value)]
        if matches:
            ranked.append((len(matches), index, resource, 'Para reforzar: ' + ', '.join(matches[:3]) + '.'))
    if not ranked:
        # Be explicit about scope when the catalog has no technical resource for
        # the occupation (for example, a clinical or legally regulated profession).
        ranked = [(0, 1, CATALOG[1], 'Habilidades digitales y profesionales transversales.'),
                  (0, 2, CATALOG[2], 'Comunicación y negocios como complemento de tu formación.')]
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [dict(resource, motivo=reason, revision='2026-10') for _, _, resource, reason in ranked[:3]]


def requests_training(message):
    return bool(re.search(r'certific|credencial|curso|capacit|aprender|formacion', normalize(message)))
