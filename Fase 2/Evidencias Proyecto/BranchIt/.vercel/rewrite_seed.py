from pathlib import Path
p=Path('backend/scripts/seed_jobs.py');s=p.read_text(encoding='utf-8');a=s.index('\ndef jobs():');s=s[:a];p.write_text(s,encoding='utf-8')
