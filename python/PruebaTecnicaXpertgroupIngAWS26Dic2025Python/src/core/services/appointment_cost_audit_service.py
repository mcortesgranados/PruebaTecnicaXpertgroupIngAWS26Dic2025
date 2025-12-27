"""Servicio que analiza la distribución de costos por especialidad."""

from __future__ import annotations

from collections import defaultdict
from statistics import mean, stdev
from typing import Dict, List

from ..models import (
    CostAuditReport,
    CostAnomalyEntry,
    SpecialtyCostSummary,
)
from ..ports import AppointmentRepository


class AppointmentCostAuditService:
    def __init__(self, repository: AppointmentRepository):
        self.repository = repository

    def analyze(self) -> CostAuditReport:
        records = list(self.repository.list_appointments())
        total_records = len(records)
        specialty_costs: Dict[str, List[float]] = defaultdict(list)
        processed_costs: List[tuple] = []

        for record in records:
            costo = record.costo
            if costo is None:
                continue
            specialty = self._normalize_specialty(record.especialidad)
            specialty_costs[specialty].append(costo)
            processed_costs.append((record, specialty))

        summaries = []
        summary_map: Dict[str, SpecialtyCostSummary] = {}

        for specialty, costs in specialty_costs.items():
            avg = mean(costs)
            deviation = stdev(costs) if len(costs) > 1 else 0.0
            summary = SpecialtyCostSummary(
                especialidad=specialty,
                count=len(costs),
                average=avg,
                std_dev=deviation,
            )
            summaries.append(summary)
            summary_map[specialty] = summary

        anomalies = []
        threshold_multiplier = 2
        for record, specialty in processed_costs:
            costs = specialty_costs[specialty]
            if len(costs) <= 1:
                continue
            others = list(costs)
            others.remove(record.costo)
            if not others:
                continue
            avg = mean(others)
            deviation_value = stdev(others) if len(others) > 1 else 0.0
            if deviation_value <= 0:
                continue
            diff = abs(record.costo - avg)
            if diff > threshold_multiplier * deviation_value:
                anomalies.append(
                    CostAnomalyEntry(
                        id_cita=record.id_cita,
                        id_paciente=record.id_paciente,
                        especialidad=specialty,
                        costo=record.costo,
                        deviation=diff,
                    )
                )

        summaries.sort(key=lambda s: s.especialidad)
        anomalies.sort(key=lambda a: -a.deviation)

        return CostAuditReport(
            total_records=total_records,
            analyzed_records=len(processed_costs),
            summaries=summaries,
            anomalies=anomalies,
        )

    @staticmethod
    def _normalize_specialty(value: str | None) -> str:
        if value and isinstance(value, str) and value.strip():
            return value.strip()
        return "sin_especialidad"
