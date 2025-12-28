from src.core.models import AppointmentRecord, PatientRecord
from src.core.services import DoctorNotificationService
from src.core.ports import AppointmentRepository, PatientRepository


class _DummyPatientRepo(PatientRepository):
    def __init__(self, patients):
        self._patients = patients

    def list_patients(self):
        yield from self._patients


class _DummyAppointmentRepo(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        yield from self._appointments


def test_alerts_detect_high_frequency_and_cancellations():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre="Test Nombre",
            fecha_nacimiento="1990-01-01",
            edad=35,
            sexo="M",
            email=None,
            telefono=None,
            ciudad=None,
        )
    ]
    appointments = [
        AppointmentRecord(
            id_cita="A1",
            id_paciente=1,
            fecha_cita="2025-03-01",
            especialidad="General",
            medico="Dr. Alert",
            costo=None,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="A2",
            id_paciente=1,
            fecha_cita="2025-03-03",
            especialidad="General",
            medico="Dr. Alert",
            costo=None,
            estado_cita="Cancelada",
        ),
        AppointmentRecord(
            id_cita="A3",
            id_paciente=1,
            fecha_cita="2025-03-06",
            especialidad="General",
            medico="Dr. Alert",
            costo=None,
            estado_cita="Cancelada",
        ),
        AppointmentRecord(
            id_cita="A4",
            id_paciente=1,
            fecha_cita="2025-04-10",
            especialidad="General",
            medico="Dr. Alert",
            costo=None,
            estado_cita="Completada",
        ),
    ]

    service = DoctorNotificationService(_DummyPatientRepo(patients), _DummyAppointmentRepo(appointments))
    report = service.analyze()

    assert report.total_alerts == 1
    entry = report.entries[0]
    assert "Múltiples citas en períodos cortos" in entry.patterns
    assert "Cancelaciones recurrentes" in entry.patterns
    assert entry.severity == "high"
