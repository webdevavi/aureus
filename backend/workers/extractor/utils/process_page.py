from rich import print


def should_use_vision(analysis: dict, text: str) -> bool:
    if analysis.get("type") not in {"chart_present", "mixed"}:
        return False
    if analysis.get("visual_score", 0) < 0.6:
        return False
    if len(text) < 100:
        return False
    if any(k in text.lower() for k in ["thank you", "disclaimer", "appendix"]):
        return False
    return True


def process_page(pdf_path: str, page_num: int, openai_enabled: bool = True):
    from .table_extractor import extract_tables_from_page
    from .text_extractor import extract_text_from_pdf
    from .render_page import render_page_to_image
    from .chart_detector import analyze_page
    from .easyocr_fallback import extract_easyocr_text

    try:
        table_infos = extract_tables_from_page(pdf_path, page_num)

        text_info = extract_text_from_pdf(pdf_path, page_num) or {}
        text = str(text_info.get("text", "")).strip()
        text_length = len(text)
        print(f"[debug] Page {page_num} text len={len(text)}, preview={text[:100]!r}")

        img_path = render_page_to_image(pdf_path, page_num)
        analysis = analyze_page(img_path)
        visual_score = analysis.get("visual_score", 0.0)
        has_chart_like_elements = visual_score > 0.45

        ocr_engine = "embedded"
        ocr_text = text
        chart_json = None
        needs_vision = False

        if has_chart_like_elements:
            print(
                f"[blue]Page {page_num}: Chart/visual detected (score={visual_score:.2f})[/blue]"
            )
            if openai_enabled and should_use_vision(analysis, text):
                needs_vision = True
                print(f"Marked {img_path} for Vision batch")
                ocr_engine = "openai-vision+embedded"
            else:
                print(
                    "[dim cyan]Vision skipped due to low visual signal or redundant content[/dim cyan]"
                )
                ocr_text = extract_easyocr_text(img_path, visualize=False)["text"]
                ocr_engine = "easyocr+embedded"

        elif text_length > 50:
            print(f"[green]Page {page_num}: Text-only ({text_length} chars)[/green]")

        else:
            print(
                f"[yellow]Page {page_num}: Low text ({text_length} chars) — trying OCR[/yellow]"
            )
            try:
                easy = extract_easyocr_text(img_path, visualize=False)

                ocr_text = easy["text"]
                ocr_engine = "easyocr"

            except Exception as e:
                print(f"[red]All OCR failed for page {page_num}: {e}[/red]")
                ocr_text = ""
                ocr_engine = "none"

        return {
            "page": page_num,
            "table_infos": table_infos,
            "text": ocr_text,
            "ocr_engine": ocr_engine,
            "chart_json": chart_json,
            "analysis": analysis,
            "chars": len(ocr_text),
            "visual_score": visual_score,
            "needs_vision": needs_vision,
            "img_path": img_path,
        }

    except Exception as e:
        print(f"[red]process_page() crashed for page {page_num}: {e}[/red]")
        return {
            "page": page_num,
            "error": str(e),
            "ocr_engine": "failed",
            "chart_json": None,
            "analysis": {},
            "chars": 0,
        }
