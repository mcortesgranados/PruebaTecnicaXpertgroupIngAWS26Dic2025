from src.core.models import AppointmentRecord, PatientRecord
from src.core.services import ReferentialIntegrityService
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


def test_referential_integrity_detects_orphans():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre="Paciente 1",
            fecha_nacimiento="1990-01-01",
            edad=35,
            sexo="Female",
            email=None,
            telefono=None,
            ciudad="Bogotá",
        )
    ]
    appointments = [
        AppointmentRecord(
            id_cita="a",
            id_paciente=1,
            fecha_cita="2025-01-01",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=120.0,
            estado_cita="Programada",
        ),
        AppointmentRecord(
            id_cita="b",
            id_paciente=2,
            fecha_cita="2025-01-02",
            especialidad="Cardiología",
            medico="Dr. B",
            costo=110.0,
            estado_cita="Programada",
        ),
        AppointmentRecord(
            id_cita="c",
            id_paciente=None,
            fecha_cita="2025-01-03",
            especialidad="Pediatría",
            medico="Dr. C",
            costo=90.0,
            estado_cita="Programada",
        ),
    ]

    service = ReferentialIntegrityService(
        appointment_repo=DummyAppointmentRepository(appointments),
        patient_repo=DummyPatientRepository(patients),
    )
    report = service.check()

    assert report.total_citas == 3
    assert report.orphan_citas == 2
    motivos = {entry.id_cita: entry.motivo for entry in report.entries}
    assert motivos["b"] == "paciente no registrado"
    assert motivos["c"] == "id_paciente ausente"
