"""
Servicio para detectar desvíos de edad frente a especialidad.
Utiliza anotaciones diferidas para referencias de tipo; `datetime` para calculos y validaciones de fechas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from ..models import (
    AgeSpecialtyMismatchEntry,
    AgeSpecialtyMismatchReport,
    AppointmentRecord,
    PatientRecord,
)
from ..ports import AppointmentRepository, PatientRepository


class AgeSpecialtyMismatchService:
    """
    Representa Age Specialty Mismatch servicio y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    EXPECTED_RANGES = [
        ("pediatr", 0, 17),
        ("geriatr", 65, 150),
    ]
    DEFAULT_RANGE = (18, 64)

    def __init__(self, appointment_repo: AppointmentRepository, patient_repo: PatientRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.appointment_repo = appointment_repo
        self.patient_repo = patient_repo

    def analyze(self) -> AgeSpecialtyMismatchReport:
        """
        Encapsula analyze, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        patient_map = self._load_patients()
        records = list(self.appointment_repo.list_appointments())
        entries: List[AgeSpecialtyMismatchEntry] = []

        for record in records:
            patient = patient_map.get(record.id_paciente)
            if not patient:
                continue

            appointment_age = self._calculate_age(patient, record)
            if appointment_age is None:
                continue

            expected_min, expected_max = self._expected_range(record.especialidad)
            if expected_min is not None and appointment_age < expected_min:
                entries.append(
                    AgeSpecialtyMismatchEntry(
                        id_cita=record.id_cita,
                        id_paciente=record.id_paciente,
                        especialidad=record.especialidad,
                        edad_calculada=appointment_age,
                        expected_min=expected_min,
                        expected_max=expected_max,
                        note=f"Edad {appointment_age} por debajo del mínimo esperado {expected_min} para {record.especialidad}.",
                    )
                )
            elif expected_max is not None and appointment_age > expected_max:
                entries.append(
                    AgeSpecialtyMismatchEntry(
                        id_cita=record.id_cita,
                        id_paciente=record.id_paciente,
                        especialidad=record.especialidad,
                        edad_calculada=appointment_age,
                        expected_min=expected_min,
                        expected_max=expected_max,
                        note=f"Edad {appointment_age} por encima del máximo esperado {expected_max} para {record.especialidad}.",
                    )
                )

        return AgeSpecialtyMismatchReport(
            total_citas=len(records),
            flagged_citas=len(entries),
            entries=entries,
        )

    def _load_patients(self) -> Dict[int, PatientRecord]:
        """
        Encapsula load patients, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {patient.id_paciente: patient for patient in self.patient_repo.list_patients()}

    @classmethod
    def _expected_range(cls, specialty: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        """
        Encapsula expected range, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        if not specialty:
            return cls.DEFAULT_RANGE
        normalized = specialty.lower()
        for keyword, min_age, max_age in cls.EXPECTED_RANGES:
            if keyword in normalized:
                return min_age, max_age
        if "geriatr" in normalized:
            return 65, 150
        if "pediatr" in normalized:
            return 0, 17
        return cls.DEFAULT_RANGE

    @staticmethod
    def _calculate_age(patient: PatientRecord, appointment: AppointmentRecord) -> Optional[int]:
        """
        Encapsula calculate age, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        if not patient.fecha_nacimiento or not appointment.fecha_cita:
            return None
        try:
            birth = datetime.fromisoformat(patient.fecha_nacimiento)
            appointment_date = datetime.fromisoformat(appointment.fecha_cita)
        except ValueError:
            return None
        years = appointment_date.year - birth.year
        if (appointment_date.month, appointment_date.day) < (birth.month, birth.day):
            years -= 1
        return years if years >= 0 else None
