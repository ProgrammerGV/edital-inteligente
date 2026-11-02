import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader


class CorpusError(ValueError):
    pass


def extract_document(path: Path, metadata: dict) -> tuple[list[dict], list[str]]:
    """Use physical PDF page numbers (1-based), never inferred printed numbers."""
    pages, warnings = [], []
    try:
        reader = PdfReader(path)
        if reader.is_encrypted and not reader.decrypt(''):
            raise CorpusError('PDF protegido por senha.')
        for number, page in enumerate(reader.pages, 1):
            text = re.sub(r'\s+', ' ', page.extract_text() or '').strip()
            if not text:
                warnings.append(f'{metadata["id"]}: página {number} sem texto; OCR não incluído.')
                continue
            pages.append({'document_id': metadata['id'], 'title': metadata['title'],
                          'source_url': metadata['url'], 'page': number, 'text': text})
    except CorpusError:
        raise
    except Exception as exc:
        raise CorpusError(f'Não foi possível ler {path.name}.') from exc
    if not pages:
        raise CorpusError(f'{path.name}: PDF sem texto selecionável; OCR não incluído.')
    return pages, warnings


def chunk_pages(pages: list[dict], size: int = 95, overlap: int = 20) -> list[dict]:
    if size <= overlap or overlap < 0:
        raise ValueError('O tamanho deve ser maior que a sobreposição.')
    chunks = []
    for page in pages:
        words = page['text'].split()
        for offset in range(0, len(words), size - overlap):
            chunk = dict(page, text=' '.join(words[offset:offset + size]))
            chunk['id'] = f'{page["document_id"]}:p{page["page"]}:w{offset}'
            chunks.append(chunk)
            if offset + size >= len(words):
                break
    return chunks


def build_corpus(root: Path) -> dict:
    manifest = json.loads((root / 'data/manifest.json').read_text(encoding='utf-8'))
    pages, warnings, documents = [], [], []
    for item in manifest:
        path = root / 'data/pdfs' / f'{item["id"]}.pdf'
        if not path.exists():
            raise CorpusError(f'Arquivo ausente: {path.name}. Execute scripts/download_corpus.py.')
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if item.get('sha256') and item['sha256'] != digest:
            raise CorpusError(f'{path.name}: SHA-256 diferente do manifesto; confira a versão da fonte.')
        extracted, notes = extract_document(path, item)
        pages.extend(extracted)
        warnings.extend(notes)
        documents.append(dict(item, sha256=digest, pages=len(PdfReader(path).pages)))
    corpus = {'documents': documents, 'pages': pages, 'chunks': chunk_pages(pages), 'warnings': warnings}
    (root / 'data/corpus.json').write_text(json.dumps(corpus, ensure_ascii=False, indent=2), encoding='utf-8')
    return corpus


def load_corpus(root: Path) -> dict:
    path = root / 'data/corpus.json'
    if not path.exists():
        raise CorpusError('Corpus não preparado. Execute python scripts/build_corpus.py.')
    return json.loads(path.read_text(encoding='utf-8'))
