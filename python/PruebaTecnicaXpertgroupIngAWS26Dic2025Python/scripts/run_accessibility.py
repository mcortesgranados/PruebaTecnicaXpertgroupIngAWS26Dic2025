"""Script para el caso de uso 3.4."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.core.services import AccessibilityService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_JSON = Path("reports/accessibility_log.json")
DEFAULT_HTML = Path("reports/accessibility_summary.html")


def main() -> None:
    patient_repo = JsonPatientRepository(DEFAULT_DATASET)
    appointment_repo = JsonAppointmentRepository(DEFAULT_DATASET)
    service = AccessibilityService(patient_repo, appointment_repo)
    report = service.evaluate()

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html(report), encoding="utf-8")

    print("🚶 Caso 3.4: Cruce de citas por ciudad de residencia")
    print(f"📌 Pacientes revisados: {report.total_pacientes}")
    print(f"⚠️ Pacientes con más citas de lo esperado: {report.flagged}")
    print(f"📂 JSON: {DEFAULT_JSON.resolve()}")
    print(f"🌐 Reporte HTML: {DEFAULT_HTML.resolve()}")


def build_html(report) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.id_paciente}</td>"
        f"<td>{entry.nombre}</td>"
        f"<td>{entry.residencia or '—'}</td>"
        f"<td>{entry.total_citas}</td>"
        f"<td>{entry.note}</td>"
        "</tr>"
        for entry in report.entries[:50]
    )
    if not rows:
        rows = "<tr><td colspan='5' style='text-align:center;'>Sin pacientes con viajes largos detectados</td></tr>"

    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #1565c0; }
  h2 { color: #2e7d32; margin-top: 32px; }
  table { width: 100%; border-collapse: collapse; margin-top: 18px; }
  th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: left; }
  th { background: #dbeafe; }
  .note { background: #e3f2fd; border-left: 4px solid #1976d2; padding: 16px 20px; margin: 18px 0; border-radius: 7px; }
  .footer { margin-top: 24px; text-align: right; color: #888; font-size: 0.9rem; }
  </style>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte caso 3.4</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Citas por paciente y localidad</h1>
    <div class="note">
      <p>Combinamos el número total de citas de cada paciente con su ciudad de residencia para detectar pacientes con un volumen elevado y potencialmente viajando largas distancias.</p>
    </div>
    <p><strong>Total de pacientes examinados:</strong> {report.total_pacientes}.</p>
    <table>
      <thead>
        <tr>
          <th>id_paciente</th>
          <th>nombre</th>
          <th>residencia</th>
          <th>total citas</th>
          <th>nota</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Reporte generado desde <code>scripts/run_accessibility.py</code>.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
