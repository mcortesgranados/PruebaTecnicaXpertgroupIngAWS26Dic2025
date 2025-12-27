from src.core.models import AppointmentRecord, PatientRecord
from src.core.services import QualityKpiService
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


def test_quality_kpis_report_contains_expected_fields():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre="Paciente Completo",
            fecha_nacimiento="1990-01-01",
            edad=35,
            sexo="Female",
            email="user@example.com",
            telefono="123",
            ciudad="Bogotá",
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Paciente Null",
            fecha_nacimiento=None,
            edad=None,
            sexo=None,
            email=None,
            telefono=None,
            ciudad=None,
        ),
    ]
    appointments = [
        AppointmentRecord(
            id_cita="1",
            id_paciente=1,
            fecha_cita="2025-01-01T10:00:00",
            especialidad="Cardiología",
            medico="Dr. A",
            costo=100.0,
            estado_cita="Completada",
        ),
        AppointmentRecord(
            id_cita="2",
            id_paciente=1,
            fecha_cita=None,
            especialidad="Cardiología",
            medico=None,
            costo=120.0,
            estado_cita="Programada",
        ),
    ]

    service = QualityKpiService(
        patient_repo_before=DummyPatientRepository(patients),
        appointment_repo_before=DummyAppointmentRepository(appointments),
    )
    report = service.compute()

    assert report.tables
    patient_table = next(table for table in report.tables if table.table_name == "pacientes")
    assert any(metric.field == "nombre" for metric in patient_table.before)
    assert any(metric.field == "fecha_nacimiento" for metric in patient_table.before)

    appointment_table = next(table for table in report.tables if table.table_name == "citas_medicas")
    estado_metric = next(metric for metric in appointment_table.before if metric.field == "estado_cita")
    assert estado_metric.completeness == 1.0
