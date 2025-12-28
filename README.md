# DataAnalyzer

Local-first app (offline) för automationsingenjörer som behöver importera, ansluta, analysera och visualisera logg- och tidsseriedata från industriella system. All data stannar lokalt i projektets DuckDB-fil.

## Vald stack
**Alternativ 2: Lokal webapp (React + FastAPI)**
- Snabb att starta lokalt med ett kommando.
- Enkel att packa till en offline-app senare (t.ex. med Electron/Tauri som skal).
- API och UI är separerade vilket gör plugin-arkitektur enklare.

## Struktur
```
backend/            FastAPI API + DuckDB + import/recipes/reports
frontend/           React UI (MVP layout)
data/projects/      Lokala projekt (DuckDB + metadata + reports)
```

## Installation
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> För SQL Server krävs ODBC Driver 17/18 samt `pyodbc`. Installera vid behov:
> ```bash
> pip install pyodbc
> ```

### Frontend
```bash
cd frontend
npm install
```

## Start
### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## Skapa projekt (MVP)
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Plant Project","description":"Demo"}'
```

Spara `project_id` från svaret (behövs för import, queries och recept).

## Importera Excel
```bash
curl -X POST "http://localhost:8000/api/import/excel" \
  -F "project_id=<project_id>" \
  -F "dataset_name=excel_data" \
  -F "sheet_name=Data" \
  -F "file=@/path/to/file.xlsx"
```

## Skapa SQL Server-connection
```bash
curl -X POST "http://localhost:8000/api/connections/sqlserver?project_id=<project_id>" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "plant_sql",
        "host": "localhost",
        "port": 1433,
        "database": "Plant",
        "username": "sa",
        "password": "secret",
        "trusted": false
      }'
```

## Kör SQL query och spara dataset
```bash
curl -X POST "http://localhost:8000/api/query/sqlserver?project_id=<project_id>" \
  -H "Content-Type: application/json" \
  -d '{"connection_name":"plant_sql","query":"SELECT TOP 100 * FROM dbo.Signals","dataset_name":"sql_series"}'
```

## Kör ett Python-recept
Exempelrecept finns i `backend/app/recipes/`.
```bash
curl -X POST "http://localhost:8000/api/recipes/run?project_id=<project_id>" \
  -H "Content-Type: application/json" \
  -d '{"recipe_name":"trend_and_deviation.py","parameters":{"window":60,"threshold":3.0}}'
```

## Skapa rapport (HTML/PDF)
```bash
curl -X POST "http://localhost:8000/api/reports?project_id=<project_id>" \
  -F "dataset=sql_series" \
  -F "title=Quick Report" \
  -F "format=html"

curl -X POST "http://localhost:8000/api/reports?project_id=<project_id>" \
  -F "dataset=sql_series" \
  -F "title=Quick Report" \
  -F "format=pdf"
```

## Exportera projekt-bundle
```bash
curl http://localhost:8000/api/projects/<project_id>/export
```

## Exempelrecept
- **alarm_event_timeline.py** – tidslinje för alarm/events
- **trend_and_deviation.py** – trend + outlier-detektion
- **db_join_time_sync.py** – join och tidsynk mellan SQL- och CSV-data

## Tester
```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

## TODO (framtida plugins)
- InfluxDB/TimescaleDB connector
- OPC UA import
- MQTT log ingest
- Historian (PI/Proficy) connectors
- Rust-baserad importpipeline för högre prestanda
- Sandboxed recipe runtime (Pyodide/containers)
- Snippet marketplace och plugin registry
```
