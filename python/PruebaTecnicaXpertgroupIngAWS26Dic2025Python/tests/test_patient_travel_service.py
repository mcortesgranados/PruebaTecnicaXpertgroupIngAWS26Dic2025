from src.core.models import AppointmentRecord, PatientRecord
from src.core.services import PatientTravelService
from src.core.ports import AppointmentRepository, PatientRepository


class _StubPatientRepo(PatientRepository):
    def __init__(self, patients):
        self._patients = patients

    def list_patients(self):
        yield from self._patients


class _StubAppointmentRepo(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        yield from self._appointments


def test_detects_travel_between_cities():
    patients = [
        PatientRecord(id_paciente=1, nombre="Ana", fecha_nacimiento="1990-01-01", edad=34, sexo="F", email=None, telefono=None, ciudad="Bogotá"),
        PatientRecord(id_paciente=2, nombre="Luis", fecha_nacimiento="1985-01-01", edad=39, sexo="M", email=None, telefono=None, ciudad="Cali"),
    ]
    appointments = [
        AppointmentRecord(id_cita="C1", id_paciente=1, fecha_cita="2025-03-01", especialidad="General", medico="Dr. A", costo=None, estado_cita="Completada", ciudad="Medellín"),
        AppointmentRecord(id_cita="C2", id_paciente=1, fecha_cita="2025-03-15", especialidad="General", medico="Dr. A", costo=None, estado_cita="Completada", ciudad="Bogotá"),
        AppointmentRecord(id_cita="C3", id_paciente=2, fecha_cita="2025-03-05", especialidad="General", medico="Dr. B", costo=None, estado_cita="Completada", ciudad="Cali"),
    ]

    service = PatientTravelService(_StubPatientRepo(patients), _StubAppointmentRepo(appointments))
    report = service.analyze()

    assert report.total_travelers == 1
    entry = report.entries[0]
    assert entry.id_paciente == 1
    assert "Medellín" in entry.travel_cities
    assert entry.severity == "medium"
