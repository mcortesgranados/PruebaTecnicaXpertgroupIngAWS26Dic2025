"""Servicio para validar integridad referencial entre pacientes y citas."""

from __future__ import annotations

from typing import Iterable, List, Optional, Set

from ..models import ReferentialIntegrityEntry, ReferentialIntegrityReport
from ..ports import AppointmentRepository, PatientRepository


class ReferentialIntegrityService:
    def __init__(self, appointment_repo: AppointmentRepository, patient_repo: PatientRepository):
        self.appointment_repo = appointment_repo
        self.patient_repo = patient_repo

    def check(self) -> ReferentialIntegrityReport:
        patient_ids = self._load_patient_ids()
        records = list(self.appointment_repo.list_appointments())
        entries: List[ReferentialIntegrityEntry] = []

        for record in records:
            if record.id_paciente is None:
                entries.append(
                    ReferentialIntegrityEntry(
                        id_cita=record.id_cita,
                        id_paciente=None,
                        motivo="id_paciente ausente",
                    )
                )
                continue

            if record.id_paciente not in patient_ids:
                entries.append(
                    ReferentialIntegrityEntry(
                        id_cita=record.id_cita,
                        id_paciente=record.id_paciente,
                        motivo="paciente no registrado",
                    )
                )

        return ReferentialIntegrityReport(
            total_citas=len(records),
            orphan_citas=len(entries),
            entries=entries,
        )

    def _load_patient_ids(self) -> Set[int]:
        return {patient.id_paciente for patient in self.patient_repo.list_patients()}
