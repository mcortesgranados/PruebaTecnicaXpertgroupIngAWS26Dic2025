from datetime import datetime

from src.core.models import AppointmentRecord, PatientRecord
from src.core.services import AgeSpecialtyMismatchService
from src.core.ports import AppointmentRepository, PatientRepository


class DummyAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        return iter(self._appointments)


class DummyPatientRepository(PatientRepository):
    def __init__(self, patients):
        self._patients = patients

    def list_patients(self):
        return iter(self._patients)


def test_age_specialty_mismatch_flags_pediatric_and_geriatric_outliers():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre="Niño 1",
            fecha_nacimiento="2015-01-01",
            edad=8,
            sexo="Male",
            email=None,
            telefono=None,
            ciudad="Bogotá",
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Adulto 1",
            fecha_nacimiento="1980-01-01",
            edad=45,
            sexo="Female",
            email=None,
            telefono=None,
            ciudad="Medellín",
        ),
        PatientRecord(
            id_paciente=3,
            nombre="Anciano 1",
            fecha_nacimiento="1940-01-01",
            edad=82,
            sexo="Male",
            email=None,
            telefono=None,
            ciudad="Cali",
        ),
    ]

    appointments = [
        AppointmentRecord(
            id_cita="pedi-anomaly",
            id_paciente=2,
            fecha_cita="2025-02-01",
            especialidad="Pediatría",
            medico="Dr. P",
            costo=100.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="geriatric-anomaly",
            id_paciente=1,
            fecha_cita="2025-02-02",
            especialidad="Geriatría",
            medico="Dr. G",
            costo=100.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="normal",
            id_paciente=1,
            fecha_cita="2025-02-03",
            especialidad="Pediatría",
            medico="Dr. P",
            costo=100.0,
            estado_cita="Completada",
        ),
    ]

    service = AgeSpecialtyMismatchService(
        appointment_repo=DummyAppointmentRepository(appointments),
        patient_repo=DummyPatientRepository(patients),
    )
    report = service.analyze()

    assert report.total_citas == 3
    assert report.flagged_citas == 2
    ids = {entry.id_cita: entry for entry in report.entries}
    assert "pedi-anomaly" in ids
    assert "geriatric-anomaly" in ids
