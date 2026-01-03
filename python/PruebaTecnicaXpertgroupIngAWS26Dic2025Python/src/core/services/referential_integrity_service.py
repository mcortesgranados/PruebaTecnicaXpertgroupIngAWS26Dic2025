"""
Servicio para validar integridad referencial entre pacientes y citas.
Utiliza anotaciones diferidas para referencias de tipo; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from typing import Iterable, List, Optional, Set

from ..models import ReferentialIntegrityEntry, ReferentialIntegrityReport
from ..ports import AppointmentRepository, PatientRepository


class ReferentialIntegrityService:
    """
    Representa referencial integridad servicio y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    def __init__(self, appointment_repo: AppointmentRepository, patient_repo: PatientRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.appointment_repo = appointment_repo
        self.patient_repo = patient_repo

    def check(self) -> ReferentialIntegrityReport:
        """
        Encapsula check, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

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
        """
        Encapsula load paciente ids, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        return {patient.id_paciente for patient in self.patient_repo.list_patients()}
