import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from edital.corpus import build_corpus

if __name__ == '__main__':
    corpus = build_corpus(ROOT)
    print(f'{len(corpus["documents"])} documentos, {len(corpus["pages"])} páginas com texto, {len(corpus["chunks"])} trechos.')
    for warning in corpus['warnings']:
        print(warning)
