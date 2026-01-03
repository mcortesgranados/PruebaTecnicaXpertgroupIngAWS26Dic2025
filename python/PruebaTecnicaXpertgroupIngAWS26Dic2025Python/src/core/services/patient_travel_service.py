"""
Servicio que detecta pacientes viajando entre ciudades para planificar telemedicina.
Utiliza anotaciones diferidas para referencias de tipo; `collections` para contadores y agrupaciones; `datetime` para calculos y validaciones de fechas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set

from ..models import PatientTravelEntry, PatientTravelReport, PatientRecord
from ..ports import AppointmentRepository, PatientRepository


class PatientTravelService:
    """
    Representa paciente viaje servicio y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    MIN_TRAVEL_ALERTS = 1

    def __init__(self, patient_repo: PatientRepository, appointment_repo: AppointmentRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.patient_repo = patient_repo
        self.appointment_repo = appointment_repo

    def analyze(self) -> PatientTravelReport:
        """
        Encapsula analyze, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        patients: Dict[int, PatientRecord] = {
            patient.id_paciente: patient for patient in self.patient_repo.list_patients()
            if patient.id_paciente is not None
        }

        travel_map: Dict[int, Dict[str, Set[str]]] = defaultdict(
            lambda: {"cities": set(), "dates": set()}
        )

        for appointment in self.appointment_repo.list_appointments():
            patient = patients.get(appointment.id_paciente)
            if not patient:
                continue
            residence = self._normalize_city(patient.ciudad)
            appointment_city = self._normalize_city(getattr(appointment, "ciudad", None))
            if not residence or not appointment_city or residence == appointment_city:
                continue
            travel_map[patient.id_paciente]["cities"].add(appointment_city)
            travel_map[patient.id_paciente]["dates"].add(self._friendly_date(appointment.fecha_cita))

        entries: List[PatientTravelEntry] = []
        for patient_id, travel in travel_map.items():
            if len(travel["cities"]) < self.MIN_TRAVEL_ALERTS:
                continue
            patient = patients[patient_id]
            cities = sorted(travel["cities"])
            dates = sorted(travel["dates"])
            severity = "high" if len(cities) > 1 else "medium"
            entries.append(
                PatientTravelEntry(
                    id_paciente=patient_id,
                    nombre=patient.nombre or f"Paciente {patient_id}",
                    residence=self._normalize_city(patient.ciudad),
                    travel_cities=cities,
                    travel_count=len(cities),
                    severity=severity,
                    last_travel_dates=dates,
                )
            )

        entries.sort(key=lambda entry: (-entry.travel_count, entry.nombre))

        return PatientTravelReport(
            generated_at=datetime.utcnow().isoformat(),
            total_travelers=len(entries),
            entries=entries,
        )

    @staticmethod
    def _normalize_city(value: Optional[str]) -> str:
        """
        Encapsula normalize ciudad, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        if not value:
            return ""
        return value.strip().title()

    @staticmethod
    def _friendly_date(value: Optional[str]) -> str:
        """
        Encapsula friendly date, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        if not value:
            return "Sin fecha"
        try:
            parsed = datetime.fromisoformat(value)
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            return value
