from src.core.models import AppointmentRecord
from src.core.services import DemandForecastService
from src.core.ports import AppointmentRepository


class _InMemoryAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        yield from self._appointments


def test_forecast_computes_growth_and_gap():
    appointments = [
        AppointmentRecord(
            id_cita="A1",
            id_paciente=1,
            fecha_cita="2025-01-05T10:00:00",
            especialidad="General",
            medico="Dr. A",
            costo=None,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="A2",
            id_paciente=1,
            fecha_cita="2025-01-10T11:00:00",
            especialidad="General",
            medico="Dr. A",
            costo=None,
            estado_cita="Cancelada",
        ),
        AppointmentRecord(
            id_cita="A3",
            id_paciente=1,
            fecha_cita="2025-02-05T09:00:00",
            especialidad="General",
            medico="Dr. A",
            costo=None,
            estado_cita="Programada",
        ),
        AppointmentRecord(
            id_cita="A4",
            id_paciente=3,
            fecha_cita="2025-02-07T10:00:00",
            especialidad="General",
            medico="Dr. A",
            costo=None,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="A5",
            id_paciente=4,
            fecha_cita="2025-02-20T09:00:00",
            especialidad="General",
            medico="Dr. A",
            costo=None,
            estado_cita="Reprogramada",
        ),
        AppointmentRecord(
            id_cita="B1",
            id_paciente=2,
            fecha_cita="2025-01-12T09:00:00",
            especialidad="Cardiología",
            medico="Dr. B",
            costo=None,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="B2",
            id_paciente=2,
            fecha_cita="2025-02-15T09:00:00",
            especialidad="Cardiología",
            medico="Dr. B",
            costo=None,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="B3",
            id_paciente=2,
            fecha_cita="2025-02-25T09:00:00",
            especialidad="Cardiología",
            medico="Dr. B",
            costo=None,
            estado_cita="Reprogramada",
        ),
        AppointmentRecord(
            id_cita="B4",
            id_paciente=2,
            fecha_cita="2025-02-28T09:00:00",
            especialidad="Cardiología",
            medico="Dr. B",
            costo=None,
            estado_cita="Programada",
        ),
    ]

    service = DemandForecastService(_InMemoryAppointmentRepository(appointments))
    report = service.forecast()

    assert report.avg_monthly_growth == 1.0
    assert report.future_months[0] == "2025-03"
    dr_a_entry = next(entry for entry in report.entries if entry.doctor == "Dr. A" and entry.month == "2025-03")
    assert dr_a_entry.predicted_demand == 6
    assert dr_a_entry.capacity == 15
    assert dr_a_entry.gap == -9
    assert len(report.entries) == 6
