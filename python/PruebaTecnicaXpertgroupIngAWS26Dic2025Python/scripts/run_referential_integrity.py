"""Script para el caso de uso 3.1: integridad referencial entre pacientes y citas."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.core.services import ReferentialIntegrityService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_JSON = Path("reports/referential_integrity_log.json")
DEFAULT_HTML = Path("reports/referential_integrity_summary.html")


def main() -> None:
    appointment_repo = JsonAppointmentRepository(DEFAULT_DATASET)
    patient_repo = JsonPatientRepository(DEFAULT_DATASET)
    service = ReferentialIntegrityService(appointment_repo, patient_repo)
    report = service.check()

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html_report(report), encoding="utf-8")

    print("🧾 Caso de uso 3.1: Integridad referencial de citas")
    print(f"📌 Registros de citas: {report.total_citas}")
    print(f"🕵️ Orphan records: {report.orphan_citas}")
    print(f"📁 JSON registrado en: {DEFAULT_JSON.resolve()}")
    print(f"🌐 Reporte HTML en: {DEFAULT_HTML.resolve()}")


def build_html_report(report) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.id_cita}</td>"
        f"<td>{entry.id_paciente or '—'}</td>"
        f"<td>{entry.motivo}</td>"
        "</tr>"
        for entry in report.entries[:50]
    )
    if not rows:
        rows = "<tr><td colspan='3' style='text-align:center;'>No se encontraron entradas huérfanas</td></tr>"

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
  <title>Reporte caso de uso 3.1</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Integridad referencial – Caso 3.1</h1>
    <div class="note">
      <p>Detectamos cada <code>id_cita</code> cuyo <code>id_paciente</code> no coincide con ningún paciente registrado y los dejamos para auditoría manual.</p>
    </div>
    <div class="note">
      <strong>Resumen:</strong>
      <ul>
        <li>Total de citas examinadas: {report.total_citas}</li>
        <li>Citas huérfanas registradas: {report.orphan_citas}</li>
      </ul>
    </div>
    <table>
      <thead>
        <tr>
          <th>id_cita</th>
          <th>id_paciente</th>
          <th>motivo</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Reporte generado desde <code>scripts/run_referential_integrity.py</code>.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
