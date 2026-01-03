"""
Script principal para medir indicadores diarios/semanales de citas (caso de uso 2.1).
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
from src.core.services import AppointmentIndicatorService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_LOG = Path("reports/appointment_indicators_log.json")
DEFAULT_HTML_REPORT = Path("reports/appointment_indicators_summary.html")


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    repository = JsonAppointmentRepository(DEFAULT_DATASET)
    service = AppointmentIndicatorService(repository)
    report = service.measure_indicators()

    DEFAULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_LOG.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML_REPORT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML_REPORT.write_text(build_html_report(report), encoding="utf-8")

    print("🧮 Caso de uso 2.1: Indicadores de citas por especialidad/estado/médico")
    print(f"📆 Registros procesados: {report.total_records}")
    print(f"❗ Registros sin fecha: {report.missing_date}")
    print(f"📈 Entradas registradas: {len(report.entries)}")
    print(f"🌐 JSON completo: {DEFAULT_LOG.resolve()}")
    print(f"📝 Reporte HTML: {DEFAULT_HTML_REPORT.resolve()}")


def build_html_report(report) -> str:
    """
    Composes the HTML summary/report string, keeping presentation logic
    separate from business logic (Single Responsibility).
    """

    entries = report.entries[:30]
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.period_type}</td>"
        f"<td>{entry.period_value}</td>"
        f"<td>{entry.especialidad}</td>"
        f"<td>{entry.estado_cita}</td>"
        f"<td>{entry.medico}</td>"
        f"<td>{entry.count}</td>"
        "</tr>"
        for entry in entries
    )
    if not rows:
        rows = "<tr><td colspan='6' style='text-align:center;'>No hay datos para mostrar</td></tr>"

    bottlenecks = "\n".join(
        f"<li>{entry.period_type} {entry.period_value} · {entry.especialidad} / {entry.estado_cita} / {entry.medico} ({entry.count} citas)</li>"
        for entry in report.bottlenecks
    ) or "<li>No se detectaron cuellos de botella.</li>"

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
  <title>Reporte caso de uso 2.1</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Indicadores de citas – Caso de uso 2.1</h1>
    <p>Detalle de los conteos diarios y semanales agrupados por especialidad, estado de cita y médico.</p>

    <div class="note">
      <p>Resumen de cuellos de botella:</p>
      <ul>
        {bottlenecks}
      </ul>
    </div>

    <div class="note">
      <p>Se registran {len(entries)} combinaciones. Consulte el JSON para el historial completo.</p>
    </div>

    <table>
      <thead>
        <tr>
          <th>periodo</th>
          <th>valor</th>
          <th>especialidad</th>
          <th>estado_cita</th>
          <th>médico</th>
          <th>conteo</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>

    <div class="footer">
      Reporte generado automáticamente desde <code>scripts/run_appointment_indicators.py</code>.
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
