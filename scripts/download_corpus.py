import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    manifest_path = ROOT / 'data/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    folder = ROOT / 'data/pdfs'
    folder.mkdir(parents=True, exist_ok=True)
    for item in manifest:
        if urlparse(item['url']).scheme != 'https':
            raise ValueError('Use fontes HTTPS.')
        path = folder / f'{item["id"]}.pdf'
        data = path.read_bytes() if path.exists() else None
        if data is None:
            with urlopen(Request(item['url'], headers={'User-Agent': 'EditalInteligente/0.1 (academic portfolio)'}), timeout=60) as response:
                data = response.read(25 * 1024 * 1024)
        if not data.startswith(b'%PDF'):
            raise ValueError(f'{item["id"]}: a fonte não retornou um PDF.')
        digest = hashlib.sha256(data).hexdigest()
        if item.get('sha256') and item['sha256'] != digest:
            raise ValueError(f'{item["id"]}: a fonte mudou. Não substituí o snapshot de avaliação.')
        path.write_bytes(data)
        item['sha256'] = digest
        print(f'{item["id"]}: {len(data)} bytes, SHA-256 {digest}')
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
