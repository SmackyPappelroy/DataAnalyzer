from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    description: Optional[str] = None
    path: str


class CsvImportOptions(BaseModel):
    dataset_name: str
    delimiter: Optional[str] = None
    encoding: Optional[str] = None
    decimal: Optional[str] = None
    timestamp_column: Optional[str] = None
    timezone: Optional[str] = None


class ExcelImportOptions(BaseModel):
    dataset_name: str
    sheet_name: Optional[str] = None
    header_row: Optional[int] = 0
    start_row: Optional[int] = None
    timestamp_column: Optional[str] = None
    timezone: Optional[str] = None


class SqlServerConnection(BaseModel):
    name: str
    host: str
    port: int = 1433
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    trusted: bool = False


class SqlQueryRequest(BaseModel):
    connection_name: str
    query: str
    dataset_name: str


class RecipeRunRequest(BaseModel):
    recipe_name: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class RecipeRunResponse(BaseModel):
    status: str
    logs: list[str]
    outputs: list[str]
