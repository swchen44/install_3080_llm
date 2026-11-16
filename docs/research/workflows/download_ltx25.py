#!/usr/bin/env python3
"""Download the approved LTX-2.5 files and check official sizes and hashes."""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from huggingface_hub import hf_hub_download

research = Path(__file__).resolve().parents[1]
manifest = json.loads((research / 'logs/21-ltx25-download-manifest.json').read_text())
root = Path.home() / 'Downloads/ai/models/comfyui/ComfyUI/models'
for item in manifest['files']:
    name = item['rfilename']
    print(datetime.now().astimezone().isoformat(), 'START', name, item['size'], flush=True)
    path = Path(hf_hub_download('Lightricks/LTX-2.5', name, revision=manifest['revision'], local_dir=root, token=True))
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    if path.stat().st_size != item['size'] or digest.hexdigest() != item['lfs']['sha256']:
        raise RuntimeError(f'File verification failed: {path}')
    print(datetime.now().astimezone().isoformat(), 'VERIFIED', name, digest.hexdigest(), flush=True)
print('ALL VERIFIED', flush=True)
