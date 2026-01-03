"""
Script para el caso 6.1: ETL completo hacia tablas limpias.
Utiliza `json` for serializing reports and logs; `sys` for runtime path wiring; `datetime` for cutoff or event dates; `pathlib.Path` for cross-platform filesystem paths; core services implement business rules while respecting Dependency Inversion.
Este modulo sigue SOLID: Single Responsibility keeps orchestration focused, Open/Closed lets new services plug in, y Dependency Inversion depends on abstractions instead of concrete implementations.
"""




import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.core.services import ETLPipelineService

DATASET = ROOT / "dataset_hospital 2 AWS.json"
REPORT_DIR = ROOT / "reports"
HTML_REPORT = REPORT_DIR / "etl" / "etl_summary.html"


def build_html(summary: dict) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    orphan_preview = summary.get("orphans", [])[:10]
    orphan_rows = "\n".join(f"<li>{oid}</li>" for oid in orphan_preview) or "<li>Sin registros huérfanos.</li>"
    clean_dir = REPORT_DIR / "etl"
    files = [
        ("Pacientes (CSV)", clean_dir / "pacientes_cleaned.csv"),
        ("Pacientes (Parquet)", clean_dir / "pacientes_cleaned.parquet"),
        ("Citas (CSV)", clean_dir / "citas_cleaned.csv"),
        ("Citas (Parquet)", clean_dir / "citas_cleaned.parquet"),
    ]
    file_rows = "\n".join(
        "<tr>"
        f"<td>{label}</td>"
        f"<td>{path.name}</td>"
        f"<td>{path.exists()}</td>"
        "</tr>"
        for label, path in files
    )
    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #1565c0; }
  h2 { color: #2e7d32; margin-top: 32px; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: left; }
  th { background: #dbeafe; }
  .note { background: #e3f2fd; border-left: 4px solid #1976d2; padding: 16px 20px; margin: 18px 0; border-radius: 7px; }
  .footer { text-align: right; color: #888; font-size: 1em; margin-top: 40px; }
  ul { padding-left: 1.2em; }
  """
    generated = summary.get("generated_at", datetime.utcnow().isoformat())
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte ETL 6.1</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>ETL hacia tablas limpias</h1>
    <div class="note">
      <p>Se aplicaron limpiezas de texto, normalización de fechas y eliminación de huérfanos antes de exportar los conjuntos limpios.</p>
    </div>
    <h2>Resumen</h2>
    <ul>
      <li>Total pacientes originales: {summary.get("patients_raw", 0)}</li>
      <li>Total citas originales: {summary.get("appointments_raw", 0)}</li>
      <li>Huérfanos eliminados: {len(summary.get("orphans", []))}</li>
      <li>Generado el: {generated}</li>
    </ul>
    <h2>Archivos exportados</h2>
    <table>
      <thead>
        <tr><th>Descripción</th><th>Archivo</th><th>Existe</th></tr>
      </thead>
      <tbody>
        {file_rows}
      </tbody>
    </table>
    <h2>Huérfanos destacados</h2>
    <ul>
      {orphan_rows}
    </ul>
    <div class="footer">
      Reporte generado desde <code>scripts/run_etl_pipeline.py</code>
    </div>
  </div>
</body>
</html>"""


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    service = ETLPipelineService(DATASET, REPORT_DIR)
    summary = service.run()
    summary["generated_at"] = datetime.utcnow().isoformat()

    print("🧰 Caso 6.1: ETL de JSON a tablas limpias")
    print(f"✅ Pacientes procesados: {summary['patients_raw']}")
    print(f"🧾 Citas procesadas: {summary['appointments_raw']}")
    print(f"🔍 Registros huérfanos eliminados: {len(summary['orphans'])}")
    print(f"📂 Archivos exportados en: {REPORT_DIR / 'etl'}")
    print(f"🧮 Resumen guardado: {json.dumps(summary, ensure_ascii=False)}")

    HTML_REPORT.parent.mkdir(parents=True, exist_ok=True)
    HTML_REPORT.write_text(build_html(summary), encoding="utf-8")
    print(f"📰 Reporte HTML disponible en: {HTML_REPORT.resolve()}")


if __name__ == "__main__":
    main()
