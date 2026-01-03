"""
Servicio que alerta médicos sobre pacientes con patrones sospechosos.
Utiliza anotaciones diferidas para referencias de tipo; `collections` para contadores y agrupaciones; `datetime` para calculos y validaciones de fechas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from ..models import DoctorNotificationEntry, DoctorNotificationReport, PatientRecord
from ..ports import AppointmentRepository, PatientRepository


class DoctorNotificationService:
    """
    Representa medico notificacion servicio y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    RECENT_WINDOW_DAYS = 7
    CANCEL_THRESHOLD = 2

    def __init__(self, patient_repo: PatientRepository, appointment_repo: AppointmentRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.patient_repo = patient_repo
        self.appointment_repo = appointment_repo

    def analyze(self) -> DoctorNotificationReport:
        """
        Encapsula analyze, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        patients = {p.id_paciente: p for p in self.patient_repo.list_patients()}
        grouped: Dict[tuple[str, Optional[int]], List] = defaultdict(list)

        for appointment in self.appointment_repo.list_appointments():
            doctor = (appointment.medico or "Sin médico").strip().title()
            grouped[(doctor, appointment.id_paciente)].append(appointment)

        entries: List[DoctorNotificationEntry] = []
        for (doctor, patient_id), appts in grouped.items():
            if patient_id is None:
                continue
            appts_sorted = sorted(appts, key=lambda a: self._parse_date(a.fecha_cita) or datetime.min)
            patterns = self._detect_patterns(appts_sorted)
            if not patterns:
                continue
            patient = patients.get(patient_id)
            name = patient.nombre if patient else f"Paciente {patient_id}"
            dates = [self._format_date(a.fecha_cita) for a in appts_sorted if self._parse_date(a.fecha_cita)]
            severity = "high" if len(patterns) > 1 else "medium"
            entries.append(
                DoctorNotificationEntry(
                    doctor=doctor,
                    id_paciente=patient_id,
                    nombre=name,
                    patterns=patterns,
                    severity=severity,
                    appointment_dates=dates,
                )
            )
        return DoctorNotificationReport(
            generated_at=datetime.utcnow().isoformat(),
            total_alerts=len(entries),
            entries=sorted(entries, key=lambda e: len(e.patterns), reverse=True),
        )

    def _detect_patterns(self, appointments) -> List[str]:
        """
        Encapsula detect patterns, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        patterns: List[str] = []
        cancels = 0
        prev_date: Optional[datetime] = None
        closeness = 0

        for appointment in appointments:
            date = self._parse_date(appointment.fecha_cita)
            if appointment.estado_cita and appointment.estado_cita.strip().lower() == "cancelada":
                cancels += 1
            if prev_date and date:
                delta = (date - prev_date).days
                if delta <= self.RECENT_WINDOW_DAYS:
                    closeness += 1
            if date:
                prev_date = date
        if closeness >= 2:
            patterns.append("Múltiples citas en períodos cortos")
        if cancels >= self.CANCEL_THRESHOLD:
            patterns.append("Cancelaciones recurrentes")
        return patterns

    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[datetime]:
        """
        Encapsula parse date, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _format_date(value: Optional[str]) -> Optional[str]:
        """
        Encapsula format date, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        parsed = DoctorNotificationService._parse_date(value)
        return parsed.strftime("%Y-%m-%d") if parsed else None
