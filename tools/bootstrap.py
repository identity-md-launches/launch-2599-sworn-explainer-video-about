"""Offline-Bootstrap; entpackt ausschließlich mitgelieferte Abhängigkeiten."""
from pathlib import Path
import hashlib
import json
import sys
import tarfile

ROOT = Path(__file__).resolve().parent.parent
SCRATCH = ROOT / 'test' / 'scratch'

def setup():
    manifest = json.loads((ROOT / 'tools' / 'vendor' / 'manifest.json').read_text())
    for entry in manifest:
        path = ROOT / entry['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256'], path
    SCRATCH.mkdir(parents=True, exist_ok=True)
    site = SCRATCH / 'python'
    if not (site / 'PIL' / '__init__.py').exists():
        with tarfile.open(ROOT / 'tools' / 'vendor' / 'pillow-runtime.tar.xz') as archive:
            archive.extractall(site, filter='data')
    sys.path.insert(0, str(site))
    binaries = SCRATCH / 'ffmpeg-runtime'
    if not (binaries / 'ffprobe').exists():
        with tarfile.open(ROOT / 'tools' / 'vendor' / 'ffmpeg-runtime.tar.xz') as archive:
            archive.extractall(binaries, filter='data')
    return binaries / 'ffmpeg', binaries / 'ffprobe'
