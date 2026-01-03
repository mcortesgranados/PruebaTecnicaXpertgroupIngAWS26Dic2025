"""
Servicio que evalúa la consistencia entre <code>fecha_nacimiento</code> y <code>edad</code>.
Utiliza anotaciones diferidas para referencias de tipo; `datetime` para calculos y validaciones de fechas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from ..models import AgeCorrectionLogEntry, AgeConsistencyReport, PatientRecord
from ..ports import PatientRepository


class AgeConsistencyService:
    """
    Representa Age Consistency servicio y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    def __init__(self, repository: PatientRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.repository = repository

    def audit_ages(self, cutoff_date: date) -> AgeConsistencyReport:
        """
        Encapsula auditoria ages, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        records = list(self.repository.list_patients())
        log_entries: List[AgeCorrectionLogEntry] = []
        inconsistencies = 0
        imputations = 0
        missing_birthdate_records = 0

        for record in records:
            birth_date = self._parse_birthdate(record.fecha_nacimiento)
            if birth_date is None:
                if not record.fecha_nacimiento:
                    action = "missing_birthdate"
                    note = (
                        "No se puede calcular la edad porque falta la fecha de nacimiento."
                    )
                else:
                    action = "invalid_birthdate"
                    note = (
                        "La fecha de nacimiento existe pero no cumple el formato ISO válido."
                    )
                missing_birthdate_records += 1
                log_entries.append(
                    AgeCorrectionLogEntry(
                        id_paciente=record.id_paciente,
                        nombre=record.nombre,
                        fecha_nacimiento=record.fecha_nacimiento,
                        edad_registrada=record.edad,
                        edad_calculada=None,
                        action=action,
                        note=note,
                    )
                )
                continue

            calculated_age = self._calculate_age(birth_date, cutoff_date)
            if record.edad is None:
                imputations += 1
                log_entries.append(
                    AgeCorrectionLogEntry(
                        id_paciente=record.id_paciente,
                        nombre=record.nombre,
                        fecha_nacimiento=record.fecha_nacimiento,
                        edad_registrada=None,
                        edad_calculada=calculated_age,
                        action="imputed_age",
                        note=(
                            f"Edad imputada usando la diferencia entre {cutoff_date.isoformat()} "
                            f"y la fecha de nacimiento."
                        ),
                    )
                )
                continue

            if record.edad != calculated_age:
                inconsistencies += 1
                log_entries.append(
                    AgeCorrectionLogEntry(
                        id_paciente=record.id_paciente,
                        nombre=record.nombre,
                        fecha_nacimiento=record.fecha_nacimiento,
                        edad_registrada=record.edad,
                        edad_calculada=calculated_age,
                        action="inconsistent_age",
                        note=(
                            f"La edad registrada ({record.edad}) no coincide con la calculada "
                            f"({calculated_age}) para la fecha de corte {cutoff_date.isoformat()}."
                        ),
                    )
                )

        return AgeConsistencyReport(
            cutoff_date=cutoff_date,
            total_records=len(records),
            inconsistencies=inconsistencies,
            imputations=imputations,
            missing_birthdate_records=missing_birthdate_records,
            log_entries=log_entries,
        )

    @staticmethod
    def _parse_birthdate(value: Optional[str]) -> Optional[date]:
        """
        Encapsula parse birthdate, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        if not value:
            return None
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None

    @staticmethod
    def _calculate_age(birth_date: date, cutoff_date: date) -> int:
        """
        Encapsula calculate age, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        years = cutoff_date.year - birth_date.year
        if (cutoff_date.month, cutoff_date.day) < (birth_date.month, birth_date.day):
            years -= 1
        return max(years, 0)
