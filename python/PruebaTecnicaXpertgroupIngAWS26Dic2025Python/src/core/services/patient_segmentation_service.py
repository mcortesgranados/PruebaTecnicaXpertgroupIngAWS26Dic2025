"""Servicio para generar segmentos de pacientes por edad, sexo y frecuencia de citas."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from ..models import PatientSegmentationReport, PatientSegment
from ..ports import AppointmentRepository, PatientRepository


class PatientSegmentationService:
    AGE_BUCKETS = [
        ("0-17 (Niños)", 0, 17),
        ("18-34 (Adultos jóvenes)", 18, 34),
        ("35-64 (Adultos)", 35, 64),
        ("65+ (Adultos mayores)", 65, 200),
    ]

    def __init__(self, patient_repo: PatientRepository, appointment_repo: AppointmentRepository):
        self.patient_repo = patient_repo
        self.appointment_repo = appointment_repo

    def segment(self) -> PatientSegmentationReport:
        appointment_counts = self._count_appointments()
        buckets: Dict[tuple[str, str, str], int] = {}
        total_patients = 0
        for patient in self.patient_repo.list_patients():
            total_patients += 1
            age = self._calculate_age(patient)
            age_segment = self._label_age_segment(age)
            sexo_label = self._normalize_sex(patient.sexo)
            frequency_label = self._frequency_bucket(appointment_counts.get(patient.id_paciente, 0))
            key = (age_segment, sexo_label, frequency_label)
            buckets[key] = buckets.get(key, 0) + 1

        cohorts = [
            PatientSegment(
                age_segment=age_label,
                sexo=sexo_label,
                frequency_bucket=frequency_label,
                count=count,
            )
            for (age_label, sexo_label, frequency_label), count in sorted(
                buckets.items(), key=lambda item: item[1], reverse=True
            )
        ]

        return PatientSegmentationReport(
            generated_at=datetime.utcnow().isoformat(),
            total_patients=total_patients,
            cohorts=cohorts,
        )

    def _count_appointments(self) -> Dict[int, int]:
        counts: Dict[int, int] = {}
        for appointment in self.appointment_repo.list_appointments():
            if appointment.id_paciente is None:
                continue
            counts[appointment.id_paciente] = counts.get(appointment.id_paciente, 0) + 1
        return counts

    def _calculate_age(self, patient) -> Optional[int]:
        if isinstance(patient.edad, int):
            return patient.edad
        if patient.fecha_nacimiento:
            try:
                born = datetime.fromisoformat(patient.fecha_nacimiento)
            except ValueError:
                return None
            today = datetime.utcnow()
            age = today.year - born.year - (
                (today.month, today.day) < (born.month, born.day)
            )
            return max(age, 0)
        return None

    def _label_age_segment(self, age: Optional[int]) -> str:
        if age is None:
            return "Edad desconocida"
        for label, minimum, maximum in self.AGE_BUCKETS:
            if minimum <= age <= maximum:
                return label
        return "Edad adulta"

    def _normalize_sex(self, sexo: Optional[str]) -> str:
        if not sexo:
            return "No declarado"
        cleaned = sexo.strip().lower()
        if cleaned in {"f", "femenino", "female"}:
            return "Femenino"
        if cleaned in {"m", "masculino", "male"}:
            return "Masculino"
        return sexo.strip().title()

    def _frequency_bucket(self, count: int) -> str:
        if count == 0:
            return "Sin citas registradas"
        if count <= 2:
            return "Frecuencia baja (1-2 citas)"
        if count <= 4:
            return "Frecuencia moderada (3-4 citas)"
        return "Frecuencia alta (5+ citas)"
