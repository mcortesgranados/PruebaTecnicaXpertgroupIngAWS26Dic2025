from src.core.models import AppointmentRecord
from src.core.services import AppointmentAlertService
from src.core.ports import AppointmentRepository


class DummyAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        return iter(self._appointments)


def test_appointment_alert_service_flags_missing_fields():
    appointments = [
        AppointmentRecord(
            id_cita="1",
            id_paciente=10,
            fecha_cita=None,
            especialidad="Cardiología",
            medico="Dr. A",
            costo=90.0,
            estado_cita="Pendiente",
        ),
        AppointmentRecord(
            id_cita="2",
            id_paciente=11,
            fecha_cita="2025-03-01",
            especialidad="Neurología",
            medico="",
            costo=150.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="3",
            id_paciente=12,
            fecha_cita="2025-03-02",
            especialidad="Ginecología",
            medico="Dr. C",
            costo=130.0,
            estado_cita="Cancelada",
        ),
    ]

    report = AppointmentAlertService(DummyAppointmentRepository(appointments)).scan_alerts()

    assert report.total_records == 3
    assert report.alerts == 2
    ids = {entry.id_cita: entry for entry in report.entries}
    assert ids["1"].falta_fecha is True
    assert ids["1"].falta_medico is False
    assert "fecha_cita ausente" in ids["1"].note
    assert ids["2"].falta_fecha is False
    assert ids["2"].falta_medico is True
    assert "médico sin asignar" in ids["2"].note
