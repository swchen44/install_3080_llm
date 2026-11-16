#!/usr/bin/env python3
"""Reproducible long-context needle-recall probe against a local OpenAI API."""
import argparse, datetime, hashlib, json, random, subprocess, time, urllib.request, urllib.error
from pathlib import Path

FACTS = {
    "rollback_ticket": "RB-7319",
    "archive_region": "north-04",
    "queue_limit": "163",
    "canary_owner": "team-amber",
    "schema_revision": "schema-28c",
    "incident_checksum": "a91f-0c72",
}

def now(): return datetime.datetime.now().astimezone().isoformat()

def build_prompt(rows, nonce):
    rng = random.Random(30802026)
    names = list(FACTS)
    chunks = [f"Run {nonce}. This is an archived operations record; use only the records below.\n"]
    per = max(1, rows // len(names))
    for section, name in enumerate(names):
        for i in range(per):
            tag = rng.randrange(100000, 999999)
            words = " ".join(f"{rng.choice(('module','request','cache','kernel','trace','buffer','result','thread','value','index','record','validate'))}{rng.randrange(10000)}" for _ in range(12))
            chunks.append(f"Log {section*per+i:07d} ref={tag} status=closed note={words}.\n")
        chunks.append(f"AUDIT RECORD target={name}; authoritative_value={FACTS[name]}; source=sealed-ledger-{section}.\n")
    return "".join(chunks) + (
        "\nReturn exactly one JSON object with these six keys and their authoritative values: "
        + ", ".join(names) + ". Do not guess or add commentary."
    )

def request(url, model, prompt, max_tokens, timeout):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0,
            "max_tokens": max_tokens, "stream": False, "reasoning_effort": "none"}
    req = urllib.request.Request(url.rstrip("/") + "/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response: result = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8', 'replace')
        raise RuntimeError(f"HTTP {error.code}: {detail[:2000]}") from error
    return result, (time.monotonic() - start) * 1000

def hardware():
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=power.limit,power.draw,temperature.gpu,memory.used,clocks.sm,clocks.mem", "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
    mem = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, _, value = line.partition(':')
        if key in ('MemAvailable', 'SwapFree', 'SwapTotal'): mem[key] = value.strip()
    return {"gpu_csv": gpu, "meminfo": mem, "time": now()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--context', type=int, choices=(131072, 262144), required=True)
    parser.add_argument('--url', default='http://127.0.0.1:8080')
    parser.add_argument('--out', required=True)
    parser.add_argument('--timeout', type=int, default=3600)
    args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    models = json.load(urllib.request.urlopen(args.url.rstrip('/') + '/v1/models', timeout=15))['data']
    if len(models) != 1: raise SystemExit(f"expected exactly one loaded model, got {len(models)}")
    model = models[0]['id']
    model_ctx = (models[0].get('meta') or {}).get('n_ctx')
    if model_ctx != args.context: raise SystemExit(f"server context mismatch: requested {args.context}, /v1/models reports {model_ctx}")
    target = int(args.context * .95)
    # This record format averages substantially more than 30 tokenizer tokens.
    # Start conservatively so the first calibration request always fits.
    rows = max(1, target // 160)
    calibration = []
    # Calibrate with a separate nonce so the scored request cannot reuse its KV cache.
    for trial in range(5):
        prompt = build_prompt(rows, f"calibration-{trial}-{time.time_ns()}")
        response, elapsed = request(args.url, model, prompt, 1, args.timeout)
        usage = response.get('usage') or {}; actual = usage.get('prompt_tokens')
        calibration.append({"rows": rows, "prompt_tokens": actual, "elapsed_ms": elapsed, "usage": usage})
        if not isinstance(actual, int): raise SystemExit("calibration returned no prompt token count")
        if abs(actual-target) < max(40, target*.025): break
        rows = max(1, round(rows * target / actual))
    nonce = f"scored-{time.time_ns()}"
    prompt = build_prompt(rows, nonce)
    (out/'prompt.txt').write_text(prompt)
    started = now(); before = hardware()
    response, elapsed = request(args.url, model, prompt, 256, args.timeout)
    after = hardware()
    choice = (response.get('choices') or [{}])[0]
    content = ((choice.get('message') or {}).get('content') or '').strip()
    parse_error = None
    try:
        answer = json.loads(content)
        correct = {key: answer.get(key) == value for key, value in FACTS.items()}
    except (ValueError, AttributeError) as error:
        answer = None; correct = {key: False for key in FACTS}; parse_error = str(error)
    usage = response.get('usage') or {}
    report = {"started_at": started, "model": model, "configured_context_tokens": args.context,
              "target_prompt_tokens": target, "actual_prompt_tokens": usage.get('prompt_tokens'),
              "completion_tokens": usage.get('completion_tokens'), "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
              "answer": answer, "raw_content": content, "correct_by_key": correct,
              "score": sum(correct.values()), "score_max": len(FACTS), "parse_error": parse_error,
              "elapsed_ms": elapsed, "calibration": calibration, "hardware_before": before,
              "hardware_after": after, "response_id": response.get('id'),
              "timings": response.get('timings'), "finish_reason": choice.get('finish_reason')}
    (out/'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: report[k] for k in ('model','configured_context_tokens','actual_prompt_tokens','score','score_max','elapsed_ms','correct_by_key','parse_error')}, ensure_ascii=False))

if __name__ == '__main__': main()
