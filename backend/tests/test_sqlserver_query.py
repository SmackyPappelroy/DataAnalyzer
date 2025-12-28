from pathlib import Path

import pandas as pd

from app.db.duckdb_store import create_project, list_tables, save_dataframe
from app.services.query_runner import build_sqlserver_connection_string, run_query


def test_build_sqlserver_connection_string() -> None:
    connection_string = build_sqlserver_connection_string(
        host="localhost",
        port=1433,
        database="Plant",
        username="sa",
        password="secret",
        trusted=False,
    )
    assert "mssql+pyodbc://sa:secret@localhost:1433/Plant" in connection_string


def test_mock_sqlserver_query_fetch(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    create_project(project_dir, "Test", None)

    df = pd.DataFrame({"ts": ["2024-01-01"], "value": [42]})
    class FakeClient:
        def fetch_dataframe(self, query: str) -> pd.DataFrame:
            assert query == "SELECT * FROM sensor"
            return df

    result = run_query(FakeClient(), "SELECT * FROM sensor")
    save_dataframe(project_dir, "sql_series", result)

    assert "sql_series" in list_tables(project_dir)
