"""Script para el caso 4.4: reportes ejecutivos y envío simulado a gobernanza."""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.core.services import ExecutiveDiscrepancyService


REPORT_DIR = ROOT / "reports"
DEFAULT_JSON = REPORT_DIR / "executive_discrepancies_log.json"
DEFAULT_HTML = REPORT_DIR / "executive_discrepancies_summary.html"


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    service = ExecutiveDiscrepancyService(REPORT_DIR)
    report = service.compile()

    DEFAULT_JSON.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    DEFAULT_HTML.write_text(build_html(report), encoding="utf-8")

    print("🧾 Caso 4.4: reportes ejecutivos de discrepancias y canal de gobernanza")
    print(f"✅ JSON generado en: {DEFAULT_JSON.resolve()}")
    print(f"📢 Reporte HTML disponible en: {DEFAULT_HTML.resolve()}")
    print(f"📡 Notificando a {service.CHANNEL} con el resumen de {len(report.entries)} discrepancias.")


def build_html(report) -> str:
    entries = report.entries
    chart_labels = json.dumps([entry.category for entry in entries])
    chart_values = json.dumps([entry.count for entry in entries])
    severity_colors = json.dumps(
        [
            _severity_to_color(entry.severity)
            for entry in entries
        ]
    )

    entry_cards = "\n".join(
        "<div class=\"col endpoint severity-card {severity}\">"
        f"<h3>{entry.category}</h3>"
        f"<p>{entry.description}</p>"
        f"<p><strong>Registros:</strong> {entry.count}</p>"
        f"<p><em>Fuente:</em> {entry.source}</p>"
        "</div>"
        for entry in entries
        for severity in [_normalize_severity(entry.severity)]
    )
    if not entry_cards:
        entry_cards = "<div class=\"col endpoint\"><p class=\"note\">No se detectaron discrepancias críticas en los últimos registros.</p></div>"

    source_list = (
        "\n".join(
            f"<li><strong>{entry.category}</strong> ({entry.source}): {entry.count} registros</li>"
            for entry in entries
        )
        or "<li>No se configuraron discrepancias para reportar.</li>"
    )

    generated_at = report.generated_at or datetime.utcnow().isoformat()
    color_note = (
        "<span class=\"success\">Alta</span>"
        " · "
        "<span class=\"tag\" style=\"color: #f9a826; border-color:#f9a826;\">Media</span>"
        " · "
        "<span class=\"tag\" style=\"color: #2e7d32; border-color:#2e7d32;\">Baja</span>"
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte ejecutivo 4.4</title>
  <style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }}
  .container {{ max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }}
  h1 {{ color: #1565c0; }}
  h2 {{ color: #2e7d32; margin-top: 32px; }}
  h3 {{ color: #7b1fa2; margin-top: 24px; }}
  .note {{ background: #e3f2fd; border-left: 4px solid #1976d2; padding: 16px 20px; margin: 18px 0; border-radius: 7px; }}
  .note ul {{ list-style: disc inside; margin: 0; padding-left: 1.2em; }}
  .note li {{ margin-bottom: 3px; line-height: 1.35; }}
  .note p {{ margin: 0 0 6px 0; line-height: 1.5; }}
  .footer {{ text-align: right; color: #888; font-size: 1em; margin-top: 40px; }}
  .tag {{ background: #e3f2fd; color: #1565c0; border-radius: 4px; padding: 3px 8px; margin-left: 6px; font-size: 0.95em; }}
  dt {{ color: #2e7d32; font-weight: bold; margin-top: 10px; }}
  dd {{ margin-bottom: 10px; }}
  .params table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
  .params th, .params td {{ border: 1px solid #ccc; padding: 6px; }}
  .important {{ background: #fffde7; border-left: 4px solid #fbc02d; padding: 12px 18px; margin: 18px 0; border-radius: 5px; }}
  .sideEffects ul, .solid ul {{ margin: 0; padding-left: 20px; }}
  @media (max-width: 600px) {{ .container {{ padding: 16px 8px; }} }}
  pre {{ background: #f6f8fa; padding: 14px; border-radius: 8px; overflow: auto; font-size: 0.92em; }}
  code {{ font-family: Consolas, 'Courier New', monospace; }}
  .row {{ display:flex; gap:20px; flex-wrap:wrap; }}
  .col {{ flex:1 1 420px; }}
  .endpoint {{ border: 1px solid #e0e0e0; padding: 12px 14px; border-radius: 8px; background: #fff; box-shadow: 0 3px 8px rgba(0,0,0,0.04); }}
  .json {{ white-space: pre; font-family: Consolas, 'Courier New', monospace; font-size: 0.95em; }}
  .success {{ color: #2e7d32; font-weight: 600; }}
  .error {{ color: #c62828; font-weight: 600; }}
  .severity-card {{ border-left: 6px solid transparent; padding-bottom: 18px; }}
  .severity-card.high {{ border-color: #c62828; }}
  .severity-card.medium {{ border-color: #f9a826; }}
  .severity-card.low {{ border-color: #2e7d32; }}
  canvas {{ width: 100%; height: auto; margin-top: 20px; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Reporte ejecutivo de discrepancias</h1>
    <p class="note">Consolidamos alertas críticas y las enviamos al canal <code>{report.channel}</code> antes de cualquier carga a producción.</p>
    <div class="row">
      <div class="col endpoint">
        <h2>Resumen ejecutivo</h2>
        <dl class="params">
          <dt>Fecha de generación</dt>
          <dd>{generated_at}</dd>
          <dt>Entradas con alertas</dt>
          <dd>{len(entries)}</dd>
          <dt>Canal de gobernanza</dt>
          <dd>{report.channel}</dd>
        </dl>
      </div>
      <div class="col endpoint">
        <h2>Severidades</h2>
        <p>{color_note}</p>
        <div class="important">
          <strong>Total registros críticos:</strong> {sum(entry.count for entry in entries)}
        </div>
      </div>
    </div>
    <canvas id="discrepancyChart"></canvas>
    <h2>Detalle de discrepancias</h2>
    <div class="row">
      {entry_cards}
    </div>
    <div class="note">
      <h3>Fuentes monitorizadas</h3>
      <ul>
        {source_list}
      </ul>
    </div>
    <div class="footer">
      Reporte generado desde <code>scripts/run_executive_discrepancy.py</code>
    </div>
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
    const labels = {chart_labels};
    const data = {chart_values};
    const palette = {severity_colors};
    const ctx = document.getElementById('discrepancyChart').getContext('2d');
    new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels,
        datasets: [{{
          label: 'Discrepancias',
          data,
          backgroundColor: palette,
          borderRadius: 8,
        }}],
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{ callbacks: {{ label: context => `Registros: ${{context.raw}}` }} }}
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


def _severity_to_color(severity: str) -> str:
    mapping = {
        "high": "#c62828",
        "medium": "#f9a826",
        "low": "#2e7d32",
    }
    return mapping.get(severity.lower(), "#5c6bc0")


def _normalize_severity(severity: str) -> str:
    return severity.lower() if severity else "low"


if __name__ == "__main__":
    main()
