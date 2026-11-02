"""Evidence selection and a documented scope rule for opening notices."""
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .text import normalize

STOP_WORDS = ['a', 'o', 'e', 'as', 'os', 'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na',
              'nos', 'nas', 'um', 'uma', 'para', 'por', 'qual', 'quais', 'como', 'que',
              'se', 'ser', 'sao', 'sera', 'serao', 'edital', 'estagio']
INJECTION = re.compile(r'(ignore|desconsidere).{0,80}(instruc|instruction|sistema|system|prompt)|'
                       r'\b(system|assistant)\s*:|'
                       r'(revele|reveal|imprima|print).{0,60}(senha|password|secret|segredo|api.?key)')


def outside_notice_scope(question: str, documents: list[dict], document_id: str | None) -> bool:
    selected = [d for d in documents if document_id is None or d['id'] == document_id]
    if not selected or not all(d.get('document_type') == 'opening_notice' for d in selected):
        return False
    text = normalize(question)
    # Opening notices define rules and planned dates; individual outcomes need result documents.
    # This is an explicit corpus scope rule, not learned or general-purpose fact verification.
    patterns = [r'\bquem\b.{0,50}\b(foi|foram)\b.{0,30}(contratad|aprovad|convocad|selecionad)',
                r'\b(nome|nomes)\b.{0,50}(aprovad|contratad|primeiro colocado|selecionad)',
                r'\bnota\b.{0,60}(primeiro colocado|obtida|individual)',
                r'\bnota final\b.{0,60}(candidato|candidata|aprovad)',
                r'\b(quantos|quantas|numero|quantidade)\b.{0,80}(compareceram|assinaram|foram aprovados|foram contratados|inscritos foram)',
                r'(resultado individual|classificacao individual|minha nota|meu resultado)']
    return any(re.search(pattern, text) for pattern in patterns)


def expand_sources(index, hits: list[dict]) -> list[dict]:
    pages = {(p['document_id'], p['page']): p['text'] for p in index.corpus.get('pages', [])}
    return [dict(hit, id=f'{hit["document_id"]}:p{hit["page"]}',
                 retrieval_chunk_id=hit['id'],
                 evidence_text=pages.get((hit['document_id'], hit['page']), hit['text'])) for hit in hits]


def covers_named_subject(question: str, quote: str) -> bool:
    """Conservative named-benefit constraint: salary is not evidence for another allowance.

    Extracts the subject dynamically instead of memorizing missing answers from a test set.
    Synonyms are not inferred by this rule; an unmatched synonym may cause an abstention.
    """
    question, quote = normalize(question), normalize(quote)
    patterns = [r'\b(?:auxilio|vale)(?:[ -]+de)?[ -]+([a-z]{4,})',
                r'\breembolso(?:\s+mensal)?(?:\s+d[aeo])?\s+([a-z]{4,})']
    for pattern in patterns:
        match = re.search(pattern, question)
        if match:
            subject=match.group(1)
            if subject not in {'mensal','diario','financeiro','para','pago','paga','oferecido'} and subject[:5] not in quote:
                return False
    return True


def _windows(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?;])\s+(?=[A-ZÀ-Ú])', text)
    pieces = []
    for i, sentence in enumerate(sentences):
        if len(sentence) <= 450:
            pieces.append(sentence.strip())
            if i + 1 < len(sentences):
                pair = sentence + ' ' + sentences[i + 1]
                if len(pair) <= 450:
                    pieces.append(pair.strip())
        else:
            words = list(re.finditer(r'\S+', sentence))
            start = 0
            while start < len(words):
                end = start
                while end < len(words) and words[end].end() - words[start].start() <= 450:
                    end += 1
                if end == start:
                    start += 1
                    continue
                pieces.append(sentence[words[start].start():words[end - 1].end()])
                if end >= len(words):
                    break
                start = max(start + 1, end - 10)
    return pieces


def candidates(question: str, hits: list[dict], limit: int = 4, encoder=None) -> list[dict]:
    items, seen = [], set()
    for source in hits:
        for quote in _windows(source.get('evidence_text', source['text'])):
            if (len(quote) < 18 or quote in seen or INJECTION.search(normalize(quote))
                    or (len(quote) < 85 and quote.upper() == quote)
                    or not covers_named_subject(question,quote)):
                continue
            seen.add(quote)
            items.append({'source_id': source['id'], 'quote': quote})
    if not items:
        return []
    vectorizer = TfidfVectorizer(strip_accents='unicode', stop_words=STOP_WORDS, ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform([item['quote'] for item in items])
        scores = (matrix @ vectorizer.transform([question]).T).toarray().ravel()
    except ValueError:
        return []
    semantic_scores = np.zeros(len(items))
    if encoder is not None:
        vectors=encoder.encode([item['quote'] for item in items],normalize_embeddings=True,show_progress_bar=False)
        query=encoder.encode([question],normalize_embeddings=True,show_progress_bar=False)[0]
        semantic_scores=vectors @ query
        ranking=0.7*semantic_scores+0.3*scores
    else:
        ranking=scores
    order = sorted(range(len(items)), key=lambda i: (-float(ranking[i]), len(items[i]['quote']), i))
    chosen=[]
    for i in order:
        if any(items[i]['source_id']==items[j]['source_id'] and
               (items[i]['quote'] in items[j]['quote'] or items[j]['quote'] in items[i]['quote']) for j in chosen):
            continue
        chosen.append(i)
        if len(chosen)>=limit:
            break
    return [dict(items[i], evidence_id=f'E{n}', lexical_score=round(float(scores[i]), 6),
                 semantic_score=round(float(semantic_scores[i]),6) if encoder is not None else None)
            for n, i in enumerate(chosen)]
