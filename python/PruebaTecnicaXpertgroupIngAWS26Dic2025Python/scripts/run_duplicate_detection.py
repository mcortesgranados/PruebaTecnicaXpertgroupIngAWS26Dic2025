"""Script principal para ejecutar el caso de uso 1.3."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.core.services import DuplicateDetectionService


DEFAULT_DATASET = Path("dataset_hospital 2 AWS.json")
DEFAULT_LOG = Path("reports/duplicate_detection_log.json")
DEFAULT_HTML_REPORT = Path("reports/duplicate_detection_summary.html")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ejecuta el caso de uso 1.3 de duplicados.")
    parser.add_argument(
        "--dataset-path",
        type=Path,
        default=DEFAULT_DATASET,
        help="Ruta al JSON que contiene la tabla de pacientes.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG,
        help="Archivo JSON donde se documentará el dossier de duplicados.",
    )
    parser.add_argument(
        "--html-report",
        type=Path,
        default=DEFAULT_HTML_REPORT,
        help="Reporte HTML con resumen de los duplicados detectados.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    repository = JsonPatientRepository(args.dataset_path)
    service = DuplicateDetectionService(repository)
    report = service.detect_duplicates()

    args.log_path.parent.mkdir(parents=True, exist_ok=True)
    args.log_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    log_path_resolved = args.log_path.resolve()

    args.html_report.parent.mkdir(parents=True, exist_ok=True)
    args.html_report.write_text(build_html_report(report), encoding="utf-8")
    html_path_resolved = args.html_report.resolve()

    print("🧩 Caso de uso 1.3: Detección y consolidación de duplicados potenciales")
    print(f"📊 - Registros procesados: {report.total_records}")
    print(f"🧾 - Grupos detectados: {report.total_groups}")
    print(f"🗂️ - Registros archivados como duplicados: {report.total_duplicates}")
    print(f"📄 Log de duplicados disponible en: {log_path_resolved}")
    print(f"🌐 Reporte HTML generado en: {html_path_resolved}")


def build_html_report(report: "DuplicateConsolidationReport") -> str:
    entries = report.log_entries[:25]
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.canonical_id}</td>"
        f"<td>{entry.canonical_nombre}</td>"
        f"<td>{entry.criteria}</td>"
        f"<td>{', '.join(map(str, entry.duplicate_ids))}</td>"
        f"<td>{entry.note}</td>"
        "</tr>"
        for entry in entries
    )
    if not rows:
        rows = "<tr><td colspan='5' style='text-align:center;'>No se detectaron duplicados</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Caso de uso 1.3 – Reporte de duplicados</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f9fafc; color:#111827; margin:0; padding:20px; }}
    .container {{ max-width:1100px; margin:0 auto; padding:32px; background:#fff; border-radius:12px; box-shadow:0 20px 40px rgba(15,23,42,0.1); }}
    h1 {{ color:#2563eb; }}
    .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px; margin:24px 0; }}
    .card {{ background:#eff6ff; border-radius:10px; padding:16px; }}
    .card strong {{ display:block; font-size:1.1rem; color:#1d4ed8; }}
    table {{ width:100%; border-collapse:collapse; margin-top:18px; font-size:0.95rem; }}
    th, td {{ border:1px solid #e5e7eb; padding:10px; text-align:left; }}
    th {{ background:#dbeafe; color:#1d4ed8; }}
    .note {{ margin-top:18px; color:#374151; font-size:0.9rem; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Caso de uso 1.3 – Duplicados potenciales</h1>
    <div class="cards">
      <div class="card">
        <strong>Total registros</strong>
        <span>{report.total_records}</span>
      </div>
      <div class="card">
        <strong>Grupos detectados</strong>
        <span>{report.total_groups}</span>
      </div>
      <div class="card">
        <strong>Registros archivados</strong>
        <span>{report.total_duplicates}</span>
      </div>
    </div>
    <p class="note">Se muestran hasta {len(entries)} grupos con los ids duplicados y su registro canónico. Consulte el JSON si necesita todo el detalle.</p>
    <table>
      <thead>
        <tr>
          <th>canonical_id</th>
          <th>nombre</th>
          <th>criterio</th>
          <th>duplicate_ids</th>
          <th>nota</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
