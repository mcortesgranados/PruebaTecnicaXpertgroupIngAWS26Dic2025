from src.core.models import AppointmentRecord
from src.core.services import AppointmentReviewService
from src.core.ports import AppointmentRepository


class DummyAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        return iter(self._appointments)


def test_appointment_review_finds_missing_data_in_completion_states():
    appointments = [
        AppointmentRecord(
            id_cita="1",
            id_paciente=10,
            fecha_cita="2025-07-01",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=100.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="2",
            id_paciente=11,
            fecha_cita=None,
            especialidad="Neurología",
            medico="",
            costo=150.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="3",
            id_paciente=12,
            fecha_cita="2025-07-02",
            especialidad="Pediatría",
            medico=None,
            costo=80.0,
            estado_cita="Cancelada",
        ),
        AppointmentRecord(
            id_cita="4",
            id_paciente=13,
            fecha_cita="2025-07-03",
            especialidad="Dermatología",
            medico="Dr. D",
            costo=90.0,
            estado_cita="Programada",
        ),
    ]

    report = AppointmentReviewService(DummyAppointmentRepository(appointments)).review()

    assert report.total_citas == 4
    assert report.reviewed_citas == 2
    ids = {entry.id_cita: entry for entry in report.entries}
    assert "fecha_cita inválida o ausente" in ids["2"].issues
    assert "médico no asignado" in ids["2"].issues
    assert "médico no asignado" in ids["3"].issues
