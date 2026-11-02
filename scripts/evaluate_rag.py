"""Versioned local-LLM evaluation. Preserves v1 reports; flushes every case to disk."""
import argparse
import hashlib
import json
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from edital.answer import answer, generation_status
from edital.corpus import load_corpus
from edital.search import SearchIndex


def run(split, methods, output, resume=False):
    status=generation_status()
    if not status['available']:
        raise RuntimeError('Ollama e o modelo configurado precisam estar disponíveis antes da avaliação.')
    questions_path = ROOT / 'evaluation' / f'{split}.json'
    questions = json.loads(questions_path.read_text(encoding='utf-8'))
    output_path = ROOT / 'reports' / output
    question_hash = hashlib.sha256(questions_path.read_bytes()).hexdigest()
    implementation={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                    for name in ['edital/answer.py','edital/evidence.py','edital/search.py']}
    if output_path.exists():
        if not resume:
            raise RuntimeError('Relatório existente. Use outro nome ou --resume; não sobrescrever execuções.')
        report = json.loads(output_path.read_text(encoding='utf-8'))
        if report['question_sha256'] != question_hash:
            raise RuntimeError('O conjunto mudou depois do congelamento.')
        if report['implementation_sha256'] != implementation:
            raise RuntimeError('A implementação mudou. Crie outro relatório para não misturar versões.')
        if report['model_digest'] != status['digest']:
            raise RuntimeError('O modelo mudou. Crie outro relatório para não misturar versões.')
    else:
        report = {'created_at':datetime.now(timezone.utc).isoformat(), 'split':split,
                  'question_sha256':question_hash,
                  'corpus_sha256':hashlib.sha256((ROOT/'data/corpus.json').read_bytes()).hexdigest(),
                  'model':status['model'],'model_digest':status['digest'],'implementation_sha256':implementation,
                  'python':platform.python_version(),'platform':platform.platform(),
                  'evaluation_kind':'generated citations; review by assistant is not independent human review',
                  'scope':'Documento pré-selecionado; corpus de editais de abertura.','methods':{}}
    index = SearchIndex(load_corpus(ROOT), ROOT/'data/models/minilm')
    for method in methods:
        preparation = time.perf_counter()
        if method == 'semantic' or (ROOT/'data/models/minilm/config.json').exists():
            index.prepare_semantic()
        block = report['methods'].setdefault(method, {'preparation_ms':round((time.perf_counter()-preparation)*1000,2),'rows':[]})
        done = {row['id'] for row in block['rows']}
        for item in questions:
            if item['id'] in done:
                continue
            result = answer(index,item['question'],method,item['document_id'],generate=True)
            row = dict(item,result=result,assisted_correctness=None,assisted_source_support=None,
                       review_notes='',reviewer=None,independent_human_review=False)
            block['rows'].append(row)
            output_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
            print(json.dumps({'method':method,'id':item['id'],'status':result['status'],
                              'latency_ms':result['latency_ms'],'answer':result['answer']},ensure_ascii=False),flush=True)
        rows=block['rows'];positive=[r for r in rows if r['answerable']];negative=[r for r in rows if not r['answerable']]
        block['summary']={'cases':len(rows),'answered':sum(r['result']['status']=='answered' for r in rows),
                          'answerable_coverage':statistics.mean(r['result']['status']=='answered' for r in positive),
                          'unanswerable_abstention':statistics.mean(r['result']['status']=='insufficient_evidence' for r in negative),
                          'generation_unavailable':sum(r['result']['status']=='generation_unavailable' for r in rows),
                          'latency_median_ms':statistics.median(r['result']['latency_ms'] for r in rows),
                          'source_support_review':'pending','correctness_review':'pending'}
        output_path.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(method,json.dumps(block['summary'],ensure_ascii=False),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--split',choices=['dev-v2','test-v2'],default='dev-v2')
    parser.add_argument('--methods',nargs='+',choices=['tfidf','semantic'],default=['tfidf','semantic'])
    parser.add_argument('--output',required=True)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--model',choices=['llama3.2:1b','llama3.2:3b'],default='llama3.2:3b')
    args=parser.parse_args()
    if Path(args.output).name != args.output or not args.output.endswith('.json'):
        raise ValueError('Use um nome de arquivo JSON, sem diretório.')
    os.environ['EDITAL_OLLAMA_MODEL']=args.model
    run(args.split,args.methods,args.output,args.resume)
