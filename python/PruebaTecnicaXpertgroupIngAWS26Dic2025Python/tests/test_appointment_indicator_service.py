from src.core.models import AppointmentRecord
from src.core.services import AppointmentIndicatorService
from src.core.ports import AppointmentRepository


class DummyAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        return iter(self._appointments)


def test_appointment_indicators_count_daily_and_weekly():
    appointments = [
        AppointmentRecord(
            id_cita="1",
            id_paciente=1,
            fecha_cita="2025-01-01T10:00:00",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=100.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="2",
            id_paciente=2,
            fecha_cita="2025-01-01T11:00:00",
            especialidad="Cardiología",
            medico="Dr. B",
            costo=120.0,
            estado_cita="Reprogramada",
        ),
        AppointmentRecord(
            id_cita="3",
            id_paciente=3,
            fecha_cita=None,
            especialidad="Pediatría",
            medico=None,
            costo=80.0,
            estado_cita="Pendiente",
        ),
    ]

    report = AppointmentIndicatorService(DummyAppointmentRepository(appointments)).measure_indicators()

    assert report.total_records == 3
    assert report.missing_date == 1
    assert any(
        entry.period_type == "daily"
        and entry.period_value == "2025-01-01"
        and entry.especialidad == "Cardiología"
        and entry.estado_cita == "Completada"
        and entry.medico == "Dr. A"
        and entry.count == 1
        for entry in report.entries
    )
    assert any(
        entry.period_type == "weekly"
        and entry.period_value == "2025-W01"
        and entry.especialidad == "Cardiología"
        and entry.estado_cita == "Reprogramada"
        and entry.medico == "Dr. B"
        and entry.count == 1
        for entry in report.entries
    )
    assert len(report.bottlenecks) == 5 or len(report.entries) < 5
