"""Script principal para implementar caso de uso 2.2."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.core.services import AppointmentAlertService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_JSON = Path("reports/appointment_alerts_log.json")
DEFAULT_HTML = Path("reports/appointment_alerts_summary.html")


def main() -> None:
    repository = JsonAppointmentRepository(DEFAULT_DATASET)
    service = AppointmentAlertService(repository)
    report = service.scan_alerts()

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html_report(report), encoding="utf-8")

    print("🚨 Caso de uso 2.2: Alertas para citas incompletas")
    print(f"📋 Registros procesados: {report.total_records}")
    print(f"⚠️ Alertas generadas: {report.alerts}")
    print(f"📂 JSON de alertas: {DEFAULT_JSON.resolve()}")
    print(f"🌐 Reporte HTML: {DEFAULT_HTML.resolve()}")


def build_html_report(report) -> str:
    entries = report.entries[:40]
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.id_cita}</td>"
        f"<td>{entry.id_paciente or '—'}</td>"
        f"<td>{entry.especialidad or '—'}</td>"
        f"<td>{'sí' if entry.falta_fecha else 'no'}</td>"
        f"<td>{'sí' if entry.falta_medico else 'no'}</td>"
        f"<td>{entry.note}</td>"
        "</tr>"
        for entry in entries
    )
    if not rows:
        rows = "<tr><td colspan='6' style='text-align:center;'>No se detectaron alertas</td></tr>"

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
  .tag { background: #e3f2fd; color: #1565c0; border-radius: 4px; padding: 3px 8px; margin-left: 6px; font-size: 0.95em; }
  dt { color: #2e7d32; font-weight: bold; margin-top: 10px; }
  dd { margin-bottom: 10px; }
  .params table { border-collapse: collapse; width: 100%; margin: 10px 0; }
  .params th, .params td { border: 1px solid #ccc; padding: 6px; }
  .important { background: #fffde7; border-left: 4px solid #fbc02d; padding: 12px 18px; margin: 18px 0; border-radius: 5px; }
  .sideEffects ul, .solid ul { margin: 0; padding-left: 20px; }
  @media (max-width: 600px) { .container { padding: 16px 8px; } }
  /* Code block styling */
  pre { background: #f6f8fa; padding: 14px; border-radius: 8px; overflow: auto; font-size: 0.92em; }
  code { font-family: Consolas, 'Courier New', monospace; }
  .row { display:flex; gap:20px; flex-wrap:wrap; }
  .col { flex:1 1 420px; }
  /* Small visual helpers */
  .endpoint { border: 1px solid #e0e0e0; padding: 12px 14px; border-radius: 8px; background: #fff; box-shadow: 0 3px 8px rgba(0,0,0,0.04); }
  .json { white-space: pre; font-family: Consolas, 'Courier New', monospace; font-size: 0.95em; }
  .success { color: #2e7d32; font-weight: 600; }
  .error { color: #c62828; font-weight: 600; }"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte caso de uso 2.2</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Alertas de citas incompletas</h1>
    <div class="note">
      <p>Se generan alertas automáticas cuando falta <strong>fecha_cita</strong> o <strong>médico</strong>. El equipo de operaciones debe validar manualmente estos registros.</p>
    </div>
    <table>
      <thead>
        <tr>
          <th>id_cita</th>
          <th>id_paciente</th>
          <th>especialidad</th>
          <th>sin fecha</th>
          <th>sin médico</th>
          <th>nota</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Reporte generado desde <code>scripts/run_appointment_alerts.py</code>.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
