from __future__ import annotations

import json
import uuid
from pathlib import Path

import pandas as pd
import zipfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.db.duckdb_store import create_project, list_tables
from app.models import (
    CsvImportOptions,
    ExcelImportOptions,
    ProjectCreateRequest,
    ProjectResponse,
    RecipeRunRequest,
    RecipeRunResponse,
    SqlQueryRequest,
    SqlServerConnection,
)
from app.services.connections import SqlServerConnectionInfo, get_sqlserver_connection, save_sqlserver_connection
from app.services.importer import import_csv, import_excel
from app.services.query_runner import SqlServerClient, build_sqlserver_connection_string
from app.services.recipes import run_recipe
from app.services.reports import generate_html_report, generate_pdf_report
from app.settings import PROJECTS_DIR
from app.utils.file_utils import ensure_path_within, sanitize_name

app = FastAPI(title="DataAnalyzer Local API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)

INDEX_PATH = PROJECTS_DIR / "index.json"


def load_index() -> dict:
    if INDEX_PATH.exists():
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    return {}


def save_index(index: dict) -> None:
    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")


def get_project_dir(project_id: str) -> Path:
    index = load_index()
    project = index.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ensure_path_within(PROJECTS_DIR, Path(project["path"]))


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project_endpoint(payload: ProjectCreateRequest) -> ProjectResponse:
    project_id = str(uuid.uuid4())
    project_name = sanitize_name(payload.name)
    project_dir = PROJECTS_DIR / f"{project_name}_{project_id}"
    create_project(project_dir, payload.name, payload.description)

    index = load_index()
    index[project_id] = {"name": payload.name, "path": str(project_dir)}
    save_index(index)

    return ProjectResponse(project_id=project_id, name=payload.name, description=payload.description, path=str(project_dir))


@app.get("/api/projects")
async def list_projects() -> dict:
    return load_index()


@app.post("/api/import/csv")
async def import_csv_endpoint(
    project_id: str = Form(...),
    dataset_name: str = Form(...),
    delimiter: str | None = Form(None),
    encoding: str | None = Form(None),
    decimal: str | None = Form(None),
    file: UploadFile = File(...),
) -> dict:
    project_dir = get_project_dir(project_id)
    temp_path = project_dir / file.filename
    temp_path.write_bytes(await file.read())
    options = CsvImportOptions(
        dataset_name=dataset_name,
        delimiter=delimiter,
        encoding=encoding,
        decimal=decimal,
    )
    result = import_csv(project_dir, temp_path, options.dict())
    temp_path.unlink(missing_ok=True)
    return result


@app.post("/api/import/excel")
async def import_excel_endpoint(
    project_id: str = Form(...),
    dataset_name: str = Form(...),
    sheet_name: str | None = Form(None),
    header_row: int | None = Form(0),
    file: UploadFile = File(...),
) -> dict:
    project_dir = get_project_dir(project_id)
    temp_path = project_dir / file.filename
    temp_path.write_bytes(await file.read())
    options = ExcelImportOptions(
        dataset_name=dataset_name,
        sheet_name=sheet_name,
        header_row=header_row,
    )
    result = import_excel(project_dir, temp_path, options.dict())
    temp_path.unlink(missing_ok=True)
    return result


@app.get("/api/datasets")
async def list_datasets(project_id: str) -> dict:
    project_dir = get_project_dir(project_id)
    return {"datasets": list_tables(project_dir)}


@app.post("/api/connections/sqlserver")
async def save_sqlserver_connection_endpoint(project_id: str, payload: SqlServerConnection) -> dict:
    project_dir = get_project_dir(project_id)
    connection = SqlServerConnectionInfo(**payload.dict())
    save_sqlserver_connection(project_dir, connection)
    return {"status": "saved"}


@app.post("/api/query/sqlserver")
async def query_sqlserver_endpoint(project_id: str, payload: SqlQueryRequest) -> dict:
    project_dir = get_project_dir(project_id)
    connection = get_sqlserver_connection(project_dir, payload.connection_name)
    connection_string = build_sqlserver_connection_string(
        host=connection.host,
        port=connection.port,
        database=connection.database,
        username=connection.username,
        password=connection.password,
        trusted=connection.trusted,
    )
    client = SqlServerClient(connection_string)
    df = client.fetch_dataframe(payload.query)
    from app.db.duckdb_store import save_dataframe
    save_dataframe(project_dir, sanitize_name(payload.dataset_name), df)
    return {"status": "imported", "rows": len(df)}


@app.post("/api/recipes/run", response_model=RecipeRunResponse)
async def run_recipe_endpoint(project_id: str, payload: RecipeRunRequest) -> RecipeRunResponse:
    project_dir = get_project_dir(project_id)
    recipe_path = ensure_path_within(Path(__file__).resolve().parent / "recipes", Path(__file__).resolve().parent / "recipes" / payload.recipe_name)
    if not recipe_path.exists():
        raise HTTPException(status_code=404, detail="Recipe not found")
    result = run_recipe(project_dir, recipe_path, payload.parameters)
    return RecipeRunResponse(status=result.status, logs=result.logs, outputs=result.outputs)


@app.get("/api/recipes")
async def list_recipes() -> dict:
    recipes_dir = Path(__file__).resolve().parent / "recipes"
    recipes = [path.name for path in recipes_dir.glob("*.py")]
    return {"recipes": recipes}


@app.post("/api/reports")
async def create_report(project_id: str, dataset: str = Form(...), title: str = Form("Report"), format: str = Form("html")) -> dict:
    project_dir = get_project_dir(project_id)
    if format == "html":
        report_path = generate_html_report(project_dir, dataset, title)
    elif format == "pdf":
        report_path = generate_pdf_report(project_dir, dataset, title)
    else:
        raise HTTPException(status_code=400, detail="Unsupported report format")
    return {"status": "created", "path": str(report_path)}


@app.get("/api/projects/{project_id}/export")
async def export_project_bundle(project_id: str) -> dict:
    project_dir = get_project_dir(project_id)
    bundle_path = project_dir / f"{project_dir.name}.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in project_dir.rglob("*"):
            if path.is_file() and path != bundle_path:
                archive.write(path, path.relative_to(project_dir))
    return {"status": "created", "path": str(bundle_path)}
