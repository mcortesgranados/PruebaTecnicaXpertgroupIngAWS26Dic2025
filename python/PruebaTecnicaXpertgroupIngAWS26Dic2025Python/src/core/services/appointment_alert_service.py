"""
Servicio que detecta citas sin información crítica y genera alertas.
Utiliza anotaciones diferidas para referencias de tipo; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from typing import List

from ..models import AppointmentAlertEntry, AppointmentAlertReport
from ..ports import AppointmentRepository


class AppointmentAlertService:
    """
    Representa cita Alert servicio y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    def __init__(self, repository: AppointmentRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.repository = repository

    def scan_alerts(self) -> AppointmentAlertReport:
        """
        Encapsula scan alertas, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        records = list(self.repository.list_appointments())
        entries: List[AppointmentAlertEntry] = []

        for record in records:
            falta_fecha = not record.fecha_cita or not record.fecha_cita.strip()
            falta_medico = not record.medico or not record.medico.strip()
            if not (falta_fecha or falta_medico):
                continue

            note_parts = []
            if falta_fecha:
                note_parts.append("fecha_cita ausente")
            if falta_medico:
                note_parts.append("médico sin asignar")
            note = "Alerta automática: " + " y ".join(note_parts) + ". Validar manualmente."

            entries.append(
                AppointmentAlertEntry(
                    id_cita=record.id_cita,
                    id_paciente=record.id_paciente,
                    falta_fecha=falta_fecha,
                    falta_medico=falta_medico,
                    especialidad=record.especialidad,
                    note=note,
                )
            )

        return AppointmentAlertReport(
            total_records=len(records),
            alerts=len(entries),
            entries=entries,
        )
