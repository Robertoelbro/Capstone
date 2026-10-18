"""Transparent job-related matches; no personal or protected attributes are scored."""
import re
from .careers import normalize, recommendation


def affinity(job, career, portfolio):
    text = normalize(' '.join([job.titulo, job.descripcion or '', job.requisitos or '', job.funciones or '']))
    names = [s['nombre'] for s in portfolio.get('habilidades', [])]
    names += [t for p in portfolio.get('proyectos', []) for t in p.get('tecnologias', [])]
    unique = {normalize(n).strip(): n for n in names if n.strip()}
    matches = [label for key, label in sorted(unique.items())
               if re.search(r'(?<!\w)' + re.escape(key) + r'(?!\w)', text)]
    career_match = recommendation(job, career)['afin']
    return {'puntos': (20 if career_match else 0) + min(80, 40 * len(matches)),
            'coincidencias': matches, 'carrera_afin': career_match}
