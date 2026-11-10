import sys
from pathlib import Path
sys.path.insert(0,str(Path('backend').resolve()))
from scripts.seed_jobs import reset_sql
Path('.vercel/reset-empresas-v2.sql').write_text(reset_sql('branchit_backup_20261018_reset_v2',{'empresas':13,'egresados':2,'ofertas':101,'postulaciones':3,'archivos_empresa':2}),encoding='utf-8')
print('SQL final preparado con comprobación de cantidades y respaldo privado.')
