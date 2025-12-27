"""Servicio para revisar citas completadas/canceladas que carecen de datos críticos."""

from __future__ import annotations

from typing import Iterable, List

from ..models import AppointmentRecord, AppointmentReviewEntry, AppointmentReviewReport
from ..ports import AppointmentRepository


class AppointmentReviewService:
    TARGET_STATES = {"Completada", "Cancelada"}

    def __init__(self, repository: AppointmentRepository):
        self.repository = repository

    def review(self) -> AppointmentReviewReport:
        records = list(self.repository.list_appointments())
        entries: List[AppointmentReviewEntry] = []

        for record in records:
            estado = (record.estado_cita or "").strip()
            if estado not in self.TARGET_STATES:
                continue

            issues = self._collect_issues(record)
            if not issues:
                continue

            entries.append(
                AppointmentReviewEntry(
                    id_cita=record.id_cita,
                    estado_cita=estado,
                    fecha_cita=record.fecha_cita,
                    medico=record.medico,
                    issues=issues,
                )
            )

        return AppointmentReviewReport(
            total_citas=len(records),
            reviewed_citas=len(entries),
            entries=entries,
        )

    def _collect_issues(self, record: AppointmentRecord) -> List[str]:
        issues = []
        if not record.fecha_cita or not record.fecha_cita.strip():
            issues.append("fecha_cita inválida o ausente")
        if not record.medico or not record.medico.strip():
            issues.append("médico no asignado")
        return issues
