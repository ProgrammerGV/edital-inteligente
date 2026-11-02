import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from edital.answer import generation_status
from edital.corpus import load_corpus

if __name__=='__main__':
    corpus=load_corpus(ROOT)
    status=generation_status()
    print(json.dumps({'documents':len(corpus['documents']),
                      'semantic_model_installed':(ROOT/'data/models/minilm/config.json').exists(),
                      'generation':status},ensure_ascii=False,indent=2))
    if not status['available']:
        print('A busca continua disponível. Para gerar citações, inicie Ollama e baixe o modelo configurado.')
