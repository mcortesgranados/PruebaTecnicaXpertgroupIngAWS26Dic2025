from src.core.models import AppointmentRecord, PatientRecord
from src.core.services import AccessibilityService
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


def test_accessibility_flags_high_volume_out_of_city():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre="Viaja",
            fecha_nacimiento="1990-01-01",
            edad=35,
            sexo="Female",
            email=None,
            telefono=None,
            ciudad="Bogotá",
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Local",
            fecha_nacimiento="1985-01-01",
            edad=40,
            sexo="Male",
            email=None,
            telefono=None,
            ciudad="Medellín",
        ),
    ]
    appointments = [
        AppointmentRecord(
            id_cita=str(i),
            id_paciente=1,
            fecha_cita="2025-01-01",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=100.0,
            estado_cita="Completada",
        )
        for i in range(5)
    ] + [
        AppointmentRecord(
            id_cita="6",
            id_paciente=2,
            fecha_cita="2025-02-01",
            especialidad="Pediatría",
            medico="Dr. B",
            costo=80.0,
            estado_cita="Completada",
        )
    ]

    report = AccessibilityService(
        patient_repo=DummyPatientRepository(patients),
        appointment_repo=DummyAppointmentRepository(appointments),
    ).evaluate()

    assert report.flagged == 1
    assert report.entries[0].id_paciente == 1
