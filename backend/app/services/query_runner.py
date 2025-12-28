from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class QueryClient(Protocol):
    def fetch_dataframe(self, query: str) -> pd.DataFrame:
        ...


@dataclass
class SqlServerClient:
    connection_string: str

    def fetch_dataframe(self, query: str) -> pd.DataFrame:
        try:
            from sqlalchemy import create_engine
        except ImportError as exc:
            raise RuntimeError("SQLAlchemy is required for SQL Server queries") from exc
        engine = create_engine(self.connection_string)
        with engine.connect() as conn:
            return pd.read_sql(query, conn)


def build_sqlserver_connection_string(
    host: str,
    port: int,
    database: str,
    username: str | None,
    password: str | None,
    trusted: bool,
) -> str:
    if trusted:
        return (
            "mssql+pyodbc://@{host}:{port}/{database}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
            "&trusted_connection=yes"
        ).format(host=host, port=port, database=database)
    if not username or not password:
        raise ValueError("Username and password are required when not using trusted auth")
    return (
        "mssql+pyodbc://{username}:{password}@{host}:{port}/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    ).format(
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )


def run_query(client: QueryClient, query: str) -> pd.DataFrame:
    return client.fetch_dataframe(query)
