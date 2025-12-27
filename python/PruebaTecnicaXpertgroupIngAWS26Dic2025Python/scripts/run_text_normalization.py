"""Script principal para ejecutar el caso de uso 1.4."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.core.services import TextNormalizationService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_LOG = Path("reports/text_normalization_log.json")
DEFAULT_HTML_REPORT = Path("reports/text_normalization_summary.html")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta la normalización de texto en el dataset.")
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=DEFAULT_DATASET,
        help="Ruta al JSON con la tabla de pacientes.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG,
        help="Archivo JSON donde se registran los cambios de texto.",
    )
    parser.add_argument(
        "--html-report",
        type=Path,
        default=DEFAULT_HTML_REPORT,
        help="Reporte HTML con el resumen de la normalización.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    repository = JsonPatientRepository(args.dataset_path)
    service = TextNormalizationService(repository)
    report = service.normalize()

    args.log_path.parent.mkdir(parents=True, exist_ok=True)
    args.log_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    log_path_resolved = args.log_path.resolve()

    args.html_report.parent.mkdir(parents=True, exist_ok=True)
    args.html_report.write_text(build_html_report(report), encoding="utf-8")
    html_path_resolved = args.html_report.resolve()

    print("🌱 Manuela · Spring Boot Normalization Console")
    print("🌀 Caso de uso 1.4: Normalización de campos de texto")
    print(f"📋 - Registros procesados: {report.total_records}")
    print(f"✏️ - Cambios en nombre: {report.normalized_fields.get('nombre', 0)}")
    print(f"🏙️ - Cambios en ciudad: {report.normalized_fields.get('ciudad', 0)}")
    print(
        f"🔎 strip() + lower() + remove_tildes documentados en: {log_path_resolved}"
    )
    print(f"🌐 Reporte HTML completo en: {html_path_resolved}")


def build_html_report(report: "TextNormalizationReport") -> str:
    entries = report.log_entries[:20]
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.id_paciente}</td>"
        f"<td>{entry.field}</td>"
        f"<td>{entry.original_value or '—'}</td>"
        f"<td>{entry.normalized_value or '—'}</td>"
        f"<td>{entry.method}</td>"
        "</tr>"
        for entry in entries
    )
    if not rows:
        rows = "<tr><td colspan='5' style='text-align:center;'>No se normalizaron campos</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte caso de uso 1.4</title>
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
  /* Code block styling */
  pre {{ background: #f6f8fa; padding: 14px; border-radius: 8px; overflow: auto; font-size: 0.92em; }}
  code {{ font-family: Consolas, 'Courier New', monospace; }}
  .row {{ display:flex; gap:20px; flex-wrap:wrap; }}
  .col {{ flex:1 1 420px; }}
  /* Small visual helpers */
  .endpoint {{ border: 1px solid #e0e0e0; padding: 12px 14px; border-radius: 8px; background: #fff; box-shadow: 0 3px 8px rgba(0,0,0,0.04); }}
  .json {{ white-space: pre; font-family: Consolas, 'Courier New', monospace; font-size: 0.95em; }}
  .success {{ color: #2e7d32; font-weight: 600; }}
  .error {{ color: #c62828; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Caso de uso 1.4 – Normalización de texto</h1>
    <div class="row">
      <div class="col">
        <h3>Resumen</h3>
        <div class="note">
          <p>Se aplicaron strip() + lower() + remove_tildes para limpiar <strong>nombre</strong> y <strong>ciudad</strong>. Los primeros {len(entries)} cambios se muestran abajo; el JSON guarda todos los detalles.</p>
        </div>
      </div>
      <div class="col">
        <h3>Totales</h3>
        <dl class="params">
          <dt>Total registros</dt>
          <dd>{report.total_records}</dd>
          <dt>Nombre normalizado</dt>
          <dd>{report.normalized_fields.get('nombre', 0)}</dd>
          <dt>Ciudad normalizada</dt>
          <dd>{report.normalized_fields.get('ciudad', 0)}</dd>
        </dl>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th>id_paciente</th>
          <th>campo</th>
          <th>valor original</th>
          <th>valor normalizado</th>
          <th>método</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    <div class="footer">
      <span class="tag">strip()</span>
      <span class="tag">lower()</span>
      <span class="tag">remove_tildes</span>
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
