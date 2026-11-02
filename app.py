import os
import threading
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from edital.answer import answer
from edital.corpus import CorpusError, load_corpus
from edital.search import SearchIndex, SemanticUnavailable

ROOT = Path(__file__).resolve().parent


def create_app(index=None, root=ROOT):
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024
    state = {'index': index}
    lock = threading.Lock()

    def get_index():
        if state['index'] is None:
            with lock:
                if state['index'] is None:
                    state['index'] = SearchIndex(load_corpus(root), root / 'data/models/minilm')
        return state['index']

    @app.after_request
    def headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @app.get('/')
    def home():
        return render_template('index.html')

    @app.get('/api/documents')
    def documents():
        idx = get_index()
        return jsonify(documents=idx.corpus['documents'], warnings=idx.corpus.get('warnings', []),
                       semantic_installed=bool(idx.model_path and (idx.model_path / 'config.json').exists()))

    @app.get('/api/health')
    def health():
        return jsonify(status='ok', documents=len(get_index().corpus['documents']))

    @app.get('/documents/<document_id>.pdf')
    def pdf(document_id):
        if document_id not in {d['id'] for d in get_index().corpus['documents']}:
            return jsonify(error='Documento desconhecido.'), 404
        return send_from_directory(root / 'data/pdfs', f'{document_id}.pdf')

    @app.post('/api/ask')
    def ask():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return jsonify(error='Envie um objeto JSON.'), 400
        question = body.get('question')
        method, doc, generate = body.get('method', 'tfidf'), body.get('document_id'), body.get('generate', False)
        if not isinstance(question, str) or not 5 <= len(question.strip()) <= 600:
            return jsonify(error='Digite uma pergunta com 5 a 600 caracteres.'), 400
        if method not in ('tfidf', 'semantic') or not isinstance(generate, bool):
            return jsonify(error='Método ou opção de geração inválida.'), 400
        if doc is not None and (not isinstance(doc, str) or doc not in {d['id'] for d in get_index().corpus['documents']}):
            return jsonify(error='Documento desconhecido.'), 400
        return jsonify(answer(get_index(), question.strip(), method, doc, generate))

    @app.errorhandler(CorpusError)
    @app.errorhandler(SemanticUnavailable)
    def unavailable(exc):
        return jsonify(error=str(exc)), 503

    @app.errorhandler(413)
    def too_large(exc):
        return jsonify(error='Requisição muito grande.'), 413

    return app


app = create_app()

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='127.0.0.1', port=int(os.environ.get('PORT', '5000')), threads=2)
