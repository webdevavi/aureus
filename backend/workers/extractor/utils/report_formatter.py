import json
import os
import re
import time
from typing import Any, Dict
from rich import print
from backend.workers.extractor.utils.compressor import llm_friendly_compress
from backend.workers.extractor.utils.prompt_builder import build_financial_prompt
from backend.workers.extractor.openai_client import openai_client
from backend.workers.extractor.utils.validate_report_schema import (
    validate_report_schema,
)


def generate_report(
    parsed_json_path: str, company_name: str, model: str = "gpt-4o-mini"
) -> str:
    if not os.path.exists(parsed_json_path):
        raise FileNotFoundError(parsed_json_path)

    with open(parsed_json_path, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)

    print("[cyan]Building context for OpenAI...[/cyan]")
    context = llm_friendly_compress(parsed_data)
    prompt = build_financial_prompt(context, company_name)

    for attempt in range(5):
        try:
            print(
                f"[yellow]Requesting structured report (attempt {attempt+1})...[/yellow]"
            )

            resp = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst producing structured equity reports.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                seed=42,
                top_p=1,
                max_tokens=4000,
            )

            raw_output = resp.choices[0].message.content
            if not raw_output:
                raise ValueError("Empty response from OpenAI.")

            report = try_fix_json(raw_output)
            if not isinstance(report, dict):
                raise ValueError("Parsed report is not a valid dict.")

            if not validate_report_schema(report):
                print(
                    "[yellow]Report JSON failed schema validation. Retrying...[/yellow]"
                )
                continue
            else:
                break

        except Exception as e:
            wait = min(2**attempt, 30)
            print(f"[red]API error: {e} (retrying in {wait}s)[/red]")
            time.sleep(wait)
    else:
        report = {"error": "All retries failed."}

    os.makedirs("tmp/output", exist_ok=True)
    out_path = "tmp/output/final_report.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"[green]Structured report saved to {out_path}[/green]")
    return out_path


def try_fix_json(raw: str) -> Dict[str, Any]:
    try:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1:
            snippet = raw[start : end + 1]
            return json.loads(snippet)
    except Exception:
        pass

    cleaned = re.sub(r"```(?:json)?", "", raw)
    cleaned = cleaned.replace("“", '"').replace("”", '"').strip()
    try:
        return json.loads(cleaned)
    except Exception:
        return {"raw_output": raw}
