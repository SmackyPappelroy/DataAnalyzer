from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.db.duckdb_store import load_metadata, save_metadata


@dataclass
class SqlServerConnectionInfo:
    name: str
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    trusted: bool = False


def save_sqlserver_connection(project_dir, connection: SqlServerConnectionInfo) -> None:
    metadata = load_metadata(project_dir)
    connections = metadata.get("connections", {})
    connections[connection.name] = {
        "type": "sqlserver",
        "host": connection.host,
        "port": connection.port,
        "database": connection.database,
        "username": connection.username,
        "password": connection.password,
        "trusted": connection.trusted,
    }
    metadata["connections"] = connections
    save_metadata(project_dir, metadata)


def get_sqlserver_connection(project_dir, name: str) -> SqlServerConnectionInfo:
    metadata = load_metadata(project_dir)
    config = metadata.get("connections", {}).get(name)
    if not config:
        raise ValueError(f"Connection '{name}' not found")
    return SqlServerConnectionInfo(
        name=name,
        host=config["host"],
        port=config.get("port", 1433),
        database=config["database"],
        username=config.get("username"),
        password=config.get("password"),
        trusted=config.get("trusted", False),
    )
