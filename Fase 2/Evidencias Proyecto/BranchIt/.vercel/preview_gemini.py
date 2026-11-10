from pathlib import Path
import os,sys,json
from unittest.mock import patch,MagicMock
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
os.environ['GEMINI_API_KEY']='isolated-qa-key-not-real'
def fake_transport(request,**kwargs):
 payload=json.loads(request.data)
 task=payload['systemInstruction']['parts'][0]['text']
 history=payload['contents']
 if 'Simula una entrevista' in task:
  text='¿Cómo diseñarías la validación de datos de una API para tu proyecto académico?' if len(history)==3 else 'Explicaste el objetivo del proyecto con claridad. Puedes mejorar indicando cómo validaste los resultados.\n\n¿Qué harías si una solicitud contiene datos incompletos?'
 else:
  text='PRUEBA LOCAL: respuesta simulada, no generada por Gemini.\n\nTu borrador destaca un proyecto concreto. Puedes ordenar la presentación en formación, proyecto y objetivo profesional.\n\nVersión sugerida: Soy egresado de Informática y desarrollé un sistema de inventario con Python. Busco una primera oportunidad para aplicar lo aprendido y seguir creciendo.'
 response=MagicMock()
 response.__enter__.return_value.read.return_value=json.dumps({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':text}]}}]}).encode()
 return response
from scripts.preview_sprints import main
with patch('urllib.request.urlopen',side_effect=fake_transport):
 main()
