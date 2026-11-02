"""Summarize explicit assisted annotations; never infer correctness from answered status."""
import argparse
import json
import statistics
from collections import Counter
from pathlib import Path


def summarize(block):
    rows = block['rows']
    reviewed = [r for r in rows if r.get('assisted_correctness') in (0, 1)]
    answered = [r for r in rows if r['result']['status'] == 'answered']
    reviewed_answers = [r for r in answered if r.get('assisted_correctness') in (0, 1)]
    positive = [r for r in reviewed if r['answerable']]
    negative = [r for r in reviewed if not r['answerable']]
    refusals = Counter()
    for row in rows:
        result = row['result']
        if result['status'] != 'insufficient_evidence':
            continue
        if result.get('abstention_reason') == 'outside_notice_scope':
            reason = 'scope_rule'
        elif result.get('generation', {}).get('reason') == 'no_safe_candidates':
            reason = 'candidate_filter'
        elif result.get('generation', {}).get('request_sent'):
            reason = 'model_abstention'
        else:
            reason = 'retrieval_threshold'
        refusals[reason] += 1
    supported = [r for r in reviewed_answers if r.get('assisted_source_support') in (0, 1)]
    return {
        'reviewed_cases': len(reviewed),
        'correct_cases': sum(r['assisted_correctness'] for r in reviewed),
        'answerable_cases_reviewed': len(positive),
        'correct_answerable_cases': sum(r['assisted_correctness'] for r in positive),
        'answered_cases_reviewed': len(reviewed_answers),
        'correct_answers_presented': sum(r['assisted_correctness'] for r in reviewed_answers),
        'source_support_cases_reviewed': len(supported),
        'source_support_and_relevance': sum(r['assisted_source_support'] for r in supported),
        'literal_quotes_verified': sum(r.get('literal_quote_verified') is True for r in answered),
        'unanswerable_cases_reviewed': len(negative),
        'correct_unanswerable_cases': sum(r['assisted_correctness'] for r in negative),
        'refusal_mechanisms_all_cases': dict(refusals),
        'generation_unavailable': sum(r['result']['status'] == 'generation_unavailable' for r in rows),
        'latency_median_ms': statistics.median(r['result']['latency_ms'] for r in rows),
        'latency_answered_median_ms': statistics.median(r['result']['latency_ms'] for r in answered) if answered else None,
        'independent_human_review': False,
        'review_kind': 'assistant comparison with frozen key and PDF text; not independent validation'
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding='utf-8'))
    print(json.dumps({method: summarize(block) for method, block in report['methods'].items()},
                     ensure_ascii=False, indent=2))
