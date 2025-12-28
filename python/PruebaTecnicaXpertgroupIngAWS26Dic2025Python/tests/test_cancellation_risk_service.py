from datetime import datetime, timedelta

from src.core.models import AppointmentRecord
from src.core.services import CancellationRiskService
from src.core.ports import AppointmentRepository


class _InMemoryAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        yield from self._appointments


def test_high_risk_triggers_with_prior_cancel_and_short_interval():
    appointments = [
        AppointmentRecord(
            id_cita="A1",
            id_paciente=1,
            fecha_cita="2025-01-01T10:00:00",
            especialidad="General",
            medico="Dr. M",
            costo=100.0,
            estado_cita="Cancelada",
        ),
        AppointmentRecord(
            id_cita="A2",
            id_paciente=1,
            fecha_cita="2025-01-03T10:00:00",
            especialidad="General",
            medico="Dr. M",
            costo=120.0,
            estado_cita="Programada",
        ),
        AppointmentRecord(
            id_cita="B1",
            id_paciente=2,
            fecha_cita="2025-02-10T09:00:00",
            especialidad="Cardiología",
            medico="Dr. C",
            costo=80.0,
            estado_cita="Programada",
        ),
    ]

    service = CancellationRiskService(_InMemoryAppointmentRepository(appointments))
    report = service.analyze()

    assert report.total_records == 3
    assert report.high_risk_count >= 1
    assert report.entries[0].id_cita == "A2"
    assert any("Cancelación previa" in factor for factor in report.entries[0].factors)
    assert report.entries[0].days_since_last == 2


def test_specialty_risk_summary_includes_all_entries():
    appointments = [
        AppointmentRecord(
            id_cita="C1",
            id_paciente=3,
            fecha_cita="2025-03-01",
            especialidad="Pediatría",
            medico="Dr. P",
            costo=90.0,
            estado_cita="Programada",
        )
    ]
    service = CancellationRiskService(_InMemoryAppointmentRepository(appointments))
    report = service.analyze()

    assert report.specialty_risk["pediatría"] > 0
    assert report.average_risk <= 1
