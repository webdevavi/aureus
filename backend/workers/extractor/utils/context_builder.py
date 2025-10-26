import json
import pandas as pd
from typing import List, Dict, Any


def build_context(parsed_data: List[Dict[str, Any]]) -> str:
    table_blocks = []
    text_blocks = []
    chart_blocks = []

    for page in parsed_data:
        page_num = page.get("page", "?")

        text = (page.get("text") or "").strip()
        if text:
            text_blocks.append(f"Page {page_num} Text:\n{text}")

        table_field = page.get("tables") or page.get("table_infos") or []
        for table_info in table_field:
            try:
                df = pd.read_csv(table_info["path"])
                if not df.empty and df.shape[1] > 1:
                    df = df.fillna("")
                    table_blocks.append(
                        f"Page {page_num} Table ({len(df)}×{len(df.columns)}):\n"
                        f"{df.to_markdown(index=False)}"
                    )
            except Exception as e:
                print(f"Table parse error on page {page_num}: {e}")
                continue

        ocr_text = (page.get("ocr_text") or page.get("ocr") or "").strip()
        if ocr_text and ocr_text != text:
            text_blocks.append(f"Page {page_num} OCR Extract:\n{ocr_text}")

        chart_data = page.get("chart_json")
        if chart_data:
            try:
                if isinstance(chart_data, str):
                    chart_data = json.loads(chart_data)

                title = chart_data.get("title") or chart_data.get("page_type", "Chart")
                chart_type = chart_data.get("chart_type", "unknown")
                entities = chart_data.get("entities", [])
                metrics = chart_data.get("key_metrics", [])

                chart_summary = f"Page {page_num} Chart ({chart_type}): {title}\n"

                if entities and isinstance(entities, list):
                    df = pd.DataFrame(entities)
                    if not df.empty:
                        chart_summary += df.to_markdown(index=False)
                elif metrics:
                    chart_summary += json.dumps(metrics, indent=2)

                chart_blocks.append(chart_summary)
            except Exception as e:
                print(f"Chart parse error on page {page_num}: {e}")
                continue

    context_sections = [
        "=== TEXT CONTENT ===",
        "\n\n".join(text_blocks),
        "=== TABLE DATA ===",
        "\n\n".join(table_blocks),
        "=== CHART DATA ===",
        "\n\n".join(chart_blocks),
    ]

    context = "\n\n".join([s for s in context_sections if s.strip()])
    return context
