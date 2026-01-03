"""
Script para el caso 7.3: detectar viajes entre ciudades residencia vs. cita.
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
from src.core.services import PatientTravelService

DATASET = ROOT / "dataset_hospital 2 AWS.json"
REPORT_DIR = ROOT / "reports"
LOG_JSON = REPORT_DIR / "patient_travel_log.json"
SUMMARY_HTML = REPORT_DIR / "patient_travel_summary.html"


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    service = PatientTravelService(JsonPatientRepository(DATASET), JsonAppointmentRepository(DATASET))
    report = service.analyze()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_HTML.write_text(build_html(report), encoding="utf-8")

    print("🧭 Caso 7.3: pacientes viajando entre ciudades para telemedicina")
    print(f"✅ JSON adicional en: {LOG_JSON.resolve()}")
    print(f"📰 HTML adicional en: {SUMMARY_HTML.resolve()}")
    print(f"👣 Pacientes viajando detectados: {report.total_travelers}")


def build_html(report) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    rows = "\n".join(
        "<tr>"
        f"<td>{entry.nombre}</td>"
        f"<td>{entry.residence}</td>"
        f"<td>{', '.join(entry.travel_cities)}</td>"
        f"<td>{entry.travel_count}</td>"
        f"<td>{entry.severity.title()}</td>"
        f"<td>{', '.join(entry.last_travel_dates)}</td>"
        "</tr>"
        for entry in report.entries
    ) or "<tr><td colspan='6' style='text-align:center;'>No se detectaron traslados entre ciudades.</td></tr>"

    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 980px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.08); padding: 32px 40px; }
  h1 { color: #0f172a; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: left; }
  th { background: #d1fae5; }
  .note { background: #dcfce7; border-left: 4px solid #22c55e; padding: 16px; border-radius: 6px; }
  .footer { margin-top: 24px; text-align: right; color: #555; }
  """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Detección de viajes 7.3</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Pacientes viajando entre ciudades</h1>
    <p class="note">Identificamos pacientes cuya residencia difiere de la ciudad de la cita, lo que sugiere telemedicina o brigadas móviles.</p>
    <p><strong>Total detectados:</strong> {report.total_travelers}</p>
    <table>
      <thead>
        <tr>
          <th>Paciente</th>
          <th>Residencia</th>
          <th>Ciudades visitadas</th>
          <th>Conteo ciudades</th>
          <th>Severidad</th>
          <th>Fechas</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Generado desde <code>scripts/run_patient_travel.py</code>
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
