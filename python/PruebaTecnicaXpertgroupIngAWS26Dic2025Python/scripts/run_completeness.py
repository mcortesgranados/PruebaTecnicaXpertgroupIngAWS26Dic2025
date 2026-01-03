"""
Script principal para ejecutar el caso de uso 1.1.
Utiliza `sys` for runtime path wiring; `pathlib.Path` for cross-platform filesystem paths; imputer adapters to enrich missing values before analysis; ingestion adapters to isolate data-loading concerns; persistence adapters to emit audit logs or metrics; core services implement business rules while respecting Dependency Inversion.
Este modulo sigue SOLID: Single Responsibility keeps orchestration focused, Open/Closed lets new services plug in, y Dependency Inversion depends on abstractions instead of concrete implementations.
"""




import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.adapters.imputers.city_category_imputer import CityCategoryImputer
from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.adapters.persistence.completeness_reporter import JsonCompletenessReporter
from src.core.services import CompletenessService


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    dataset_path = Path("dataset_hospital 2 AWS.json")
    reporter_path = Path("reports/completeness_metrics.json")

    repository = JsonPatientRepository(dataset_path)
    imputer = CityCategoryImputer()
    service = CompletenessService(repository, imputer)

    metrics, plans = service.evaluate()

    reporter = JsonCompletenessReporter(reporter_path)
    reporter.export_metrics(metrics)

    print("Caso de uso 1.1: completitud de email, telefono y ciudad")
    for metric in metrics:
        print(
            f"- {metric.field}: {metric.missing}/{metric.total} missing "
            f"({round(metric.completeness * 100, 2)}% completitud)"
        )

    print("\nSugerencias de imputación:")
    for plan in plans:
        print(f"- {plan.field}: {plan.strategy}")

    html_path = Path("reports/completeness_summary.html")
    html_path.parent.mkdir(exist_ok=True, parents=True)
    html_path.write_text(build_html(metrics, plans), encoding="utf-8")

    print(f"\nReporte HTML generado en: {html_path}")


def build_html(metrics, plans):
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

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
  .json { white-space: pre; font-family: Consolas, 'Courier New', monospace; font-size: 0.95em; }
  .success { color: #2e7d32; font-weight: 600; }
  .error { color: #c62828; font-weight: 600; }"""

    metrics_html = "\n".join(
        f"<li><strong>{metric.field}</strong>: {metric.missing}/{metric.total} missing "
        f"({round(metric.completeness * 100, 2)}% completitud)</li>"
        for metric in metrics
    )
    plans_html = "\n".join(f"<li><strong>{plan.field}</strong>: {plan.strategy}</li>" for plan in plans)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Reporte de completitud 1.1</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Caso de uso 1.1 — Completitud de campos críticos</h1>
    <p>Salida generada desde <code>scripts/run_completeness.py</code>.</p>
    <div class="note">
      <p>Resumen de completitud</p>
      <ul>
        {metrics_html}
      </ul>
    </div>
    <div class="note">
      <p>Sugerencias de imputación</p>
      <ul>
        {plans_html}
      </ul>
    </div>
    <div class="footer">
      Reporte generado automáticamente.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
