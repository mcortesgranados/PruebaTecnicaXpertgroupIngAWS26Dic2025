"""
Script para alertar médicos sobre patrones críticos (caso 7.4).
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
from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.core.services import DoctorNotificationService

DATASET = ROOT / "dataset_hospital 2 AWS.json"
REPORT_DIR = ROOT / "reports"
LOG_JSON = REPORT_DIR / "doctor_notifications_log.json"
SUMMARY_HTML = REPORT_DIR / "doctor_notifications_summary.html"


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    patient_repo = JsonPatientRepository(DATASET)
    appointment_repo = JsonAppointmentRepository(DATASET)
    service = DoctorNotificationService(patient_repo, appointment_repo)
    report = service.analyze()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_HTML.write_text(build_html(report), encoding="utf-8")

    print("⚠️ Caso 7.4: Alertas médicas por patrón sospechoso de pacientes")
    print(f"📦 JSON disponible en: {LOG_JSON.resolve()}")
    print(f"📝 HTML disponible en: {SUMMARY_HTML.resolve()}")
    print(f"🔔 Alertas generadas: {report.total_alerts}")


def build_html(report) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    rows = "\n".join(
        "<tr>"
        f"<td>{entry.doctor}</td>"
        f"<td>{entry.nombre}</td>"
        f"<td>{entry.id_paciente}</td>"
        f"<td>{', '.join(entry.patterns)}</td>"
        f"<td>{entry.severity.title()}</td>"
        f"<td>{', '.join(date for date in entry.appointment_dates if date)}</td>"
        "</tr>"
        for entry in report.entries
    ) or "<tr><td colspan='6' style='text-align:center;'>No se detectaron alertas</td></tr>"

    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 980px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #b91c1c; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: left; }
  th { background: #fee2e2; }
  .note { background: #fef2f2; border-left: 4px solid #ef4444; padding: 16px; margin-top: 18px; border-radius: 8px; }
  .footer { margin-top: 24px; text-align: right; color: #888; }
  """
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Alertas médicas 7.4</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Alertas médicas por patrones de pacientes</h1>
    <p class="note">Se notifican médicos cuyos pacientes acumulan citas en periodos cortos o cancelaciones recurrentes para reforzar recordatorios.</p>
    <p><strong>Total alertas:</strong> {report.total_alerts}</p>
    <table>
      <thead>
        <tr>
          <th>Doctor</th>
          <th>Paciente</th>
          <th>ID paciente</th>
          <th>Patrones</th>
          <th>Severidad</th>
          <th>Fechas</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Generado desde <code>scripts/run_doctor_notifications.py</code>
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
