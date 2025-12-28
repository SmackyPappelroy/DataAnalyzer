from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pandas as pd

from app.db.duckdb_store import list_tables, load_metadata, save_dataframe, save_metadata
from app.utils.file_utils import sanitize_name


class ImportResult(dict):
    pass


def detect_csv_format(file_path: Path) -> dict[str, Any]:
    sample = file_path.read_text(encoding="utf-8", errors="ignore")[:4096]
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample)
        delimiter = dialect.delimiter
    except csv.Error:
        delimiter = ","
    return {"delimiter": delimiter}


def import_csv(project_dir: Path, file_path: Path, options: dict[str, Any]) -> ImportResult:
    detected = detect_csv_format(file_path)
    delimiter = options.get("delimiter") or detected["delimiter"]
    encoding = options.get("encoding") or "utf-8"
    decimal = options.get("decimal") or "."
    df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, decimal=decimal)
    dataset_name = sanitize_name(options["dataset_name"])
    save_dataframe(project_dir, dataset_name, df)

    metadata = load_metadata(project_dir)
    metadata["datasets"] = sorted(set(metadata.get("datasets", []) + [dataset_name]))
    save_metadata(project_dir, metadata)

    return ImportResult(
        dataset_name=dataset_name,
        rows=len(df),
        columns=list(df.columns),
        detected_format=detected,
        tables=list_tables(project_dir),
    )


def import_excel(project_dir: Path, file_path: Path, options: dict[str, Any]) -> ImportResult:
    sheet_name = options.get("sheet_name")
    header_row = options.get("header_row", 0)
    start_row = options.get("start_row")
    df = pd.read_excel(file_path, sheet_name=sheet_name or 0, header=header_row)
    if start_row:
        df = df.iloc[start_row:]
    dataset_name = sanitize_name(options["dataset_name"])
    save_dataframe(project_dir, dataset_name, df)

    metadata = load_metadata(project_dir)
    metadata["datasets"] = sorted(set(metadata.get("datasets", []) + [dataset_name]))
    save_metadata(project_dir, metadata)

    return ImportResult(
        dataset_name=dataset_name,
        rows=len(df),
        columns=list(df.columns),
        sheet_name=sheet_name or "0",
        tables=list_tables(project_dir),
    )
