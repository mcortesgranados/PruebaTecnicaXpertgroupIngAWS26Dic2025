"""
Script para caso 4.3: registrar responsables y auditoría de limpiezas.
Utiliza `json` for serializing reports and logs; `sys` for runtime path wiring; `pathlib.Path` for cross-platform filesystem paths; core models define domain types separately from this script; core services implement business rules while respecting Dependency Inversion.
Este modulo sigue SOLID: Single Responsibility keeps orchestration focused, Open/Closed lets new services plug in, y Dependency Inversion depends on abstractions instead of concrete implementations.
"""




import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.core.models import FieldResponsibility
from src.core.services import CleaningAuditService


DEFAULT_LOG = Path("reports/cleaning_audit_log.json")
DEFAULT_HTML = Path("reports/cleaning_audit_summary.html")


RESPONSIBILITIES = [
    FieldResponsibility(
        table="pacientes",
        field="email",
        owner="Data Ops",
        contact="dataops@hospital.local",
        notes="Responsable por validar correos antes de limpieza de contacts.",
    ),
    FieldResponsibility(
        table="pacientes",
        field="ciudad",
        owner="Equipo de Operaciones",
        contact="ops@hospital.local",
        notes="Mantiene catálogo de ciudades autorizadas.",
    ),
    FieldResponsibility(
        table="citas_medicas",
        field="fecha_cita",
        owner="Agenda",
        contact="agenda@hospital.local",
        notes="Valida fechas de agenda antes de confirmar.",
    ),
]


SAMPLE_CHANGES = [
    {
        "table": "pacientes",
        "field": "email",
        "action": "Imputación masiva",
        "user": "ana",
        "note": "Llenado con plantilla <ciudad>.contacto@hospital.local."
    },
    {
        "table": "pacientes",
        "field": "ciudad",
        "action": "Normalización",
        "user": "javier",
        "note": "Capitalización y estandarización de tildes."
    },
    {
        "table": "citas_medicas",
        "field": "fecha_cita",
        "action": "Validación",
        "user": "marcela",
        "note": "Se eliminaron registros sin fecha válida."
    },
]


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    service = CleaningAuditService(RESPONSIBILITIES)
    report = service.register_changes(SAMPLE_CHANGES)

    DEFAULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_LOG.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html(report, RESPONSIBILITIES), encoding="utf-8")

    print("🧾 Caso 4.3: Auditoría de responsables por campo")
    print(f"📌 Cambio registrados: {len(report.entries)}")
    print(f"📂 Log JSON en: {DEFAULT_LOG.resolve()}")
    print(f"🌐 Reporte HTML en: {DEFAULT_HTML.resolve()}")


def build_html(report, responsibilities) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    resp_map = {(r.table, r.field): r for r in responsibilities}
    rows = "\n".join(
        "<tr>"
        f"<td>{entry.table}</td>"
        f"<td>{entry.field}</td>"
        f"<td>{entry.owner}</td>"
        f"<td>{entry.contact}</td>"
        f"<td>{entry.action}</td>"
        f"<td>{entry.user}</td>"
        f"<td>{entry.timestamp}</td>"
        f"<td>{entry.note}</td>"
        "</tr>"
        for entry in report.entries
    )
    resp_rows = "\n".join(
        "<tr>"
        f"<td>{resp.table}</td>"
        f"<td>{resp.field}</td>"
        f"<td>{resp.owner}</td>"
        f"<td>{resp.contact}</td>"
        f"<td>{resp.notes or '—'}</td>"
        "</tr>"
        for resp in responsibilities
    )
    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 950px; margin: 40px auto; background: #fff; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border-radius: 10px; padding: 32px 40px; }
  h1 { color: #1565c0; }
  table { width: 100%; border-collapse: collapse; margin-top: 16px; }
  th, td { border: 1px solid #e5e7eb; padding: 8px; text-align: left; }
  th { background: #dbeafe; }
  .note { background: #fef9c3; border-left: 4px solid #f59e0b; padding: 12px; margin-top: 18px; }
  .footer { margin-top: 24px; text-align: right; color: #888; }
  </style>"""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Audit Trail 4.3</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Catálogo de responsables y auditoría</h1>
    <div class="note">
      <p>Responsables asignados y registros con timestamp + usuario para cada cambio masivo.</p>
    </div>
    <h2>Responsables por campo</h2>
    <table>
      <thead>
        <tr><th>Tabla</th><th>Campo</th><th>Owner</th><th>Contacto</th><th>Notas</th></tr>
      </thead>
      <tbody>
        {resp_rows}
      </tbody>
    </table>
    <h2>Registro de cambios</h2>
    <table>
      <thead>
        <tr><th>Tabla</th><th>Campo</th><th>Owner</th><th>Contacto</th><th>Acción</th><th>Usuario</th><th>Timestamp</th><th>Nota</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <div class="footer">
      Script: <code>scripts/run_cleaning_audit.py</code>
    </div>
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
