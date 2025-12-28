from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.db.duckdb_store import connect


def generate_html_report(project_dir: Path, dataset: str, title: str) -> Path:
    reports_dir = project_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    with connect(project_dir) as conn:
        df = conn.execute(f"SELECT * FROM {dataset} LIMIT 500").fetchdf()

    html = f"""
    <html>
      <head><title>{title}</title></head>
      <body>
        <h1>{title}</h1>
        <p>Dataset: {dataset}</p>
        {df.to_html(index=False)}
      </body>
    </html>
    """
    output_path = reports_dir / f"{dataset}_report.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def generate_pdf_report(project_dir: Path, dataset: str, title: str) -> Path:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise RuntimeError("reportlab is required for PDF export") from exc

    reports_dir = project_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    output_path = reports_dir / f"{dataset}_report.pdf"

    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height - 50, title)
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 80, f"Dataset: {dataset}")
    c.drawString(40, height - 110, "Preview (first 5 rows):")

    with connect(project_dir) as conn:
        df = conn.execute(f"SELECT * FROM {dataset} LIMIT 5").fetchdf()

    y = height - 140
    for _, row in df.iterrows():
        c.drawString(40, y, ", ".join(str(value) for value in row.values))
        y -= 20

    c.showPage()
    c.save()
    return output_path
