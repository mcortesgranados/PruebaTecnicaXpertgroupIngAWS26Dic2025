"""
Script principal para ejecutar el caso de uso 1.2.
Utiliza `argparse` for parsing CLI options; `json` for serializing reports and logs; `sys` for runtime path wiring; `datetime` for cutoff or event dates; `pathlib.Path` for cross-platform filesystem paths; ingestion adapters to isolate data-loading concerns; core services implement business rules while respecting Dependency Inversion.
Este modulo sigue SOLID: Single Responsibility keeps orchestration focused, Open/Closed lets new services plug in, y Dependency Inversion depends on abstractions instead of concrete implementations.
"""




import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.core.services import AgeConsistencyService


DEFAULT_CUTOFF = date(2025, 12, 31)
DEFAULT_LOG = Path("reports/age_consistency_log.json")
DEFAULT_HTML_REPORT = Path("reports/age_consistency_summary.html")


def build_parser() -> argparse.ArgumentParser:
    """
    Builds the argparse parser so CLI parsing stays isolated (Single
    Responsibility) and open for future options.
    """

    parser = argparse.ArgumentParser(description="Ejecuta el caso de uso 1.2 sobre el dataset hospitalario.")
    parser.add_argument(
        "--cutoff-date",
        type=_parse_cutoff_date,
        default=DEFAULT_CUTOFF.isoformat(),
        help="Fecha de corte ISO (yyyy-mm-dd) usada para calcular las edades.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=DEFAULT_LOG,
        help="Ruta donde se guardará el log de cambios generado.",
    )
    parser.add_argument(
        "--html-report",
        type=Path,
        default=DEFAULT_HTML_REPORT,
        help="Ruta donde se generará el reporte HTML de resumen.",
    )
    return parser


def _parse_cutoff_date(value: str) -> date:
    """
    Parses ISO 8601 cutoff dates, keeping validation isolated for callers to
    rely on accurate date objects (Single Responsibility).
    """

    try:
        return datetime.fromisoformat(value).date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Fecha inválida ({value}). Use AAAA-MM-DD.") from exc


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    parser = build_parser()
    args = parser.parse_args()

    dataset_path = Path("dataset_hospital 2 AWS.json")
    repository = JsonPatientRepository(dataset_path)
    service = AgeConsistencyService(repository)
    report = service.audit_ages(args.cutoff_date)

    args.log_path.parent.mkdir(parents=True, exist_ok=True)
    args.log_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    args.html_report.parent.mkdir(parents=True, exist_ok=True)
    args.html_report.write_text(
        build_html_report(report), encoding="utf-8"
    )

    _print_summary(report, args.log_path, args.html_report)


def _print_summary(
    report: "AgeConsistencyReport", log_path: Path, html_path: Path
) -> None:
    """
    Prints the report summary to the console to keep CLI output separate
    from business rules (Single Responsibility).
    """

    print("Caso de uso 1.2: detección de inconsistencias entre edad y fecha de nacimiento")
    print(f"- Registros procesados: {report.total_records}")
    print(f"- Inconsistencias detectadas: {report.inconsistencies}")
    print(f"- Edades imputadas: {report.imputations}")
    print(f"- Registros sin fecha válida: {report.missing_birthdate_records}")
    print(f"\nLog de cambios escrito en: {log_path}")
    print(f"Reporte HTML generado en: {html_path}")


def build_html_report(report: "AgeConsistencyReport") -> str:
    """
    Composes the HTML summary/report string, keeping presentation logic
    separate from business logic (Single Responsibility).
    """

    entries = report.log_entries[:20]
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.id_paciente}</td>"
        f"<td>{entry.nombre}</td>"
        f"<td>{entry.action}</td>"
        f"<td>{entry.edad_registrada or '—'}</td>"
        f"<td>{entry.edad_calculada if entry.edad_calculada is not None else '—'}</td>"
        f"<td>{entry.note}</td>"
        "</tr>"
        for entry in entries
    )
    if not rows:
        rows = "<tr><td colspan='6' style='text-align:center;'>No hay registros en el log</td></tr>"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Resumen caso de uso 1.2</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#f8fafc; color:#1f2933; margin:0; padding:20px; }}
    .container {{ max-width:1100px; margin:0 auto; background:#fff; border-radius:10px; box-shadow:0 12px 24px rgba(15,23,42,0.15); padding:32px; }}
    h1 {{ color:#1d4ed8; }}
    table {{ width:100%; border-collapse:collapse; margin-top:24px; font-size:0.95rem; }}
    th, td {{ border:1px solid #e5e7eb; padding:10px; text-align:left; }}
    th {{ background:#e0f2fe; color:#0369a1; }}
    .summary {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(200px,1fr)); gap:16px; margin-top:16px; }}
    .card {{ background:#f1f5f9; border-radius:8px; padding:16px; }}
    .card span {{ display:block; font-size:1.5rem; font-weight:600; }}
    .note {{ margin-top:24px; font-size:0.9rem; color:#555; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Caso de uso 1.2 – Consistencia edad vs fecha de nacimiento</h1>
    <p>Fecha de corte utilizada: {report.cutoff_date.isoformat()}</p>
    <div class="summary">
      <div class="card">
        <p>Total procesados</p>
        <span>{report.total_records}</span>
      </div>
      <div class="card">
        <p>Inconsistencias</p>
        <span>{report.inconsistencies}</span>
      </div>
      <div class="card">
        <p>Edades imputadas</p>
        <span>{report.imputations}</span>
      </div>
      <div class="card">
        <p>Sin fecha válida</p>
        <span>{report.missing_birthdate_records}</span>
      </div>
    </div>
    <p class="note">
      Se muestran los primeros {len(entries)} registros con acciones detectadas; revise el JSON si requiere el historial completo.
    </p>
    <table>
      <thead>
        <tr>
          <th>id_paciente</th>
          <th>nombre</th>
          <th>acción</th>
          <th>edad registrada</th>
          <th>edad calculada</th>
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
