"""
Modulo encargado de completitud servicio.
Utiliza anotaciones diferidas para referencias de tipo; `collections` para contadores y agrupaciones; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List, Tuple

from ..models import CompletenessMetric, ImputationPlan, PatientRecord
from ..ports import ImputationStrategy, PatientRepository


class CompletenessService:
    """
    Representa completitud servicio y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    FIELDS_TO_CHECK = ("email", "telefono", "ciudad")

    def __init__(self, repository: PatientRepository, imputer: ImputationStrategy):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.repository = repository
        self.imputer = imputer

    def evaluate(self) -> Tuple[List[CompletenessMetric], List[ImputationPlan]]:
        """
        Encapsula evaluate, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        records = list(self.repository.list_patients())
        metrics = [self._metric_for_field(records, field) for field in self.FIELDS_TO_CHECK]
        plan = self.imputer.suggest(records)
        return metrics, plan

    def _metric_for_field(self, records: Iterable[PatientRecord], field: str) -> CompletenessMetric:
        """
        Encapsula metric for field, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        total = 0
        missing = 0
        per_city = defaultdict(lambda: [0, 0])
        per_category = defaultdict(lambda: [0, 0])

        for record in records:
            total += 1
            value = getattr(record, field)
            city = record.ciudad or "sin_ciudad"
            category = record.categoria.value
            per_city[city][0] += 1
            per_category[category][0] += 1
            if not value:
                missing += 1
                per_city[city][1] += 1
                per_category[category][1] += 1

        return CompletenessMetric(
            field=field,
            total=total,
            missing=missing,
            completeness=max(0.0, 1 - missing / total) if total else 0,
            per_city_missing={
                city: round(missed / total_city * 100, 2)
                for city, (total_city, missed) in per_city.items()
                if total_city
            },
            per_category_missing={
                category: round(missed / total_category * 100, 2)
                for category, (total_category, missed) in per_category.items()
                if total_category
            },
        )
