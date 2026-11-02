"""Run a frozen split once; retrieval metrics are distinct from human answer review."""
import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from edital.answer import answer
from edital.corpus import load_corpus
from edital.search import SearchIndex, SemanticUnavailable


def evaluate(split: str, methods: list[str], generate: bool = False):
    path = ROOT / 'evaluation' / f'{split}.json'
    questions = json.loads(path.read_text(encoding='utf-8'))
    corpus = load_corpus(ROOT)
    index = SearchIndex(corpus, ROOT / 'data/models/minilm')
    report = {'created_at': datetime.now(timezone.utc).isoformat(), 'split': split,
              'question_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'corpus_sha256': hashlib.sha256((ROOT / 'data/corpus.json').read_bytes()).hexdigest(),
              'python': platform.python_version(), 'platform': platform.platform(),
              'scope': 'Consulta com documento selecionado; não mede seleção automática do edital.',
              'generation_requested': generate, 'methods': {}}
    for method in methods:
        start = time.perf_counter()
        try:
            if method == 'semantic':
                index.prepare_semantic()
            preparation_ms = round((time.perf_counter() - start) * 1000, 2)
            rows = []
            for item in questions:
                result = answer(index, item['question'], method, item['document_id'], generate)
                pages = [h['page'] for h in result['sources']]
                expected_pages = item['expected_pages']
                relevant = bool(set(pages) & set(expected_pages)) if item['answerable'] else None
                reciprocal = next((1 / (i + 1) for i, p in enumerate(pages) if p in expected_pages), 0) if item['answerable'] else None
                rows.append({'id': item['id'], 'question': item['question'], 'document_id': item['document_id'],
                             'answerable': item['answerable'], 'expected_pages': expected_pages,
                             'retrieved_pages': pages, 'hit_at_3': relevant, 'reciprocal_rank_at_3': reciprocal,
                             'expected_answer': item.get('expected_answer'), 'result': result,
                             'manual_correctness': None, 'manual_source_support': None, 'manual_notes': ''})
            answerable = [r for r in rows if r['answerable']]
            unanswerable = [r for r in rows if not r['answerable']]
            durations = sorted(r['result']['latency_ms'] for r in rows)
            report['methods'][method] = {'status': 'measured', 'preparation_ms': preparation_ms,
                'answerable_count': len(answerable), 'unanswerable_count': len(unanswerable),
                'hit_at_3': statistics.mean(r['hit_at_3'] for r in answerable) if answerable else None,
                'mrr_at_3': statistics.mean(r['reciprocal_rank_at_3'] for r in answerable) if answerable else None,
                'unanswerable_abstention_rate': statistics.mean(r['result']['status'] == 'insufficient_evidence' for r in unanswerable) if unanswerable else None,
                'latency_median_ms': statistics.median(durations),
                'latency_p95_ms': durations[max(0, __import__('math').ceil(.95 * len(durations)) - 1)],
                'manual_answer_review': 'pending' if generate else 'not_applicable_search_only', 'rows': rows}
        except SemanticUnavailable as exc:
            report['methods'][method] = {'status': 'unavailable', 'error': str(exc)}
    report_path = ROOT / 'reports' / f'{split}-results.json'
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    for method, value in report['methods'].items():
        print(method, json.dumps({k: v for k, v in value.items() if k != 'rows'}, ensure_ascii=False))
    print(report_path)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--split', choices=['dev', 'test'], default='dev')
    parser.add_argument('--methods', nargs='+', choices=['tfidf', 'semantic'], default=['tfidf', 'semantic'])
    parser.add_argument('--generate', action='store_true')
    args = parser.parse_args()
    evaluate(args.split, args.methods, args.generate)
