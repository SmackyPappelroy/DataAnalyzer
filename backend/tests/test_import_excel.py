from pathlib import Path

import pandas as pd

from app.db.duckdb_store import create_project, list_tables
from app.services.importer import import_excel


def test_import_excel_with_sheet_and_header(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    create_project(project_dir, "Test", None)

    df = pd.DataFrame({"ts": ["2024-01-01", "2024-01-02"], "value": [1, 2]})
    file_path = project_dir / "sample.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df.to_excel(writer, sheet_name="Data", index=False)

    result = import_excel(project_dir, file_path, {"dataset_name": "excel_data", "sheet_name": "Data"})

    assert result["dataset_name"] == "excel_data"
    assert "excel_data" in list_tables(project_dir)
