from src.core.models import AppointmentRecord
from src.core.services import ManagementKpiService
from src.core.ports import AppointmentRepository


class _StubAppointmentRepo(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        yield from self._appointments


def test_reports_average_cost_and_wait():
    appointments = [
        AppointmentRecord(id_cita="A1", id_paciente=1, fecha_cita="2025-01-01", especialidad="Cardiología", medico="Dr. A", costo=100.0, estado_cita="Completada"),
        AppointmentRecord(id_cita="A2", id_paciente=1, fecha_cita="2025-01-10", especialidad="Cardiología", medico="Dr. A", costo=120.0, estado_cita="Completada"),
        AppointmentRecord(id_cita="B1", id_paciente=2, fecha_cita="2025-02-05", especialidad="Pediatría", medico="Dr. B", costo=80.0, estado_cita="Completada"),
    ]

    service = ManagementKpiService(_StubAppointmentRepo(appointments))
    report = service.report()

    assert report.overall_average_cost == (100 + 120 + 80) / 3
    assert report.overall_average_wait_days == 9  # only patient 1 had interval 9
    assert any(entry.specialty == "Cardiología" for entry in report.specialty_entries)
