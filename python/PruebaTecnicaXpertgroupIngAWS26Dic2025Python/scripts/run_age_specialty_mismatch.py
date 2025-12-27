"""Script para el caso de uso 3.3."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.core.services import AgeSpecialtyMismatchService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_JSON = Path("reports/age_specialty_mismatch_log.json")
DEFAULT_HTML = Path("reports/age_specialty_mismatch_summary.html")


def main() -> None:
    appointment_repo = JsonAppointmentRepository(DEFAULT_DATASET)
    patient_repo = JsonPatientRepository(DEFAULT_DATASET)
    service = AgeSpecialtyMismatchService(appointment_repo, patient_repo)
    report = service.analyze()

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html(report), encoding="utf-8")

    print("🧪 Caso 3.3: Edad vs especialidad")
    print(f"📌 Citas procesadas: {report.total_citas}")
    print(f"⚖️ Desvíos detectados: {report.flagged_citas}")
    print(f"📂 JSON completo: {DEFAULT_JSON.resolve()}")
    print(f"🌐 Reporte HTML detallado: {DEFAULT_HTML.resolve()}")


def build_html(report) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.id_cita}</td>"
        f"<td>{entry.id_paciente or '—'}</td>"
        f"<td>{entry.especialidad or '—'}</td>"
        f"<td>{entry.edad_calculada if entry.edad_calculada is not None else '—'}</td>"
        f"<td>{entry.expected_min if entry.expected_min is not None else '—'} - {entry.expected_max if entry.expected_max is not None else '—'}</td>"
        f"<td>{entry.note}</td>"
        "</tr>"
        for entry in report.entries[:40]
    )
    if not rows:
        rows = "<tr><td colspan='6' style='text-align:center;'>No se detectaron desvíos</td></tr>"

    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #1565c0; }
  h2 { color: #2e7d32; margin-top: 32px; }
  .note { background: #e3f2fd; border-left: 4px solid #1976d2; padding: 16px 20px; margin: 18px 0; border-radius: 7px; }
  .note ul { list-style: disc inside; margin: 0; padding-left: 1.2em; }
  .note li { margin-bottom: 3px; line-height: 1.35; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: left; }
  th { background: #dbeafe; }
  .footer { margin-top: 24px; text-align: right; color: #888; }
  </style>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte caso 3.3</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Comparación edad vs especialidad</h1>
    <div class="note">
      <p>Se comparó la edad calculada desde <code>fecha_nacimiento</code> con el rango esperado para cada especialidad (p.ej., pediatría <18, geriatría >65). Los desvíos salen a auditoría.</p>
    </div>
    <p><strong>Total descartes:</strong> {report.flagged_citas} de {report.total_citas} citas.</p>
    <table>
      <thead>
        <tr>
          <th>id_cita</th>
          <th>id_paciente</th>
          <th>especialidad</th>
          <th>edad calculada</th>
          <th>rango esperado</th>
          <th>nota</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Reporte generado desde <code>scripts/run_age_specialty_mismatch.py</code>.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
