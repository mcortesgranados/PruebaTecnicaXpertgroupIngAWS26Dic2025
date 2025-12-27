"""Servicio para detectar desvíos de edad frente a especialidad."""

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
    EXPECTED_RANGES = [
        ("pediatr", 0, 17),
        ("geriatr", 65, 150),
    ]
    DEFAULT_RANGE = (18, 64)

    def __init__(self, appointment_repo: AppointmentRepository, patient_repo: PatientRepository):
        self.appointment_repo = appointment_repo
        self.patient_repo = patient_repo

    def analyze(self) -> AgeSpecialtyMismatchReport:
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
        return {patient.id_paciente: patient for patient in self.patient_repo.list_patients()}

    @classmethod
    def _expected_range(cls, specialty: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
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
