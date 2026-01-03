"""
Script para ejecutar casos de uso 4.1 (KPIs de calidad).
Utiliza `json` for serializing reports and logs; `sys` for runtime path wiring; `pathlib.Path` for cross-platform filesystem paths; ingestion adapters to isolate data-loading concerns; core models define domain types separately from this script; core services implement business rules while respecting Dependency Inversion.
Este modulo sigue SOLID: Single Responsibility keeps orchestration focused, Open/Closed lets new services plug in, y Dependency Inversion depends on abstractions instead of concrete implementations.
"""




import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.core.models import FieldQualityMetric
from src.core.services import QualityKpiService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_JSON = Path("reports/quality_kpis.json")
DEFAULT_HTML = Path("reports/quality_kpis_summary.html")


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    patient_repo = JsonPatientRepository(DEFAULT_DATASET)
    appointment_repo = JsonAppointmentRepository(DEFAULT_DATASET)
    service = QualityKpiService(patient_repo, appointment_repo)
    report = service.compute()

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html(report), encoding="utf-8")

    print("📊 Caso 4.1: KPIs de calidad pre/post limpieza")
    print(f"📂 JSON de KPIs: {DEFAULT_JSON.resolve()}")
    print(f"🌐 Reporte HTML: {DEFAULT_HTML.resolve()}")


def build_html(report) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    table_sections = []
    chart_configs = []
    for table in report.tables:
        canvas_id = f"chart_{table.table_name}"
        labels = [metric.field for metric in table.before]
        before_completeness = [metric.completeness for metric in table.before]
        after_completeness = [metric.completeness for metric in table.after]
        table_sections.append(
            f"""
<h2>{table.table_name.replace('_',' ').title()}</h2>
<div class="note">
  <canvas id="{canvas_id}"></canvas>
</div>
<table>
  <thead>
    <tr>
      <th>Campo</th>
      <th>Completitud antes (%)</th>
      <th>Completitud después (%)</th>
      <th>Unicidad antes (%)</th>
      <th>Unicidad después (%)</th>
      <th>Validez antes (%)</th>
      <th>Validez después (%)</th>
    </tr>
  </thead>
  <tbody>
    {''.join(build_row(field_before, field_after) for field_before, field_after in zip(table.before, table.after))}
  </tbody>
</table>
"""
        )
        chart_configs.append(
            {
                "canvasId": canvas_id,
                "labels": labels,
                "before": before_completeness,
                "after": after_completeness,
                "title": table.table_name.replace("_", " ").title(),
            }
        )
    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #1565c0; }
  h2 { color: #2e7d32; margin-top: 32px; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 10px; text-align: left; }
  th { background: #dbeafe; }
  .note { background: #e3f2fd; border-left: 4px solid #1976d2; padding: 16px 20px; margin: 18px 0; border-radius: 7px; }
  .footer { text-align: right; color: #888; margin-top: 24px; }
  </style>"""
    script_data = json.dumps(chart_configs)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KPI Calidad 4.1</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>KPIs de calidad (completitud, unicidad y validez)</h1>
    <div class="note">
      <p>Se calcula la completitud, unicidad y validez de formatos por campo antes y después de aplicar las limpiezas. Los porcentajes están en base 100.</p>
    </div>
    {''.join(table_sections)}
    <div class="footer">
      Reporte generado desde <code>scripts/run_quality_kpis.py</code>.
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const chartData = {script_data};
    chartData.forEach(cfg => {{
      const ctx = document.getElementById(cfg.canvasId);
      if (!ctx) return;
      new Chart(ctx, {{
        type: "bar",
        data: {{
          labels: cfg.labels,
          datasets: [
            {{
              label: "Antes",
              backgroundColor: "#2563eb",
              data: cfg.before
            }},
            {{
              label: "Después",
              backgroundColor: "#16a34a",
              data: cfg.after
            }}
          ]
        }},
        options: {{
          responsive: true,
          plugins: {{
            legend: {{ position: "top" }},
            title: {{
              display: true,
              text: cfg.title
            }}
          }}
        }}
      }});
    }});
  </script>
</body>
</html>"""


def build_row(before: FieldQualityMetric, after: FieldQualityMetric) -> str:
    """
    Builds a single HTML table row for KPI entries, keeping row rendering
    separate from calculations (Single Responsibility).
    """

    return f"""
<tr>
  <td>{before.field}</td>
  <td>{before.completeness:.2f}</td>
  <td>{after.completeness:.2f}</td>
  <td>{before.uniqueness:.2f}</td>
  <td>{after.uniqueness:.2f}</td>
  <td>{before.format_valid:.2f}</td>
  <td>{after.format_valid:.2f}</td>
</tr>
"""


if __name__ == "__main__":
    main()
