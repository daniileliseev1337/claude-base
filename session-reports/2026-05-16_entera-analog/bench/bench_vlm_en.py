"""Замер vision-LLM на УПД с EN-промптом (для англоязычных моделей вроде moondream).
"""
import base64
import json
import os
import sys
import time
from pathlib import Path

os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"

import requests

PROMPT_EN = """This is a Russian invoice document (УПД / Universal Transfer Document).
Read all visible text from the image and extract data as JSON (no markdown, JSON only):

{
  "document_type": "...",
  "invoice_number": "...",
  "invoice_date": "...",
  "seller_name": "...",
  "seller_inn": "...",
  "seller_kpp": "...",
  "seller_address": "...",
  "buyer_name": "...",
  "buyer_inn": "...",
  "buyer_kpp": "...",
  "buyer_address": "...",
  "item_name": "...",
  "item_quantity": "...",
  "item_unit": "...",
  "item_price": "...",
  "total_amount": "...",
  "vat_info": "...",
  "director_name": "...",
  "accountant_name": "..."
}

Preserve original Cyrillic text exactly. Numbers: digits only without spaces or currency symbols.
Use null if field is not visible."""


def main():
    if len(sys.argv) != 4:
        print("Usage: python bench_vlm_en.py <model> <png_path> <out_json>")
        sys.exit(2)
    model, img_path, out_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    img_b64 = base64.b64encode(img_path.read_bytes()).decode()
    print(f"Model: {model} | Image: {img_path.name} ({img_path.stat().st_size/1024:.0f} KB)", flush=True)

    payload = {
        "model": model,
        "prompt": PROMPT_EN,
        "images": [img_b64],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 1024, "num_ctx": 2048},
    }
    print("Calling Ollama...", flush=True)
    t0 = time.time()
    try:
        r = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=900, proxies={"http": None, "https": None})
        elapsed = time.time() - t0
        if r.status_code != 200:
            print(f"HTTP {r.status_code} after {elapsed:.1f}s | body: {r.text[:300]}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR after {time.time()-t0:.1f}s: {e}")
        sys.exit(1)
    data = r.json()
    raw = data.get("response", "")
    print(f"OK {elapsed:.1f}s | tokens: {data.get('eval_count')}", flush=True)

    parsed, perr = None, None
    try:
        t = raw.strip()
        if "```" in t:
            for chunk in t.split("```"):
                c = chunk.strip()
                if c.startswith("json"): c = c[4:].strip()
                if c.startswith("{"):
                    t = c; break
        parsed = json.loads(t)
    except Exception as e:
        perr = str(e)

    out = {
        "model": model, "image": str(img_path),
        "elapsed_sec": round(elapsed, 2),
        "ollama_duration_sec": round(data.get("total_duration", 0)/1e9, 2),
        "eval_count_tokens": data.get("eval_count"),
        "raw_response": raw, "parsed_json": parsed, "parse_error": perr,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {out_path}", flush=True)
    print("\n--- RAW (first 2000) ---")
    print(raw[:2000])


if __name__ == "__main__":
    main()
