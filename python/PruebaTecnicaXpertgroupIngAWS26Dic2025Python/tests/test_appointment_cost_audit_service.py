from src.core.models import AppointmentRecord
from src.core.services import AppointmentCostAuditService
from src.core.ports import AppointmentRepository


class DummyAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        return iter(self._appointments)


def test_cost_audit_flags_deviations_beyond_two_std():
    appointments = [
        AppointmentRecord(
            id_cita="A",
            id_paciente=1,
            fecha_cita="2025-05-01",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=100.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="B",
            id_paciente=2,
            fecha_cita="2025-05-02",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=102.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="C",
            id_paciente=3,
            fecha_cita="2025-05-03",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=104.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="E",
            id_paciente=5,
            fecha_cita="2025-05-05",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=200.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="D",
            id_paciente=4,
            fecha_cita="2025-05-04",
            especialidad="Pediatría",
            medico="Dr. B",
            costo=150.0,
            estado_cita="Completada",
        ),
    ]

    report = AppointmentCostAuditService(DummyAppointmentRepository(appointments)).analyze()

    specialty_summary = {entry.especialidad: entry for entry in report.summaries}
    assert specialty_summary["Cardiología"].count == 4
    assert specialty_summary["Pediatría"].count == 1
    assert report.analyzed_records == 5
    assert len(report.anomalies) == 1
    anomaly = report.anomalies[0]
    assert anomaly.id_cita == "E"
    assert anomaly.especialidad == "Cardiología"
