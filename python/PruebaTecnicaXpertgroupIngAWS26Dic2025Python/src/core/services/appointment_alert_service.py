"""Servicio que detecta citas sin información crítica y genera alertas."""

from __future__ import annotations

from typing import List

from ..models import AppointmentAlertEntry, AppointmentAlertReport
from ..ports import AppointmentRepository


class AppointmentAlertService:
    def __init__(self, repository: AppointmentRepository):
        self.repository = repository

    def scan_alerts(self) -> AppointmentAlertReport:
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
