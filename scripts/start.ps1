param([switch]$Semantic)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not (Test-Path '.venv/Scripts/python.exe')) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Instale Python 3.12+ e confira python --version.' }
    }
    $pythonExe = Join-Path $projectRoot '.venv/Scripts/python.exe'
    $requirementsFile = if ($Semantic) { 'requirements-semantic.txt' } else { 'requirements.txt' }
    & $pythonExe -m pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependências.' }
    if (-not (Test-Path 'data/pdfs/ifba-dgcom-2025.pdf')) {
        New-Item -ItemType Directory -Force 'data/pdfs' | Out-Null
        $manifest = Get-Content 'data/manifest.json' -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($document in $manifest) {
            Invoke-WebRequest -Uri $document.url -OutFile (Join-Path 'data/pdfs' ($document.id + '.pdf')) -TimeoutSec 60
        }
    }
    & $pythonExe scripts/download_corpus.py
    if ($LASTEXITCODE -ne 0) { throw 'Corpus inválido; confira as fontes e os hashes.' }
    & $pythonExe scripts/build_corpus.py
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao extrair corpus.' }
    if ($Semantic -and -not (Test-Path 'data/models/minilm/config.json')) {
        & $pythonExe scripts/download_model.py
        if ($LASTEXITCODE -ne 0) { throw 'Falha no download do modelo semântico.' }
    }
    Write-Host 'Abra http://127.0.0.1:5000. Ctrl+C encerra o servidor.'
    & $pythonExe app.py
} finally { Pop-Location }
