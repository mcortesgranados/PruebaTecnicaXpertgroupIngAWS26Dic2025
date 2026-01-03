"""
Script del caso de uso 2.3: auditoría de costos por especialidad.
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
from src.core.services import AppointmentCostAuditService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_JSON = Path("reports/appointment_cost_audit_log.json")
DEFAULT_HTML = Path("reports/appointment_cost_audit_summary.html")


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    repository = JsonAppointmentRepository(DEFAULT_DATASET)
    service = AppointmentCostAuditService(repository)
    report = service.analyze()

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html_report(report), encoding="utf-8")

    print("💰 Caso de uso 2.3: Auditoría de costos por especialidad")
    print(f"📌 Registros procesados: {report.total_records}")
    print(f"🧮 Registros con costo válido: {report.analyzed_records}")
    print(f"⚖️ Anomalías detectadas (>2σ): {len(report.anomalies)}")
    print(f"📂 JSON completo: {DEFAULT_JSON.resolve()}")
    print(f"🌐 Reporte HTML detallado: {DEFAULT_HTML.resolve()}")


def build_html_report(report) -> str:
    """
    Composes the HTML summary/report string, keeping presentation logic
    separate from business logic (Single Responsibility).
    """

    summary_rows = "\n".join(
        "<tr>"
        f"<td>{summary.especialidad}</td>"
        f"<td>{summary.count}</td>"
        f"<td>{summary.average:.2f}</td>"
        f"<td>{summary.std_dev:.2f}</td>"
        f"<td>{summary.expected_min:.2f}</td>"
        f"<td>{summary.expected_max:.2f}</td>"
        "</tr>"
        for summary in report.summaries
    )
    if not summary_rows:
        summary_rows = "<tr><td colspan='6' style='text-align:center;'>Sin datos de costos</td></tr>"

    anomalies_rows = "\n".join(
        "<tr>"
        f"<td>{anomaly.id_cita}</td>"
        f"<td>{anomaly.especialidad}</td>"
        f"<td>{anomaly.costo or '—'}</td>"
        f"<td>{anomaly.deviation:.2f}</td>"
        f"<td>{anomaly.id_paciente or '—'}</td>"
        "<td>Desviación > 2σ</td>"
        "</tr>"
        for anomaly in report.anomalies[:40]
    )
    if not anomalies_rows:
        anomalies_rows = "<tr><td colspan='6' style='text-align:center;'>No se detectaron anomalías</td></tr>"

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
  <title>Reporte caso de uso 2.3</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Auditoría de costos por especialidad (2.3)</h1>
    <div class="note">
      <p>Se compara cada costo con el rango esperado (±2 desviaciones estándar). Los registros que exceden el rango se anotan para auditoría.</p>
    </div>

    <h2>Resumen</h2>
    <div class="row">
      <div class="col endpoint">
        <strong>Total registros</strong>
        <p>{report.total_records}</p>
      </div>
      <div class="col endpoint">
        <strong>Costos analizados</strong>
        <p>{report.analyzed_records}</p>
      </div>
      <div class="col endpoint">
        <strong>Anomalías</strong>
        <p>{len(report.anomalies)}</p>
      </div>
    </div>

    <h2>Resumen por especialidad</h2>
    <table>
      <thead>
        <tr>
          <th>Especialidad</th>
          <th>Registros</th>
          <th>Promedio</th>
          <th>Desviación</th>
          <th>Rango esperado</th>
        </tr>
      </thead>
      <tbody>
        {summary_rows}
      </tbody>
    </table>

    <h2>Anomalías registradas</h2>
    <p class="note">Se listan las 40 primeras desviaciones detectadas, ordenadas por magnitud.</p>
    <table>
      <thead>
        <tr>
          <th>id_cita</th>
          <th>Especialidad</th>
          <th>Costo</th>
          <th>Desviación</th>
          <th>id_paciente</th>
          <th>Nota</th>
        </tr>
      </thead>
      <tbody>
        {anomalies_rows}
      </tbody>
    </table>

    <div class="footer">
      Reporte generado desde <code>scripts/run_appointment_cost_audit.py</code>.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
