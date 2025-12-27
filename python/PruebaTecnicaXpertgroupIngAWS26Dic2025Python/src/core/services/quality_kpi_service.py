"""Servicio para calcular KPIs de calidad antes y después de la limpieza."""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Callable, Dict, Iterable, List, Optional, Sequence

from ..models import (
    FieldQualityMetric,
    TableQualityMetrics,
    QualityKpiReport,
    PatientRecord,
    AppointmentRecord,
)
from ..ports import AppointmentRepository, PatientRepository


class QualityKpiService:
    PATIENT_FIELDS = [
        ("nombre", None),
        ("fecha_nacimiento", "_is_valid_date"),
        ("email", "_is_valid_email"),
        ("telefono", None),
        ("ciudad", None),
    ]
    APPOINTMENT_FIELDS = [
        ("fecha_cita", "_is_valid_date"),
        ("especialidad", None),
        ("medico", None),
        ("estado_cita", None),
    ]

    def __init__(
        self,
        patient_repo_before: PatientRepository,
        appointment_repo_before: AppointmentRepository,
        patient_repo_after: Optional[PatientRepository] = None,
        appointment_repo_after: Optional[AppointmentRepository] = None,
    ):
        self.patient_repo_before = patient_repo_before
        self.appointment_repo_before = appointment_repo_before
        self.patient_repo_after = patient_repo_after or patient_repo_before
        self.appointment_repo_after = appointment_repo_after or appointment_repo_before

    def compute(self) -> QualityKpiReport:
        patients_before = list(self.patient_repo_before.list_patients())
        appointments_before = list(self.appointment_repo_before.list_appointments())
        patients_after = list(self.patient_repo_after.list_patients())
        appointments_after = list(self.appointment_repo_after.list_appointments())

        tables = [
            TableQualityMetrics(
                table_name="pacientes",
                before=self._compute_metrics(
                    patients_before, self.PATIENT_FIELDS
                ),
                after=self._compute_metrics(
                    patients_after, self.PATIENT_FIELDS
                ),
            ),
            TableQualityMetrics(
                table_name="citas_medicas",
                before=self._compute_metrics(
                    appointments_before, self.APPOINTMENT_FIELDS
                ),
                after=self._compute_metrics(
                    appointments_after, self.APPOINTMENT_FIELDS
                ),
            ),
        ]

        return QualityKpiReport(
            generated_at=datetime.utcnow().isoformat(),
            tables=tables,
        )

    def _compute_metrics(
        self, records: Sequence, fields: Sequence, limit: Optional[int] = None
    ) -> List[FieldQualityMetric]:
        total = len(records)
        metrics: List[FieldQualityMetric] = []
        for field_name, checker in fields:
            completeness = self._completeness(records, field_name)
            uniqueness = self._uniqueness(records, field_name)
            format_valid = self._format_validity(records, checker, field_name)
            metrics.append(
                FieldQualityMetric(
                    field=field_name,
                    completeness=completeness,
                    uniqueness=uniqueness,
                    format_valid=format_valid,
                )
            )
        return metrics

    @staticmethod
    def _completeness(records: Sequence, field: str) -> float:
        if not records:
            return 0.0
        filled = sum(
            1
            for record in records
            if getattr(record, field, None)
            not in (None, "", [], {})
        )
        return filled / len(records)

    @staticmethod
    def _uniqueness(records: Sequence, field: str) -> float:
        if not records:
            return 0.0
        values = [getattr(record, field, None) for record in records]
        unique = len(set(values))
        return unique / len(records)

    def _format_validity(
        self, records: Sequence, checker: Optional[str], field: str
    ) -> float:
        if not checker:
            return 1.0
        check_fn = getattr(self, checker)
        valid = sum(1 for record in records if check_fn(getattr(record, field, None)))
        return valid / len(records) if records else 0.0

    @staticmethod
    def _is_valid_date(value: Optional[str]) -> bool:
        if not value:
            return False
        try:
            datetime.fromisoformat(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_valid_email(value: Optional[str]) -> bool:
        if not value or "@" not in value:
            return False
        return "." in value.split("@")[-1]
