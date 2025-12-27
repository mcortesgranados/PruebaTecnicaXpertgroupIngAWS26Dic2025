from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List

from ...core.models import ImputationPlan, PatientCategory, PatientRecord
from ...core.ports import ImputationStrategy


class CityCategoryImputer(ImputationStrategy):
    MISSING_THRESHOLD = 0.15

    def suggest(self, records: Iterable[PatientRecord]) -> List[ImputationPlan]:
        records = list(records)
        field_stats = {field: self._compute_ratios(records, field) for field in ("email", "telefono", "ciudad")}
        return [
            self._plan_for_email(field_stats["email"]),
            self._plan_for_phone(field_stats["telefono"]),
            self._plan_for_city(field_stats["ciudad"], records),
        ]

    def _compute_ratios(self, records: List[PatientRecord], field: str):
        stats = defaultdict(lambda: [0, 0])
        for record in records:
            city = record.ciudad or "sin_ciudad"
            stats[city][0] += 1
            value = getattr(record, field)
            if not value:
                stats[city][1] += 1
        return {
            city: (total, missed, missed / total if total else 0)
            for city, (total, missed) in stats.items()
        }

    def _plan_for_email(self, stats) -> ImputationPlan:
        candidates = sorted(stats.items(), key=lambda item: item[1][2], reverse=True)
        city, (_, _, ratio) = candidates[0]
        strategy = (
            f"Para ciudades con más del {int(self.MISSING_THRESHOLD*100)}% de emails faltantes "
            f"(ej.: {city} con {round(ratio*100,2)}%), "
            "imputar usando plantilla <ciudad>.contacto@hospital.local y derivar alertas para validación humana."
        )
        rationale = (
            "La mayoría de pacientes comparte ciudad, así que el valor interpolado mantiene contexto geográfico "
            "sin inventar datos personales."
        )
        return ImputationPlan(field="email", strategy=strategy, rationale=rationale)

    def _plan_for_phone(self, stats) -> ImputationPlan:
        candidates = sorted(stats.items(), key=lambda item: item[1][2], reverse=True)
        city, (_, _, ratio) = candidates[0]
        strategy = (
            f"Para ciudad con más de {int(self.MISSING_THRESHOLD*100)}% de teléfonos faltantes (ej.: {city}), "
            "llenar con prefijos locales conocidos y número genérico +000 y marcar para revisión."
        )
        rationale = (
            "Los prefijos locales permiten al equipo operacional identificar rápidamente la zona y confirmar el dato."
        )
        return ImputationPlan(field="telefono", strategy=strategy, rationale=rationale)

    def _plan_for_city(self, stats, records: List[PatientRecord]) -> ImputationPlan:
        category_missing = defaultdict(lambda: [0, 0])
        for record in records:
            category_missing[record.categoria][0] += 1
            if not record.ciudad:
                category_missing[record.categoria][1] += 1

        top_category = max(category_missing.items(), key=lambda item: item[1][1]/item[1][0] if item[1][0] else 0)[0]
        strategy = (
            f"Para pacientes en {top_category.value} con ciudad vacía, imputar la última ciudad conocida del historial "
            "o asignar una ciudad firme (por ejemplo, 'Bogotá' como ciudad responsable) y documentar la suposición."
        )
        rationale = (
            "Las ciudades son clave para segmentación y gobernanza; elegir una ciudad base por categoría permite mantener comparabilidad."
        )
        return ImputationPlan(field="ciudad", strategy=strategy, rationale=rationale)
