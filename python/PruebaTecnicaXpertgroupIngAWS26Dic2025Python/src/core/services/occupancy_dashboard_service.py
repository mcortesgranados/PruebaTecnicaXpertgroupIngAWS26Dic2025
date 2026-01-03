"""
Servicio que resume ocupación por ciudad y especialidad.
Utiliza anotaciones diferidas para referencias de tipo; `collections` para contadores y agrupaciones; `datetime` para calculos y validaciones de fechas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Tuple

from ..models import CitySpecialtyOccupancy, OccupancyDashboardReport
from ..ports import AppointmentRepository, PatientRepository


class OccupancyDashboardService:
    """
    Representa ocupacion tablero servicio y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    COMPLETED = {"completada", "completed"}
    CANCELED = {"cancelada", "cancelled", "canceled"}
    REPROGRAMMED = {"reprogramada", "reprogramado", "reprogramadas"}

    def __init__(self, patient_repo: PatientRepository, appointment_repo: AppointmentRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.patient_repo = patient_repo
        self.appointment_repo = appointment_repo

    def summarize(self) -> OccupancyDashboardReport:
        """
        Encapsula summarize, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        city_by_patient = {
            patient.id_paciente: self._normalize_city(patient.ciudad)
            for patient in self.patient_repo.list_patients()
        }
        counts: Dict[Tuple[str, str], Dict[str, int]] = defaultdict(
            lambda: {"completed": 0, "canceled": 0, "reprogrammed": 0}
        )
        total = 0

        for appointment in self.appointment_repo.list_appointments():
            status = self._normalize_status(appointment.estado_cita)
            if not status:
                continue
            city = city_by_patient.get(appointment.id_paciente, "Sin ciudad")
            specialty = self._normalize_specialty(appointment.especialidad)
            bucket = counts[(city, specialty)]
            bucket[status] += 1
            total += 1

        entries = [
            CitySpecialtyOccupancy(
                city=city,
                specialty=specialty,
                completed=bucket["completed"],
                canceled=bucket["canceled"],
                reprogrammed=bucket["reprogrammed"],
            )
            for (city, specialty), bucket in counts.items()
            if sum(bucket.values()) > 0
        ]

        sorted_entries = sorted(entries, key=lambda entry: entry.total, reverse=True)

        return OccupancyDashboardReport(
            generated_at=datetime.utcnow().isoformat(),
            total_appointments=total,
            entries=sorted_entries,
        )

    @classmethod
    def _normalize_status(cls, status: str | None) -> str | None:
        """
        Encapsula normalize status, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        if not status:
            return None
        sanitized = status.strip().lower()
        if sanitized in cls.COMPLETED:
            return "completed"
        if sanitized in cls.CANCELED:
            return "canceled"
        if sanitized in cls.REPROGRAMMED:
            return "reprogrammed"
        return None

    @staticmethod
    def _normalize_city(city: str | None) -> str:
        """
        Encapsula normalize ciudad, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        if not city:
            return "Sin ciudad"
        cleaned = city.strip()
        return cleaned or "Sin ciudad"

    @staticmethod
    def _normalize_specialty(especialidad: str | None) -> str:
        """
        Encapsula normalize specialty, manteniendo Single Responsibility y
        dejando el contrato abierto para nuevas versiones (Open/Closed) mientras
        depende de abstracciones (Dependency Inversion).
        """

        if not especialidad:
            return "General"
        cleaned = especialidad.strip()
        return cleaned.title() if cleaned else "General"
