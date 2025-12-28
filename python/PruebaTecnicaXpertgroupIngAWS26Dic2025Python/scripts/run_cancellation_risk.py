"""Script para el caso 5.2: modelo heurístico de probabilidad de cancelación."""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.core.services import CancellationRiskService

DATASET = ROOT / "dataset_hospital 2 AWS.json"
REPORT_DIR = ROOT / "reports"
LOG_JSON = REPORT_DIR / "cancellation_risk_log.json"
SUMMARY_HTML = REPORT_DIR / "cancellation_risk_summary.html"


def main() -> None:
    repo = JsonAppointmentRepository(DATASET)
    report = CancellationRiskService(repo).analyze()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_HTML.write_text(build_html(report), encoding="utf-8")

    print("🧠 Caso 5.2: Probabilidad de cancelación por recordatorio prioritario")
    print(f"✅ JSON generado en: {LOG_JSON.resolve()}")
    print(f"📈 Reporte HTML disponible en: {SUMMARY_HTML.resolve()}")
    print(f"📊 Grupos con riesgo crítico: {report.high_risk_count}")


def build_html(report) -> str:
    entries = report.entries
    chart_labels = json.dumps([entry.id_cita for entry in entries[:10]])
    chart_values = json.dumps([round(entry.risk_score, 3) for entry in entries[:10]])

    risk_rows = "\n".join(
        "<tr>"
        f"<td>{entry.id_cita}</td>"
        f"<td>{entry.id_paciente or 'N/A'}</td>"
        f"<td>{entry.especialidad}</td>"
        f"<td>{entry.estado_cita or 'Sin estado'}</td>"
        f"<td>{entry.days_since_last or 'nd'}</td>"
        f"<td>{', '.join(entry.factors)}</td>"
        f"<td>{round(entry.risk_score,3)}</td>"
        "</tr>"
        for entry in entries
    ) or "<tr><td colspan='7' style='text-align:center;'>No hay registros analizados</td></tr>"

    specialty_list = "\n".join(
        f"<li><strong>{name.title()}:</strong> {round(score,3)}</li>"
        for name, score in report.specialty_risk.items()
    ) or "<li>No hay especialidades registradas.</li>"

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
  pre { background: #f6f8fa; padding: 14px; border-radius: 8px; overflow: auto; font-size: 0.92em; }
  code { font-family: Consolas, 'Courier New', monospace; }
  .row { display:flex; gap:20px; flex-wrap:wrap; }
  .col { flex:1 1 420px; }
  .endpoint { border: 1px solid #e0e0e0; padding: 12px 14px; border-radius: 8px; background: #fff; box-shadow: 0 3px 8px rgba(0,0,0,0.04); }
  canvas { width: 100%; height: auto; margin-top: 20px; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: center; }
  th { background: #dbeafe; }
  .row-list { list-style: none; margin-left: 0; padding-left: 0; }
  .row-list li { margin-bottom: 4px; }
  """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte cancelaciones 5.2</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Probabilidad de cancelación (5.2)</h1>
    <p class="note">Usamos estados previos, especialidad y tiempos entre citas para detectar riesgos y priorizar recordatorios.</p>
    <div class="row">
      <div class="col endpoint">
        <h2>Resumen</h2>
        <table class="params">
          <tr><th>Total analizados</th><td>{report.total_records}</td></tr>
          <tr><th>Riesgo medio</th><td>{round(report.average_risk, 3)}</td></tr>
          <tr><th>Alertas críticas</th><td>{report.high_risk_count}</td></tr>
        </table>
      </div>
      <div class="col endpoint">
        <h2>Riesgo por especialidad</h2>
        <ul class="row-list">
          {specialty_list}
        </ul>
      </div>
    </div>
    <canvas id="riskChart"></canvas>
    <h2>Top riesgos</h2>
    <div class="note">
      <p>Los valores indican la distancia al umbral crítico de recordatorios.</p>
    </div>
    <table>
      <thead>
        <tr>
          <th>id_cita</th>
          <th>id_paciente</th>
          <th>Especialidad</th>
          <th>Estado</th>
          <th>Días desde anterior</th>
          <th>Factores</th>
          <th>Score</th>
        </tr>
      </thead>
      <tbody>
        {risk_rows}
      </tbody>
    </table>
    <div class="footer">
      Reporte generado desde <code>scripts/run_cancellation_risk.py</code>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const labels = {chart_labels};
    const data = {chart_values};
    const ctx = document.getElementById('riskChart').getContext('2d');
    new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels,
        datasets: [{{
          label: 'Score de riesgo',
          data,
          backgroundColor: '#ef4444',
          borderRadius: 5,
        }}],
      }},
      options: {{
        responsive: true,
        scales: {{
          y: {{
            beginAtZero: true,
            max: 1,
            ticks: {{ stepSize: 0.1 }}
          }}
        }},
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{ callbacks: {{ label: item => 'Riesgo: ' + item.raw }} }}
        }},
      }},
    }});
  </script>
</body>
</html>"""


if __name__ == "__main__":
    main()
