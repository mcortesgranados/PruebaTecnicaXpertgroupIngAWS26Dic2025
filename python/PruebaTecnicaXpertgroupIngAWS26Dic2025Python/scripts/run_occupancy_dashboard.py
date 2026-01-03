"""
Script para caso 5.3: dashboards de ocupación por ciudad y especialidad.
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
from src.core.services import OccupancyDashboardService

DATASET = ROOT / "dataset_hospital 2 AWS.json"
REPORT_DIR = ROOT / "reports"
LOG_JSON = REPORT_DIR / "occupancy_dashboard_log.json"
SUMMARY_HTML = REPORT_DIR / "occupancy_dashboard_summary.html"


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    patient_repo = JsonPatientRepository(DATASET)
    appointment_repo = JsonAppointmentRepository(DATASET)
    service = OccupancyDashboardService(patient_repo, appointment_repo)
    report = service.summarize()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_HTML.write_text(build_html(report), encoding="utf-8")

    print("📊 Caso 5.3: Dashboard de ocupación por ciudad y especialidad")
    print(f"✅ JSON generado en: {LOG_JSON.resolve()}")
    print(f"🖥️ HTML generado en: {SUMMARY_HTML.resolve()}")
    print(f"💡 Top combos ciudad/especialidad: {len(report.entries)}")


def build_html(report) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    entries = report.entries[:10]
    label_status = ["Completadas", "Canceladas", "Reprogramadas"]
    status_totals = {
        "completed": sum(entry.completed for entry in report.entries),
        "canceled": sum(entry.canceled for entry in report.entries),
        "reprogrammed": sum(entry.reprogrammed for entry in report.entries),
    }
    chart_labels = json.dumps(label_status)
    chart_values = json.dumps([status_totals["completed"], status_totals["canceled"], status_totals["reprogrammed"]])
    chart_colors = json.dumps(["#16a34a", "#dc2626", "#c084fc"])

    rows = "\n".join(
        "<tr>"
        f"<td>{entry.city}</td>"
        f"<td>{entry.specialty}</td>"
        f"<td>{entry.completed}</td>"
        f"<td>{entry.canceled}</td>"
        f"<td>{entry.reprogrammed}</td>"
        f"<td>{entry.total}</td>"
        f"<td>{round(entry.completion_rate*100,1)}%</td>"
        "</tr>"
        for entry in entries
    ) or "<tr><td colspan='7' style='text-align:center;'>No hay datos para mostrar.</td></tr>"

    generated_at = report.generated_at or __import__("datetime").datetime.utcnow().isoformat()
    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #1565c0; }
  h2 { color: #2e7d32; margin-top: 32px; }
  h3 { color: #7b1fa2; margin-top: 24px; }
  .note { background: #e3f2fd; border-left: 4px solid #1976d2; padding: 16px 20px; margin: 18px 0; border-radius: 7px; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: center; }
  th { background: #dbeafe; }
  .footer { text-align: right; color: #888; font-size: 1em; margin-top: 40px; }
  canvas { width: 100%; height: auto; margin-top: 20px; }
  .row { display:flex; gap:20px; flex-wrap:wrap; }
  .col { flex:1 1 420px; }
  .endpoint { border: 1px solid #e0e0e0; padding: 12px 14px; border-radius: 8px; background: #fff; box-shadow: 0 3px 8px rgba(0,0,0,0.04); }
  .tag { background: #e3f2fd; color: #1565c0; border-radius: 4px; padding: 3px 8px; margin-left: 6px; font-size: 0.95em; }
  .row-list { list-style: none; margin-left: 0; padding-left: 0; }
  .row-list li { margin-bottom: 6px; }
  .highlight { font-weight: 600; color: #0f172a; }
  """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard de ocupación 5.3</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Ocupación por ciudad y especialidad</h1>
    <p class="note">Comparamos citas completadas frente a canceladas y reprogramadas para priorizar agenda y recordatorios.</p>
    <div class="row">
      <div class="col endpoint">
        <h2>Resumen global</h2>
        <p><strong>Total citas analizadas:</strong> {report.total_appointments}</p>
        <p><strong>Generado en:</strong> {generated_at}</p>
        <ul class="row-list">
          <li><span class="highlight">Completadas:</span> {status_totals["completed"]}</li>
          <li><span class="highlight">Canceladas:</span> {status_totals["canceled"]}</li>
          <li><span class="highlight">Reprogramadas:</span> {status_totals["reprogrammed"]}</li>
        </ul>
      </div>
      <div class="col endpoint">
        <h2>Distribución</h2>
        <canvas id="statusChart"></canvas>
      </div>
    </div>
    <h2>Top combinaciones ciudad/especialidad</h2>
    <table>
      <thead>
        <tr>
          <th>Ciudad</th>
          <th>Especialidad</th>
          <th>Completadas</th>
          <th>Canceladas</th>
          <th>Reprogramadas</th>
          <th>Total</th>
          <th>%Completadas</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Script: <code>scripts/run_occupancy_dashboard.py</code>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const labels = {chart_labels};
    const data = {chart_values};
    const colors = {chart_colors};
    const ctx = document.getElementById('statusChart').getContext('2d');
    new Chart(ctx, {{
      type: 'pie',
      data: {{
        labels,
        datasets: [{{
          data,
          backgroundColor: colors,
        }}],
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ position: 'bottom' }},
        }},
      }},
    }});
  </script>
</body>
</html>"""


if __name__ == "__main__":
    main()
