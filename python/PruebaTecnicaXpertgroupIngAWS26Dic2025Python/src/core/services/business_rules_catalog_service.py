"""
Servicio que documenta reglas de negocio clave.
Utiliza anotaciones diferidas para referencias de tipo; `datetime` para calculos y validaciones de fechas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from ..models import BusinessRule, BusinessRulesCatalog


class BusinessRulesCatalogService:
    """
    Representa negocio reglas catalogo servicio y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    def define_catalog(self) -> BusinessRulesCatalog:
        """
        Encapsula define catalogo, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        rules = [
            BusinessRule(
                id="rule-estado",
                title="Estado válido de cita",
                description="Los estados permitidos deben ser Programada, Completada, Cancelada o Reprogramada.",
                details={
                    "valid_states": ["Programada", "Completada", "Cancelada", "Reprogramada"],
                    "source": "Catálogo de estados esperado por operaciones",
                },
            ),
            BusinessRule(
                id="rule-edad-especialidad",
                title="Rango de edades por especialidad",
                description="Pediatría <18 años, adultos 18-64 y geriatría >=65.",
                details={
                    "ranges": {
                        "Pediatría": {"min": 0, "max": 17},
                        "Geriatría": {"min": 65, "max": 120},
                        "General": {"min": 18, "max": 64},
                    }
                },
            ),
            BusinessRule(
                id="rule-email-format",
                title="Formato de correo electrónico",
                description="Debe contener '@' seguido de un dominio con punto.",
                details={"pattern": "^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$"},
            ),
            BusinessRule(
                id="rule-phone-format",
                title="Formato de teléfono",
                description="Teléfonos deben ser dígitos con guiones opcionales (ej.: 315-123-4567).",
                details={"example": "XXX-XXX-XXXX"},
            ),
        ]
        return BusinessRulesCatalog(
            created_at=datetime.utcnow().isoformat(),
            rules=rules,
        )
