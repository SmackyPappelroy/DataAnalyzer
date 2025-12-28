from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from app.db.duckdb_store import connect, save_dataframe
from app.utils.file_utils import sanitize_name


@dataclass
class RecipeResult:
    status: str
    logs: list[str]
    outputs: list[str]


def run_recipe(project_dir: Path, recipe_path: Path, parameters: dict[str, Any]) -> RecipeResult:
    logs: list[str] = []
    outputs: list[str] = []

    def log(message: str) -> None:
        logs.append(message)

    def load(name: str) -> pd.DataFrame:
        with connect(project_dir) as conn:
            return conn.execute(f"SELECT * FROM {name}").fetchdf()

    def query_duckdb(sql: str) -> pd.DataFrame:
        with connect(project_dir) as conn:
            return conn.execute(sql).fetchdf()

    def save_table(name: str, df: pd.DataFrame) -> None:
        table_name = sanitize_name(name)
        save_dataframe(project_dir, table_name, df)
        outputs.append(table_name)

    def save_timeseries(name: str, df: pd.DataFrame, time_col: str = "ts") -> None:
        df = df.copy()
        if time_col not in df.columns:
            raise ValueError(f"Missing time column: {time_col}")
        save_table(name, df)

    def plot_timeseries(*_args: Any, **_kwargs: Any) -> None:
        logs.append("plot_timeseries called (UI handles visualization)")

    def add_event_markers(*_args: Any, **_kwargs: Any) -> None:
        logs.append("add_event_markers called (UI handles visualization)")

    api: dict[str, Callable[..., Any]] = {
        "load": load,
        "query_duckdb": query_duckdb,
        "save_table": save_table,
        "save_timeseries": save_timeseries,
        "plot_timeseries": plot_timeseries,
        "add_event_markers": add_event_markers,
        "log": log,
        "params": parameters,
    }

    source = recipe_path.read_text(encoding="utf-8")
    compiled = compile(source, recipe_path.name, "exec")
    exec(compiled, api)

    history_path = project_dir / "recipe_history.json"
    history = []
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    history.append({
        "recipe": recipe_path.name,
        "parameters": parameters,
        "outputs": outputs,
        "logs": logs,
    })
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    return RecipeResult(status="success", logs=logs, outputs=outputs)
