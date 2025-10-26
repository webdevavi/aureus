import json
import re
import pandas as pd
from typing import List, Dict, Any
from collections import Counter


def normalize_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def serialize_table(path: str) -> Dict[str, Any] | None:
    try:
        df = pd.read_csv(path)
        if df.empty or df.shape[1] < 2:
            return None

        df = df.fillna("").astype(str)

        headers = [str(h).strip() for h in df.columns.tolist()]

        if len(df) > 20:
            rows = [[str(cell).strip() for cell in row] for row in df.values.tolist()]
            return {
                "format": "compact",
                "headers": headers,
                "rows": rows,
                "row_count": len(rows),
            }
        else:
            records = df.to_dict("records")
            return {
                "format": "records",
                "data": [
                    {str(k).strip(): str(v).strip() for k, v in rec.items()}
                    for rec in records
                ],
            }
    except Exception as e:
        print(f"Failed to serialize table {path}: {e}")
        return None


def deduplicate_intelligently(
    text: str, seen_texts: Dict[str, int], threshold: int = 50
) -> str:
    if not text or len(text) < threshold:
        return text

    text_key = text[:100]
    seen_texts[text_key] = seen_texts.get(text_key, 0) + 1

    if seen_texts[text_key] >= 3 and len(text) > 200:
        preview = " ".join(text.split()[:8]) + "..."
        return f"[REPEATED: {preview}]"

    return text


def llm_friendly_compress(parsed_data: List[Dict[str, Any]]) -> str:
    seen_texts = {}
    compressed_pages = []
    repeated_content = {}

    for page in parsed_data:
        page_num = page.get("page", "?")
        text = normalize_text(page.get("text", ""))
        ocr = normalize_text(page.get("ocr_text") or page.get("ocr") or "")

        text_dedupe = deduplicate_intelligently(text, seen_texts)
        ocr_dedupe = deduplicate_intelligently(ocr, seen_texts)

        if "[REPEATED:" in text_dedupe and text not in repeated_content.values():
            key = text_dedupe.split("[REPEATED: ")[1].split("]")[0]
            repeated_content[key] = text
        if "[REPEATED:" in ocr_dedupe and ocr not in repeated_content.values():
            key = ocr_dedupe.split("[REPEATED: ")[1].split("]")[0]
            repeated_content[key] = ocr

        tables_field = page.get("tables") or page.get("table_infos") or []
        tables = []
        for table_info in tables_field:
            tbl = serialize_table(table_info.get("path", ""))
            if tbl:
                tables.append(tbl)

        charts = []
        chart_data = page.get("chart_json")
        if chart_data:
            try:
                chart_obj = (
                    json.loads(chart_data)
                    if isinstance(chart_data, str)
                    else chart_data
                )

                charts.append(
                    {
                        "type": chart_obj.get("type", "unknown"),
                        "data": chart_obj.get("data", chart_obj),
                    }
                )
            except Exception as e:
                print(f"Chart parse error on page {page_num}: {e}")

        page_obj = {
            "page_number": page_num,
        }

        if text_dedupe:
            page_obj["text"] = text_dedupe
        if ocr_dedupe:
            page_obj["ocr"] = ocr_dedupe
        if tables:
            page_obj["tables"] = tables
        if charts:
            page_obj["charts"] = charts

        compressed_pages.append(page_obj)

    context_obj: Dict[str, Any] = {"document": compressed_pages}

    if repeated_content:
        context_obj["repeated_content_reference"] = repeated_content

    return json.dumps(context_obj, ensure_ascii=False, indent=1)


def ultra_compact_compress(parsed_data: List[Dict[str, Any]]) -> str:
    pages = []

    for page in parsed_data:
        p = {"pg": page.get("page", "?")}

        text = normalize_text(page.get("text", ""))
        ocr = normalize_text(page.get("ocr_text") or page.get("ocr") or "")

        if text and ocr:
            if (
                text in ocr
                or ocr in text
                or len(set(text.split()) & set(ocr.split()))
                / max(len(text.split()), len(ocr.split()))
                > 0.8
            ):
                p["content"] = text if len(text) > len(ocr) else ocr
            else:
                p["content"] = f"{text}\n[OCR]: {ocr}"
        else:
            p["content"] = text or ocr or ""

        tables_field = page.get("tables") or page.get("table_infos") or []
        if tables_field:
            tables = []
            for tbl_info in tables_field:
                tbl = serialize_table(tbl_info.get("path", ""))
                if tbl:
                    tables.append(tbl)
            if tables:
                p["tables"] = tables

        chart_data = page.get("chart_json")
        if chart_data:
            try:
                chart = (
                    json.loads(chart_data)
                    if isinstance(chart_data, str)
                    else chart_data
                )
                p["chart"] = chart
            except:
                pass

        pages.append(p)

    return json.dumps({"pages": pages}, ensure_ascii=False, separators=(",", ":"))
