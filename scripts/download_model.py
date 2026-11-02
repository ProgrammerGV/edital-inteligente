"""Explicit network step; application inference itself is local-only."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('HF_HOME', str(ROOT / 'data/cache/huggingface'))
from sentence_transformers import SentenceTransformer

if __name__ == '__main__':
    destination = ROOT / 'data/models/minilm'
    model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', device='cpu')
    model.save_pretrained(str(destination))
    print(f'Modelo disponível em {destination}')
