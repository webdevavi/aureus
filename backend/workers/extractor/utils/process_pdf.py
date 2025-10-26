from concurrent.futures import ProcessPoolExecutor, as_completed
from rich.progress import Progress
from rich import print
from backend.workers.extractor.utils.process_page import process_page


def process_pdf(pdf_path: str, max_workers: int = 2):
    import fitz

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    if not doc.is_closed:
        try:
            doc.close()
        except Exception:
            pass

    print(f"[yellow]Starting extraction for:[/yellow] {pdf_path}")
    print(f"[cyan]Total pages:[/cyan] {total_pages}")

    results = []

    with Progress() as progress:
        task = progress.add_task("[cyan]Extracting pages...", total=total_pages)

        with ProcessPoolExecutor(
            max_workers=max_workers,
        ) as executor:
            futures = {
                executor.submit(
                    process_page,
                    pdf_path,
                    i,
                    True,
                ): i
                for i in range(1, total_pages + 1)
            }

            for fut in as_completed(futures):
                page_num = futures[fut]
                try:
                    result = fut.result()
                except Exception as e:
                    result = {"page": page_num, "error": str(e)}

                results.append(result)
                progress.advance(task)

    results.sort(key=lambda x: x["page"])

    print(f"[green]Parallel extraction complete for {len(results)} pages.[/green]")
    return results
