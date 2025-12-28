from src.core.models import AppointmentRecord, PatientRecord
from src.core.services import OccupancyDashboardService
from src.core.ports import AppointmentRepository, PatientRepository


class _SimplePatientRepository(PatientRepository):
    def __init__(self, patients):
        self._patients = patients

    def list_patients(self):
        yield from self._patients


class _SimpleAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments):
        self._appointments = appointments

    def list_appointments(self):
        yield from self._appointments


def test_summarize_counts_per_city_and_specialty():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre="Ana",
            fecha_nacimiento="1990-01-01",
            edad=35,
            sexo="F",
            email=None,
            telefono=None,
            ciudad="Bogotá",
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Luis",
            fecha_nacimiento="1980-01-01",
            edad=45,
            sexo="M",
            email=None,
            telefono=None,
            ciudad="Cali",
        ),
    ]
    appointments = [
        AppointmentRecord(
            id_cita="C1",
            id_paciente=1,
            fecha_cita="2025-01-01",
            especialidad="Pediatría",
            medico="Dr. A",
            costo=None,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="C2",
            id_paciente=1,
            fecha_cita="2025-01-02",
            especialidad="Pediatría",
            medico="Dr. A",
            costo=None,
            estado_cita="Reprogramada",
        ),
        AppointmentRecord(
            id_cita="C3",
            id_paciente=2,
            fecha_cita="2025-01-03",
            especialidad="Cardiología",
            medico="Dr. C",
            costo=None,
            estado_cita="Cancelada",
        ),
    ]

    service = OccupancyDashboardService(
        _SimplePatientRepository(patients),
        _SimpleAppointmentRepository(appointments),
    )
    report = service.summarize()

    assert report.total_appointments == 3
    assert report.entries[0].city == "Bogotá"
    assert report.entries[0].specialty == "Pediatría"
    assert report.entries[0].completed == 1
    assert report.entries[0].reprogrammed == 1
    assert report.entries[1].specialty == "Cardiología"
    assert report.entries[1].canceled == 1
