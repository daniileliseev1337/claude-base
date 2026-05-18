"""Замер MiniCPM-V на УПД через Ollama HTTP API.
Извлекает структурированный JSON, замеряет время.
"""
import base64
import json
import sys
import time
from pathlib import Path

import requests

BENCH_DIR = Path(__file__).parent
IMG_PATH = BENCH_DIR / "samples" / "upd_vrnlom_p1.png"
OUT_PATH = BENCH_DIR / "result_minicpm_vrnlom.json"

PROMPT = """На изображении — российский Универсальный Передаточный Документ (УПД).
Извлеки данные строго в JSON-формате (без markdown, без комментариев, только JSON):

{
  "type": "УПД",
  "status": <1 или 2>,
  "number": "<номер счёта-фактуры>",
  "date": "<дата в формате ДД.ММ.ГГГГ>",
  "seller": {"name": "...", "inn": "...", "kpp": "...", "address": "..."},
  "buyer":  {"name": "...", "inn": "...", "kpp": "...", "address": "..."},
  "items": [
    {"name": "...", "quantity": <число>, "unit": "...", "unit_price": <число>, "total_without_vat": <число>, "vat_rate": "...", "vat_amount": <число или null>, "total_with_vat": <число или null>}
  ],
  "total_to_pay": <число>,
  "director": "<ФИО руководителя>",
  "accountant": "<ФИО бухгалтера>"
}

Цифры — без пробелов и без знаков рубля. Если поля нет — null. Отвечай ТОЛЬКО JSON-объектом."""


def main():
    img_bytes = IMG_PATH.read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode()
    print(f"Image: {IMG_PATH.name}, {len(img_bytes)/1024:.1f} KB", flush=True)

    payload = {
        "model": "minicpm-v:latest",
        "prompt": PROMPT,
        "images": [img_b64],
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 2048,
        },
    }

    print("Calling Ollama...", flush=True)
    t0 = time.time()
    r = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=600)
    elapsed = time.time() - t0
    r.raise_for_status()
    data = r.json()
    raw_response = data.get("response", "")
    print(f"Done in {elapsed:.1f}s", flush=True)
    print(f"Eval count: {data.get('eval_count')}, prompt_eval_count: {data.get('prompt_eval_count')}", flush=True)
    print(f"Total duration: {data.get('total_duration', 0) / 1e9:.1f}s (ollama-side)", flush=True)

    # Попробую распарсить как JSON
    parsed = None
    parse_err = None
    try:
        # Иногда модель оборачивает в ```json ... ```
        text = raw_response.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text.strip())
    except Exception as e:
        parse_err = str(e)

    result = {
        "model": "minicpm-v:latest",
        "image": str(IMG_PATH),
        "elapsed_sec": round(elapsed, 2),
        "ollama_total_duration_sec": round(data.get("total_duration", 0) / 1e9, 2),
        "eval_count_tokens": data.get("eval_count"),
        "raw_response": raw_response,
        "parsed_json": parsed,
        "parse_error": parse_err,
    }
    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved: {OUT_PATH}", flush=True)
    print("\n--- RAW RESPONSE (first 1500 chars) ---", flush=True)
    print(raw_response[:1500], flush=True)


if __name__ == "__main__":
    main()
