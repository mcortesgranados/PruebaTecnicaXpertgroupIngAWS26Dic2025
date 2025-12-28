"""Script para caso 5.4: escenarios de demanda futura y brechas de capacidad."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.core.services import DemandForecastService

DATASET = ROOT / "dataset_hospital 2 AWS.json"
REPORT_DIR = ROOT / "reports"
LOG_JSON = REPORT_DIR / "demand_forecast_log.json"
SUMMARY_HTML = REPORT_DIR / "demand_forecast_summary.html"


def main() -> None:
    repo = JsonAppointmentRepository(DATASET)
    report = DemandForecastService(repo).forecast()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_HTML.write_text(build_html(report), encoding="utf-8")

    print("📈 Caso 5.4: Proyección de demanda y brechas de capacidad médicas")
    print(f"✅ JSON generado en: {LOG_JSON.resolve()}")
    print(f"🧾 HTML generado en: {SUMMARY_HTML.resolve()}")
    print(f"🔍 Meses proyectados: {report.future_months}")


def build_html(report) -> str:
    entries = report.entries[:12]
    month_labels = json.dumps(report.future_months)
    predicted_series = json.dumps(
        [sum(entry.predicted_demand for entry in report.entries if entry.month == month) for month in report.future_months]
    )
    capacity_series = json.dumps(
        [sum(entry.capacity for entry in report.entries if entry.month == month) for month in report.future_months]
    )

    rows = "\n".join(
        "<tr>"
        f"<td>{entry.month}</td>"
        f"<td>{entry.doctor}</td>"
        f"<td>{entry.specialty}</td>"
        f"<td>{entry.predicted_demand}</td>"
        f"<td>{entry.capacity}</td>"
        f"<td>{entry.gap}</td>"
        "</tr>"
        for entry in entries
    ) or "<tr><td colspan='6' style='text-align:center;'>Sin proyecciones disponibles</td></tr>"

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
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: center; }
  th { background: #dbeafe; }
  canvas { width: 100%; height: auto; margin-top: 20px; }
  .row { display:flex; gap:20px; flex-wrap:wrap; }
  .col { flex:1 1 420px; }
  .endpoint { border: 1px solid #e0e0e0; padding: 12px 14px; border-radius: 8px; background: #fff; box-shadow: 0 3px 8px rgba(0,0,0,0.04); }
  .highlight { font-weight: 600; }
  """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Proyección demanda 5.4</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Proyección de demanda futura</h1>
    <p class="note">Aplicamos el crecimiento mensual promedio para estimar los próximos {report.months_ahead} meses y calcular brechas de capacidad por médico.</p>
    <div class="row">
      <div class="col endpoint">
        <h2>Indicadores</h2>
        <p><span class="highlight">Crecimiento mensual medio:</span> {round(report.avg_monthly_growth, 2)}</p>
        <p><span class="highlight">Capacidad total proyectada:</span> {report.total_capacity}</p>
      </div>
      <div class="col endpoint">
        <h2>Meses proyectados</h2>
        <ul class="note">
          {''.join(f'<li>{month}</li>' for month in report.future_months)}
        </ul>
      </div>
    </div>
    <canvas id="trendChart"></canvas>
    <h2>Top brechas por médico</h2>
    <table>
      <thead>
        <tr>
          <th>Mes</th>
          <th>Médico</th>
          <th>Especialidad</th>
          <th>Demanda proyectada</th>
          <th>Capacidad</th>
          <th>Brecha</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      Reporte generado desde <code>scripts/run_demand_forecast.py</code>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const labels = {month_labels};
    const predicted = {predicted_series};
    const capacity = {capacity_series};
    const ctx = document.getElementById('trendChart').getContext('2d');
    new Chart(ctx, {{
      type: 'line',
      data: {{
        labels,
        datasets: [
          {{
            label: 'Demanda proyectada',
            data: predicted,
            borderColor: '#2563eb',
            fill: false,
            tension: 0.3,
          }},
          {{
            label: 'Capacidad',
            data: capacity,
            borderColor: '#16a34a',
            fill: false,
            tension: 0.3,
          }},
        ],
      }},
      options: {{
        responsive: true,
        scales: {{
          y: {{
            beginAtZero: true,
          }}
        }},
      }},
    }});
  </script>
</body>
</html>"""


if __name__ == "__main__":
    main()
