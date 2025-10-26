import base64
import json
import time
from rich import print
from backend.workers.extractor.openai_client import openai_client
import json, re
from typing import Any


BATCH_PROMPT = """
You are a financial document parser.

You will receive multiple chart or KPI images from the same report.
Images are grayscale and low-resolution; focus on extracting quantitative chart or table data, ignore cosmetic artifacts.
For *each image*, return one JSON object in a list, following this schema:

[
  {
    "page_index": int,
    "page_type": "chart" | "table" | "text" | "mixed" | "cover",
    "title": "string | null",
    "chart_type": "bar" | "line" | "pie" | "table" | "none",
    "entities": [{"label": "Revenue", "values": [100, 120, 140]}],
    "key_metrics": [{"name": "ROE", "value": "17.5%", "period": "Q2FY26"}],
    "insights": ["Revenue grew YoY", "Margins improved"]
  }
]

Output *only* valid JSON — no prose, no explanation, no markdown, no code fences.
If you cannot detect structure in an image, include an entry:
{"page_index": <number>, "page_type": "unknown", "error": "No structured data found"}.
"""


def extract_charts_batch(
    image_paths: list[str], model: str = "gpt-4o-mini", retries: int = 3
):
    if not image_paths:
        return []

    try:
        print(
            f"[cyan]Analyzing {len(image_paths)} pages with OpenAI Vision batch...[/cyan]"
        )

        image_inputs = []
        for idx, path in enumerate(image_paths, 1):
            with open(path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode("utf-8")
            image_inputs.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                }
            )

        raw_output = None

        for attempt in range(1, retries + 1):
            try:
                response = openai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": BATCH_PROMPT},
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Analyze these {len(image_paths)} pages.",
                                },
                                *image_inputs,
                            ],
                        },
                    ],
                    temperature=0,
                    max_tokens=2000,
                )

                raw_output = (
                    response.choices[0].message.content.strip()
                    if response.choices[0].message.content is not None
                    else ""
                )
                data = extract_json_safely(raw_output)

                if isinstance(data, list):
                    print(f"Parsed structured JSON for {len(data)} pages.")
                    return data
                else:
                    raise ValueError("Invalid data structure")

            except json.JSONDecodeError as e:
                print(f"Non-JSON response: {str(e)}")
                snippet = (
                    raw_output[:300]
                    if "content" in locals() and raw_output is not None
                    else ""
                )
                print(f"Partial output: {snippet!r}")
                return []

            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    wait = 5 * attempt
                    print(f"[yellow]Rate limited — retrying in {wait}s...[/yellow]")
                    time.sleep(wait)
                    continue
                print(
                    f"[red]Vision batch error (attempt {attempt}/{retries}): {e}[/red]"
                )
                time.sleep(2)

        print("[red]Batch Vision failed after retries.[/red]")
        return [{"page_type": "unknown", "error": "Failed batch parsing"}]

    except Exception as e:
        print(f"Vision API error: {e}")
        return []


def extract_json_safely(raw: str) -> Any:
    if not raw:
        raise ValueError("Empty model response")

    cleaned = (
        raw.replace("```json", "")
        .replace("```", "")
        .replace("“", '"')
        .replace("”", '"')
        .strip()
    )

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", cleaned)
    if match:
        snippet = match.group(0)
        try:
            return json.loads(snippet)
        except Exception:
            pass

    try:
        lines = [ln for ln in cleaned.splitlines() if ln.strip().startswith("{")]
        if lines:
            return json.loads("[" + ",".join(lines) + "]")
    except Exception:
        pass

    raise ValueError("Could not parse valid JSON from model response.")
