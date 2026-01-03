"""
Script para documentar reglas de negocio clave (caso 4.2).
Utiliza `json` for serializing reports and logs; `sys` for runtime path wiring; `pathlib.Path` for cross-platform filesystem paths; core services implement business rules while respecting Dependency Inversion.
Este modulo sigue SOLID: Single Responsibility keeps orchestration focused, Open/Closed lets new services plug in, y Dependency Inversion depends on abstractions instead of concrete implementations.
"""




import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.core.services import BusinessRulesCatalogService


DEFAULT_JSON = Path("reports/business_rules_catalog.json")
DEFAULT_HTML = Path("reports/business_rules_catalog.html")


def main() -> None:
    """
    Coordinates data ingestion adapters, the appropriate domain service, and
    reporting steps so the orchestrator maintains a single responsibility
    while remaining open to new services and depending on abstractions
    (Dependency Inversion).
    """

    service = BusinessRulesCatalogService()
    catalog = service.define_catalog()

    DEFAULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON.write_text(json.dumps(catalog.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    DEFAULT_HTML.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_HTML.write_text(build_html(catalog), encoding="utf-8")

    print("📚 Caso 4.2: Catálogo de reglas de negocio")
    print(f"📂 JSON catalogado en: {DEFAULT_JSON.resolve()}")
    print(f"🌐 HTML disponible en: {DEFAULT_HTML.resolve()}")


def build_html(catalog) -> str:
    """
    Composes the HTML summary string, keeping presentation logic isolated
    and easy to extend (Single Responsibility).
    """

    rows = "\n".join(
        "<div class=\"rule\">"
        f"<h3>{rule.title}</h3>"
        f"<p>{rule.description}</p>"
        f"<pre>{json.dumps(rule.details, ensure_ascii=False, indent=2)}</pre>"
        "</div>"
        for rule in catalog.rules
    )
    style = """  body { font-family: 'Segoe UI', Arial, sans-serif; background: #fafbfc; color: #23272f; margin: 0; padding: 0; }
  .container { max-width: 900px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 12px 30px rgba(0,0,0,0.1); padding: 32px 40px; }
  h1 { color: #1565c0; }
  .rule { background: #f1f5f9; border-left: 4px solid #2563eb; padding: 16px; margin-bottom: 18px; border-radius: 8px; }
  pre { background: #fff; border: 1px solid #e5e7eb; padding: 12px; border-radius: 6px; overflow: auto; }
  </style>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Catálogo de reglas de negocio 4.2</title>
  <style>
{style}
  </style>
</head>
<body>
  <div class="container">
    <h1>Catálogo de reglas de negocio</h1>
    <p>Documentamos los estados válidos, rangos de edad por especialidad y formatos esperados.</p>
    {rows}
  </div>
</body>
</html>"""


if __name__ == "__main__":
    main()
