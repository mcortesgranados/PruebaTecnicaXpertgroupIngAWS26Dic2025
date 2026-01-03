"""
Script para caso 7.4: reportes ejecutivos con KPIs de espera y costo.
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
from src.core.services import ManagementKpiService

DATASET = ROOT / "dataset_hospital 2 AWS.json"
REPORT_DIR = ROOT / "reports"
LOG_JSON = REPORT_DIR / "management_kpis.json"
SUMMARY_HTML = REPORT_DIR / "management_kpis_summary.html"


def build_html(report) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    rows = "\n".join(
        "<tr>"
        f"<td>{entry.specialty}</td>"
        f"<td>{entry.appointment_count}</td>"
        f"<td>${entry.average_cost}</td>"
        f"<td>{entry.average_wait_days} días</td>"
        "</tr>"
        for entry in report.specialty_entries
    ) or "<tr><td colspan='4' style='text-align:center;'>Sin datos</td></tr>"

    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 980px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.08); padding: 32px 40px; }
  h1 { color: #0f172a; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: center; }
  th { background: #e0e7ff; }
  .note { background: #e0f2fe; border-left: 4px solid #0ea5e9; padding: 16px; border-radius: 6px; }
  .footer { margin-top: 24px; text-align: right; color: #555; }
  """
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KPIs gerenciales 7.4</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>KPIs gerenciales: espera y costo por cita</h1>
    <p class="note">Presentamos costos promedio y tiempos de espera para monitorear cumplimiento ejecutivo.</p>
    <p><strong>Espera promedio total:</strong> {round(report.overall_average_wait_days, 2)} días</p>
    <p><strong>Costo promedio total:</strong> ${round(report.overall_average_cost, 2)}</p>
    <table>
      <thead>
        <tr>
          <th>Especialidad</th>
          <th>Conteo citas completadas</th>
          <th>Costo promedio</th>
          <th>Espera promedio (días)</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Generado desde <code>scripts/run_management_kpis.py</code>
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

    service = ManagementKpiService(JsonAppointmentRepository(DATASET))
    report = service.report()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_HTML.write_text(build_html(report), encoding="utf-8")

    print("📊 Caso 7.4: KPIs gerenciales de espera y costo por cita")
    print(f"✅ JSON generado en: {LOG_JSON.resolve()}")
    print(f"📰 HTML generado en: {SUMMARY_HTML.resolve()}")
    print(f"🧮 Espera promedio: {round(report.overall_average_wait_days,2)} días; Costo promedio: ${round(report.overall_average_cost,2)}")


if __name__ == "__main__":
    main()
