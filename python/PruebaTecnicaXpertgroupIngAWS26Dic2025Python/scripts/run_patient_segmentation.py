"""Script para el caso 5.5: segmentación de pacientes para comunicaciones personalizadas."""

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.core.services import PatientSegmentationService


REPORT_DIR = ROOT / "reports"
DATASET_PATH = ROOT / "dataset_hospital 2 AWS.json"
DEFAULT_JSON = REPORT_DIR / "patient_segmentation_log.json"
DEFAULT_HTML = REPORT_DIR / "patient_segmentation_summary.html"


def main() -> None:
    patient_repo = JsonPatientRepository(DATASET_PATH)
    appointment_repo = JsonAppointmentRepository(DATASET_PATH)
    service = PatientSegmentationService(patient_repo, appointment_repo)
    report = service.segment()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    DEFAULT_HTML.write_text(build_html(report), encoding="utf-8")

    print("🎯 Caso 5.5: Segmentación de pacientes para comunicaciones personalizadas")
    print(f"✅ JSON generado en: {DEFAULT_JSON.resolve()}")
    print(f"📊 Reporte HTML disponible en: {DEFAULT_HTML.resolve()}")
    print(f"📬 Segmentos clasificados: {len(report.cohorts)} combinaciones (edad/sexo/frecuencia).")


def build_html(report) -> str:
    entries = report.cohorts
    chart_entries = entries[:6]
    chart_labels = json.dumps(
        [f"{entry.age_segment} · {entry.sexo} · {entry.frequency_bucket}" for entry in chart_entries]
    )
    chart_values = json.dumps([entry.count for entry in chart_entries])

    frequency_counter = Counter(entry.frequency_bucket for entry in entries)
    sexo_counter = Counter(entry.sexo for entry in entries)
    age_counter = Counter(entry.age_segment for entry in entries)

    frequency_list = "\n".join(
        f"<li><strong>{label}:</strong> {count} pacientes</li>"
        for label, count in frequency_counter.items()
    ) or "<li>No hay pacientes segmentados.</li>"

    sexo_list = "\n".join(
        f"<li><strong>{label}:</strong> {count} combinaciones</li>"
        for label, count in sexo_counter.items()
    ) or "<li>Sin información de sexo.</li>"

    age_list = "\n".join(
        f"<li><strong>{label}:</strong> {count} segmentos</li>"
        for label, count in age_counter.items()
    ) or "<li>Sin datos de edad.</li>"

    top_cards = "\n".join(
        "<div class=\"col endpoint\">"
        f"<h3>{entry.age_segment}</h3>"
        f"<p><strong>Sexo:</strong> {entry.sexo}</p>"
        f"<p><strong>Frecuencia:</strong> {entry.frequency_bucket}</p>"
        f"<p><strong>Pacientes:</strong> {entry.count}</p>"
        "</div>"
        for entry in chart_entries
    )
    if not top_cards:
        top_cards = "<div class=\"col endpoint\"><p class=\"note\">No se identificaron segmentos todavía.</p></div>"

    generated_at = report.generated_at or datetime.utcnow().isoformat()
    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #1565c0; }
  h1, h2, h3 { margin-top: 0; }
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
  .json { white-space: pre; font-family: Consolas, 'Courier New', monospace; font-size: 0.95em; }
  .success { color: #2e7d32; font-weight: 600; }
  .error { color: #c62828; font-weight: 600; }
  canvas { width: 100%; height: auto; margin-top: 20px; }
  .note-grid { display: flex; gap: 16px; }
  .note-grid div { flex: 1; }
  .card-list { margin-top: 12px; }"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Segmentación pacientes 5.5</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Segmentación de pacientes</h1>
    <p class="note">Identificamos combinaciones de edad, sexo y frecuencia de citas para personalizar comunicaciones y programas de prevención.</p>
    <div class="row">
      <div class="col endpoint">
        <h2>Resumen</h2>
        <dl class="params">
          <dt>Generado el</dt>
          <dd>{generated_at}</dd>
          <dt>Total de pacientes segmentados</dt>
          <dd>{report.total_patients}</dd>
          <dt>Cohortes únicas</dt>
          <dd>{len(entries)}</dd>
        </dl>
      </div>
      <div class="col endpoint">
        <h2>Distribuciones clave</h2>
        <div class="note-grid">
          <div>
            <h3>Frecuencia</h3>
            <ul>{frequency_list}</ul>
          </div>
          <div>
            <h3>Sexo</h3>
            <ul>{sexo_list}</ul>
          </div>
          <div>
            <h3>Edad</h3>
            <ul>{age_list}</ul>
          </div>
        </div>
      </div>
    </div>
    <canvas id="segmentChart"></canvas>
    <h2>Cohortes destacadas</h2>
    <div class="row">
      {top_cards}
    </div>
    <div class="footer">
      Reporte generado desde <code>scripts/run_patient_segmentation.py</code>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const labels = {chart_labels};
    const data = {chart_values};
    const ctx = document.getElementById('segmentChart').getContext('2d');
    new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels,
        datasets: [{{
          label: 'Pacientes por cohorte',
          data,
          backgroundColor: '#2563eb',
          borderRadius: 6,
        }}],
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{ callbacks: {{ label: item => 'Pacientes: ' + item.raw }} }}
        }},
        scales: {{
          y: {{
            beginAtZero: true,
            ticks: {{ stepSize: 1 }}
          }}
        }},
      }},
    }});
  </script>
</body>
</html>"""


if __name__ == "__main__":
    main()
