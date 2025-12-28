from src.core.models import AppointmentRecord
from src.core.services import DoctorUtilizationService
from src.core.ports import AppointmentRepository


class _StubAppointmentRepo(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        yield from self._appointments


def test_calls_out_low_utilization_and_cancellations():
    appointments = [
        AppointmentRecord(id_cita="C1", id_paciente=1, fecha_cita="2025-01-05", especialidad="Cardiología", medico="Dr. X", costo=None, estado_cita="Completada"),
        AppointmentRecord(id_cita="C2", id_paciente=2, fecha_cita="2025-01-06", especialidad="Cardiología", medico="Dr. X", costo=None, estado_cita="Cancelada"),
        AppointmentRecord(id_cita="C3", id_paciente=3, fecha_cita="2025-01-07", especialidad="Cardiología", medico="Dr. X", costo=None, estado_cita="Reprogramada"),
        AppointmentRecord(id_cita="C4", id_paciente=4, fecha_cita="2025-01-08", especialidad="Cardiología", medico="Dr. X", costo=None, estado_cita="Cancelada"),
        AppointmentRecord(id_cita="C5", id_paciente=5, fecha_cita="2025-01-09", especialidad="Cardiología", medico="Dr. X", costo=None, estado_cita="Completada"),
    ]

    service = DoctorUtilizationService(_StubAppointmentRepo(appointments))
    report = service.analyze()

    assert len(report.entries) == 1
    assert report.entries[0].status in {"low_utilization", "high_cancellations"}
    assert report.entries[0].utilization_rate == 2/5
    assert report.entries[0].cancellation_rate == 3/5
