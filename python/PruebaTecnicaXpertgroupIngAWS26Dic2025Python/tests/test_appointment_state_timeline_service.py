from src.core.models import AppointmentRecord
from src.core.services import AppointmentStateTimelineService
from src.core.ports import AppointmentRepository


class DummyAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        return iter(self._appointments)


def test_state_timeline_tracks_reprogramaciones_and_occupancy():
    appointments = [
        AppointmentRecord(
            id_cita="1",
            id_paciente=10,
            fecha_cita="2025-06-01T08:00:00",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=100.0,
            estado_cita="Programada",
        ),
        AppointmentRecord(
            id_cita="1",
            id_paciente=10,
            fecha_cita="2025-06-03T09:00:00",
            especialidad="Cardiología",
            medico="Dr. B",
            costo=100.0,
            estado_cita="Reprogramada",
        ),
        AppointmentRecord(
            id_cita="1",
            id_paciente=10,
            fecha_cita="2025-06-05T10:00:00",
            especialidad="Cardiología",
            medico="Dr. B",
            costo=100.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="2",
            id_paciente=11,
            fecha_cita="2025-06-02T11:00:00",
            especialidad="Pediatría",
            medico="Dr. C",
            costo=80.0,
            estado_cita="Completada",
        ),
    ]

    report = AppointmentStateTimelineService(DummyAppointmentRepository(appointments)).analyze()

    assert report.total_citas == 2
    assert report.reprogrammed_citas == 1
    entry = next(entry for entry in report.entries if entry.id_cita == "1")
    assert entry.reprogram_count == 1
    assert "Dr. A" in entry.doctors
    assert "Dr. B" in entry.doctors
    assert any(impact.medico == "Dr. B" and impact.reprograms >= 1 for impact in report.occupancy_impacts)
