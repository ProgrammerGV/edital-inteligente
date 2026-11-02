import threading
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .text import normalize

MODEL_ID = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'


class SemanticUnavailable(RuntimeError):
    pass


class SearchIndex:
    def __init__(self, corpus: dict, model_path: str | Path | None = None):
        self.corpus = corpus
        self.chunks = corpus['chunks']
        if not self.chunks:
            raise ValueError('Corpus vazio.')
        # Titles intentionally excluded: otherwise identical title keywords bias every page.
        self.vectorizer = TfidfVectorizer(strip_accents='unicode', lowercase=True,
                                         ngram_range=(1, 2), sublinear_tf=True)
        self.matrix = self.vectorizer.fit_transform([c['text'] for c in self.chunks])
        self.model_path = Path(model_path) if model_path else None
        self.model = self.embeddings = None
        self._lock = threading.Lock()

    def prepare_semantic(self):
        if self.model is not None:
            return
        with self._lock:
            if self.model is not None:
                return
            if not self.model_path or not (self.model_path / 'config.json').exists():
                raise SemanticUnavailable('Modelo semântico não instalado. Execute scripts/download_model.py.')
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer(str(self.model_path), device='cpu', local_files_only=True)
                embeddings = model.encode([c['text'] for c in self.chunks], normalize_embeddings=True,
                                          show_progress_bar=False)
                self.embeddings = embeddings
                self.model = model
            except Exception as exc:
                raise SemanticUnavailable('Não foi possível carregar o modelo semântico local.') from exc

    def search(self, question: str, method: str = 'tfidf', document_id: str | None = None,
               k: int = 3) -> list[dict]:
        if method == 'semantic':
            self.prepare_semantic()
            query = self.model.encode([question], normalize_embeddings=True, show_progress_bar=False)[0]
            scores = self.embeddings @ query
        elif method == 'tfidf':
            scores = (self.matrix @ self.vectorizer.transform([question]).T).toarray().ravel()
        else:
            raise ValueError('Método desconhecido.')
        eligible = [i for i, c in enumerate(self.chunks)
                    if document_id is None or c['document_id'] == document_id]
        ranked = sorted(eligible, key=lambda i: (-float(scores[i]), self.chunks[i]['id']))
        # Return different pages: top-3 page retrieval must not count overlapping chunks as three sources.
        hits, seen = [], set()
        for i in ranked:
            chunk = self.chunks[i]
            key = (chunk['document_id'], chunk['page'])
            if key in seen or float(scores[i]) <= 0:
                continue
            seen.add(key)
            hits.append(dict(chunk, score=round(float(scores[i]), 6)))
            if len(hits) >= k:
                break
        return hits
