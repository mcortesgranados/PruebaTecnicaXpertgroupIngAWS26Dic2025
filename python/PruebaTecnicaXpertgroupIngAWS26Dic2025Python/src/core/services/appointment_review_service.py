"""
Servicio para revisar citas completadas/canceladas que carecen de datos críticos.
Utiliza anotaciones diferidas para referencias de tipo; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from typing import Iterable, List

from ..models import AppointmentRecord, AppointmentReviewEntry, AppointmentReviewReport
from ..ports import AppointmentRepository


class AppointmentReviewService:
    """
    Representa cita revision servicio y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    TARGET_STATES = {"Completada", "Cancelada"}

    def __init__(self, repository: AppointmentRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.repository = repository

    def review(self) -> AppointmentReviewReport:
        """
        Encapsula revision, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

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
        """
        Encapsula collect issues, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        issues = []
        if not record.fecha_cita or not record.fecha_cita.strip():
            issues.append("fecha_cita inválida o ausente")
        if not record.medico or not record.medico.strip():
            issues.append("médico no asignado")
        return issues
