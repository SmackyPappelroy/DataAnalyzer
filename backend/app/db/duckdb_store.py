from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from app.utils.file_utils import ensure_path_within


def create_project(project_dir: Path, name: str, description: str | None) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    db_path = project_dir / "project.duckdb"
    duckdb.connect(str(db_path)).close()
    metadata = {
        "name": name,
        "description": description,
        "datasets": [],
        "connections": {},
    }
    (project_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def load_metadata(project_dir: Path) -> dict[str, Any]:
    metadata_path = ensure_path_within(project_dir, project_dir / "metadata.json")
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def save_metadata(project_dir: Path, metadata: dict[str, Any]) -> None:
    metadata_path = ensure_path_within(project_dir, project_dir / "metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def connect(project_dir: Path) -> duckdb.DuckDBPyConnection:
    db_path = ensure_path_within(project_dir, project_dir / "project.duckdb")
    return duckdb.connect(str(db_path))


def save_dataframe(project_dir: Path, table_name: str, df: pd.DataFrame) -> None:
    with connect(project_dir) as conn:
        conn.register("_import_df", df)
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM _import_df")


def list_tables(project_dir: Path) -> list[str]:
    with connect(project_dir) as conn:
        rows = conn.execute("SHOW TABLES").fetchall()
    return [row[0] for row in rows]
