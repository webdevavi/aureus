import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="camelot")

import camelot.io as camelot
import os
import pandas as pd
import re
from typing import List, Dict
import pdfplumber


def is_probably_table(df: pd.DataFrame) -> bool:
    if df.shape[0] < 2 or df.shape[1] < 2:
        return False
    values = " ".join(df.astype(str).fillna("").values.flatten())
    digits = len(re.findall(r"[\d%]", values))
    ratio = digits / max(len(values), 1)
    return ratio > 0.15


def clean_numeric_cells(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.astype(str).fillna("")
    df = df.replace(r"(\d)\s*,\s*(\d)", r"\1\2", regex=True)
    df = df.replace(r"(\d)\s+(\d)", r"\1\2", regex=True)
    df = df.map(lambda x: str(x).strip())  # pyright: ignore[reportCallIssue]
    return df


def merge_adjacent_tables(tables: List[pd.DataFrame]) -> List[pd.DataFrame]:
    merged = []
    skip_next = False
    for i, df in enumerate(tables):
        if skip_next:
            skip_next = False
            continue
        if i + 1 < len(tables):
            nxt = tables[i + 1]
            if (
                abs(len(df) - len(nxt)) <= 1
                and len(df.columns) < 4
                and len(nxt.columns) < 4
            ):
                merged.append(
                    pd.concat(
                        [df.reset_index(drop=True), nxt.reset_index(drop=True)], axis=1
                    )
                )
                skip_next = True
                continue
        merged.append(df)
    return merged


def extract_tables_from_page(
    pdf_path: str, page_number: int, output_dir: str = "tmp/output/tables"
) -> List[Dict[str, str]]:
    os.makedirs(output_dir, exist_ok=True)
    tables_info: List[Dict[str, str]] = []

    try:
        lattice = camelot.read_pdf(pdf_path, pages=str(page_number), flavor="lattice")
        stream = camelot.read_pdf(pdf_path, pages=str(page_number), flavor="stream")

        def best_result(a, b):
            if not a:
                return b
            if not b:
                return a
            if a[0].df.shape[1] >= b[0].df.shape[1]:
                return a
            return b

        results = best_result(lattice, stream)
    except Exception as e:
        print(f"Camelot failed on page {page_number}: {e}")
        results = []

    table_idx = 1
    dfs = []
    for t in results:
        df = clean_numeric_cells(t.df)
        if not is_probably_table(df):
            continue
        dfs.append(df)

    dfs = merge_adjacent_tables(dfs)  # refinement #2

    for df in dfs:
        csv_path = os.path.join(output_dir, f"page{page_number}_table{table_idx}.csv")
        df.to_csv(csv_path, index=False)
        tables_info.append(
            {
                "page": str(page_number),
                "rows": str(len(df)),
                "cols": str(len(df.columns)),
                "path": csv_path,
            }
        )
        table_idx += 1

    if not tables_info:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[page_number - 1]
                tables = page.extract_tables(
                    {
                        "vertical_strategy": "lines",
                        "horizontal_strategy": "lines",
                        "intersection_tolerance": 5,
                        "snap_tolerance": 3,
                        "join_tolerance": 3,
                    }
                )
                dfs_plumber = []
                for t in tables:
                    df = pd.DataFrame(t).dropna(how="all").dropna(axis=1, how="all")
                    df = clean_numeric_cells(df)
                    if not is_probably_table(df):
                        continue
                    dfs_plumber.append(df)
                dfs_plumber = merge_adjacent_tables(dfs_plumber)
                for df in dfs_plumber:
                    csv_path = os.path.join(
                        output_dir, f"page{page_number}_table{table_idx}.csv"
                    )
                    df.to_csv(csv_path, index=False)
                    tables_info.append(
                        {
                            "page": str(page_number),
                            "rows": str(len(df)),
                            "cols": str(len(df.columns)),
                            "path": csv_path,
                        }
                    )
                    table_idx += 1
        except Exception as e:
            print(f"pdfplumber fallback failed on page {page_number}: {e}")

    return tables_info
