"""
Script para ejecutar el caso de uso 3.2.
Utiliza `json` for serializing reports and logs; `sys` for runtime path wiring; `pathlib.Path` for cross-platform filesystem paths; ingestion adapters to isolate data-loading concerns; core services implement business rules while respecting Dependency Inversion.
Este modulo sigue SOLID: Single Responsibility keeps orchestration focused, Open/Closed lets new services plug in, y Dependency Inversion depends on abstractions instead of concrete implementations.
"""




import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.core.services import AppointmentReviewService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_JSON = Path("reports/appointment_review_log.json")
DEFAULT_HTML = Path("reports/appointment_review_summary.html")


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    repo = JsonAppointmentRepository(DEFAULT_DATASET)
    service = AppointmentReviewService(repo)
    report = service.review()

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html(report), encoding="utf-8")

    print("🔍 Caso de uso 3.2: Validación de citas Completada/Cancelada")
    print(f"📋 Citas procesadas: {report.total_citas}")
    print(f"⚠️ Citas marcadas para revisión: {report.reviewed_citas}")
    print(f"📂 JSON disponible en: {DEFAULT_JSON.resolve()}")
    print(f"🌐 Reporte HTML: {DEFAULT_HTML.resolve()}")


def build_html(report) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    rows = "\n".join(
        "<tr>"
        f"<td>{entry.id_cita}</td>"
        f"<td>{entry.estado_cita}</td>"
        f"<td>{entry.fecha_cita or '—'}</td>"
        f"<td>{entry.medico or '—'}</td>"
        f"<td>{', '.join(entry.issues)}</td>"
        "</tr>"
        for entry in report.entries[:50]
    )
    if not rows:
        rows = "<tr><td colspan='5' style='text-align:center;'>No hay citas incompletas</td></tr>"

    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #1565c0; }
  h2 { color: #2e7d32; margin-top: 32px; }
  h3 { color: #7b1fa2; margin-top: 24px; }
  .note { background: #e3f2fd; border-left: 4px solid #1976d2; padding: 16px 20px; margin: 18px 0; border-radius: 7px; }
  .note ul { list-style: disc inside; margin: 0; padding-left: 1.2em; }
  .note li { margin-bottom: 3px; line-height: 1.35; }
  .note p { margin: 0 0 6px 0; line-height: 1.5; }
  .footer { text-align: right; color: #888; font-size: 1em; margin-top: 40px; }
  .params table { border-collapse: collapse; width: 100%; margin: 10px 0; }
  .params th, .params td { border: 1px solid #ccc; padding: 6px; }
  @media (max-width: 600px) { .container { padding: 16px 8px; } }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: left; }
  th { background: #dbeafe; }
  </style>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte caso de uso 3.2</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Citas completadas/canceladas marcadas para revisión</h1>
    <div class="note">
      <p>Revisamos estados <strong>Completada</strong> y <strong>Cancelada</strong> para asegurarnos de que tengan <code>fecha_cita</code> y <code>medico</code> correctos.</p>
    </div>
    <div class="note">
      <p><strong>Resumen:</strong> {report.reviewed_citas} citas (de {report.total_citas}) necesitan atención.</p>
    </div>
    <table>
      <thead>
        <tr>
          <th>id_cita</th>
          <th>estado</th>
          <th>fecha_cita</th>
          <th>médico</th>
          <th>issues</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Reporte generado desde <code>scripts/run_appointment_review.py</code>.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
