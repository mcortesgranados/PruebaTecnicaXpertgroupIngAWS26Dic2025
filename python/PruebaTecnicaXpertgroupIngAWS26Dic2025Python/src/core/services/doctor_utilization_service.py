"""
Servicio para monitorear compliance de agenda por médico y especialidad.
Utiliza anotaciones diferidas para referencias de tipo; `collections` para contadores y agrupaciones; `datetime` para calculos y validaciones de fechas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Tuple

from ..models import DoctorUtilizationEntry, DoctorUtilizationReport
from ..ports import AppointmentRepository


class DoctorUtilizationService:
    """
    Representa medico utilizacion servicio y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    UTILIZATION_THRESHOLD = 0.75
    CANCELLATION_THRESHOLD = 0.2

    def __init__(self, appointment_repo: AppointmentRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.appointment_repo = appointment_repo

    def analyze(self) -> DoctorUtilizationReport:
        """
        Encapsula analyze, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        counts: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(
            lambda: {"completed": 0, "cancelled": 0, "reprogrammed": 0, "scheduled": 0}
        )

        for appointment in self.appointment_repo.list_appointments():
            doctor = (appointment.medico or "Sin médico").strip().title()
            specialty = (appointment.especialidad or "General").strip().title()
            key = (doctor, specialty)
            counts[key]["scheduled"] += 1
            status = (appointment.estado_cita or "").strip().lower()
            if status == "completada":
                counts[key]["completed"] += 1
            elif status == "cancelada":
                counts[key]["cancelled"] += 1
            elif status == "reprogramada":
                counts[key]["reprogrammed"] += 1

        entries = []
        for (doctor, specialty), metrics in counts.items():
            scheduled = metrics["scheduled"]
            if scheduled == 0:
                continue
            completed = metrics["completed"]
            canceled = metrics["cancelled"]
            reprogrammed = metrics["reprogrammed"]

            utilization = completed / scheduled
            cancellation = (canceled + reprogrammed) / scheduled
            deviation = utilization - self.UTILIZATION_THRESHOLD

            status = "ok"
            if utilization < self.UTILIZATION_THRESHOLD:
                status = "low_utilization"
            if cancellation > self.CANCELLATION_THRESHOLD:
                status = "high_cancellations"

            if utilization < self.UTILIZATION_THRESHOLD or cancellation > self.CANCELLATION_THRESHOLD:
                entries.append(
                    DoctorUtilizationEntry(
                        doctor=doctor,
                        specialty=specialty,
                        completed=completed,
                        scheduled=scheduled,
                        utilization_rate=utilization,
                        cancellation_rate=cancellation,
                        deviation=deviation,
                        status=status,
                    )
                )

        entries.sort(key=lambda e: e.deviation)
        return DoctorUtilizationReport(
            generated_at=datetime.utcnow().isoformat(),
            threshold=self.UTILIZATION_THRESHOLD,
            cancellation_threshold=self.CANCELLATION_THRESHOLD,
            entries=entries,
        )
