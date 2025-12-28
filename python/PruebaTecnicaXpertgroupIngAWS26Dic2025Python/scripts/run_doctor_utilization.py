"""Script para caso 7.2: monitorear y notificar desviaciones de agenda por médico."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.core.services import DoctorUtilizationService

DATASET = ROOT / "dataset_hospital 2 AWS.json"
REPORT_DIR = ROOT / "reports"
LOG_JSON = REPORT_DIR / "doctor_utilization_log.json"
SUMMARY_HTML = REPORT_DIR / "doctor_utilization_summary.html"


def main() -> None:
    service = DoctorUtilizationService(JsonAppointmentRepository(DATASET))
    report = service.analyze()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_HTML.write_text(build_html(report), encoding="utf-8")

    print("📈 Caso 7.2: Monitoreo de cumplimiento de agenda por médico/especialidad")
    print(f"✅ JSON disponible en: {LOG_JSON.resolve()}")
    print(f"📰 HTML disponible en: {SUMMARY_HTML.resolve()}")
    print(f"⚠️ Alertas detectadas: {len(report.entries)}")


def build_html(report) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.doctor}</td>"
        f"<td>{entry.specialty}</td>"
        f"<td>{entry.completed}</td>"
        f"<td>{entry.scheduled}</td>"
        f"<td>{round(entry.utilization_rate * 100, 1)}%</td>"
        f"<td>{round(entry.cancellation_rate * 100, 1)}%</td>"
        f"<td>{round(entry.deviation * 100, 1)}%</td>"
        f"<td>{entry.status.replace('_',' ').title()}</td>"
        "</tr>"
        for entry in report.entries
    ) or "<tr><td colspan='8' style='text-align:center;'>No se detectaron desviaciones en la utilización.</td></tr>"

    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 980px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.08); padding: 32px 40px; }
  h1 { color: #0f172a; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: center; }
  th { background: #e0f2fe; }
  .note { background: #e0f2fe; border-left: 4px solid #0284c7; padding: 16px; border-radius: 6px; }
  .footer { margin-top: 24px; text-align: right; color: #555; }
  """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Monitor de cumplimiento 7.2</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Monitoreo de cumplimiento de agenda</h1>
    <p class="note">Comparamos citas completadas vs. desviaciones (cancelaciones/reprogramaciones) para cada médico y especialidad.</p>
    <p><strong>Umbral de utilización:</strong> {int(report.threshold * 100)}%, <strong>Cancelaciones toleradas:</strong> {int(report.cancellation_threshold * 100)}%</p>
    <table>
      <thead>
        <tr>
          <th>Doctor</th>
          <th>Especialidad</th>
          <th>Completadas</th>
          <th>Programadas</th>
          <th>% Utilización</th>
          <th>% Cancelaciones</th>
          <th>Desviación</th>
          <th>Estado</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Generado desde <code>scripts/run_doctor_utilization.py</code>
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
