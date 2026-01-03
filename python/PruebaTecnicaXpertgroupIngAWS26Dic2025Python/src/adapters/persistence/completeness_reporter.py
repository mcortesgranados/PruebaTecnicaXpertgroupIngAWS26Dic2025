"""
Modulo encargado de completitud reportero.
Utiliza `json` para serializar y deserializar cargas JSON; `pathlib.Path` para manejar rutas multiplataforma; `typing` para contratos explicitos; modelos del dominio ubicados en `src.core.models`; puertos que definen interfaces para el nucleo del negocio.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""

import json
from pathlib import Path
from typing import List

from ...core.models import CompletenessMetric
from ...core.ports import CompletenessReporter


class JsonCompletenessReporter(CompletenessReporter):
    """
    Representa JSON completitud reportero y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    def __init__(self, target: Path):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.target = target

    def export_metrics(self, metrics: List[CompletenessMetric]) -> None:
        """
        Encapsula export metrics, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        payload = []
        for metric in metrics:
            payload.append(
                {
                    "field": metric.field,
                    "total": metric.total,
                    "missing": metric.missing,
                    "completeness_percentage": round(metric.completeness * 100, 2),
                    "per_city_missing": metric.per_city_missing,
                    "per_category_missing": metric.per_category_missing,
                }
            )
        with self.target.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
