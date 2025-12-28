from pathlib import Path

import pandas as pd

from app.db.duckdb_store import create_project, list_tables
from app.services.importer import import_csv


def test_import_csv_with_timestamp(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    create_project(project_dir, "Test", None)

    sample = "ts,value\n2024-01-01T00:00:00Z,1\n2024-01-01T00:00:01Z,2\n"
    file_path = project_dir / "sample.csv"
    file_path.write_text(sample, encoding="utf-8")

    result = import_csv(project_dir, file_path, {"dataset_name": "sensor_data"})

    assert result["dataset_name"] == "sensor_data"
    assert "sensor_data" in list_tables(project_dir)
