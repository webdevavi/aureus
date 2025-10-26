import os
from typing import Any, cast, Union
from rich import print
from pathlib import Path
from PIL import Image, ImageDraw
from backend.workers.extractor.utils.ocr_manager import load_easyocr


EasyOCRResult = Union[
    tuple[list[list[float]], str],
    tuple[list[list[float]], str, float],
]


def extract_easyocr_text(
    image_path: str, output_dir: str = "tmp/output/ai_ocr", visualize: bool = True
) -> dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    reader = load_easyocr()
    print(f"[blue]Processing: {Path(image_path).name}[/blue]")

    try:
        results = reader.readtext(image_path, detail=1, paragraph=True)
        results_typed = cast(list[EasyOCRResult], results)

        text = " ".join([res[1] for res in results_typed]).strip()
        print(
            f"[green]OCR Output:[/green] {text[:200]}{'…' if len(text) > 200 else ''}"
        )

        txt_path = Path(output_dir) / f"{Path(image_path).stem}_easyocr.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)

        preview_path = None
        if visualize and results_typed:
            image = Image.open(image_path).convert("L")
            draw = ImageDraw.Draw(image)

            for result in results_typed:
                try:
                    if len(result) == 3:
                        bbox, txt, conf = result
                    elif len(result) == 2:
                        bbox, txt = result
                        conf = None
                    else:
                        continue

                    pts = [tuple(map(float, p)) for p in bbox]
                    draw.polygon(pts, outline=(0, 255, 0), width=2)
                except Exception as e:
                    print(f"[yellow]Skipped invalid bbox ({e})[/yellow]")

            preview_path = Path(output_dir) / f"{Path(image_path).stem}_ocr_preview.png"
            image.save(preview_path)
            print(f"[cyan]Visualization saved to: {preview_path.name}[/cyan]")

        return {
            "text": text,
            "chars": len(text),
            "ocr_engine": "easyocr",
            "text_path": str(txt_path),
            "preview_path": str(preview_path) if preview_path else None,
        }

    except Exception as e:
        print(f"[red]EasyOCR failed on {image_path}: {e}[/red]")
        return {
            "text": "",
            "chars": 0,
            "ocr_engine": "easyocr",
            "error": str(e),
        }
