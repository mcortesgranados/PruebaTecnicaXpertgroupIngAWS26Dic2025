from typing import Iterable, List

from src.core.models import AppointmentRecord, PatientRecord
from src.core.services import PatientSegmentationService
from src.core.ports import AppointmentRepository, PatientRepository


class _InMemoryPatientRepository(PatientRepository):
    def __init__(self, patients: List[PatientRecord]):
        self._patients = patients

    def list_patients(self) -> Iterable[PatientRecord]:
        yield from self._patients


class _InMemoryAppointmentRepository(AppointmentRepository):
    def __init__(self, appointments: List[AppointmentRecord]):
        self._appointments = appointments

    def list_appointments(self) -> Iterable[AppointmentRecord]:
        yield from self._appointments


def test_segment_prioritizes_high_frequency():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre="Ana",
            fecha_nacimiento="1993-05-02",
            edad=None,
            sexo="Femenino",
            email=None,
            telefono=None,
            ciudad=None,
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Carlos",
            fecha_nacimiento="1960-01-10",
            edad=None,
            sexo="Masculino",
            email=None,
            telefono=None,
            ciudad=None,
        ),
    ]
    appointments = [
        AppointmentRecord(id_cita="C1", id_paciente=1, fecha_cita=None, especialidad=None, medico=None, costo=None, estado_cita=None),
        AppointmentRecord(id_cita="C2", id_paciente=1, fecha_cita=None, especialidad=None, medico=None, costo=None, estado_cita=None),
        AppointmentRecord(id_cita="C3", id_paciente=1, fecha_cita=None, especialidad=None, medico=None, costo=None, estado_cita=None),
        AppointmentRecord(id_cita="C4", id_paciente=1, fecha_cita=None, especialidad=None, medico=None, costo=None, estado_cita=None),
        AppointmentRecord(id_cita="C5", id_paciente=1, fecha_cita=None, especialidad=None, medico=None, costo=None, estado_cita=None),
        AppointmentRecord(id_cita="C6", id_paciente=2, fecha_cita=None, especialidad=None, medico=None, costo=None, estado_cita=None),
    ]

    service = PatientSegmentationService(_InMemoryPatientRepository(patients), _InMemoryAppointmentRepository(appointments))
    report = service.segment()

    assert report.total_patients == 2
    assert report.cohorts[0].sexo == "Femenino"
    assert report.cohorts[0].frequency_bucket == "Frecuencia alta (5+ citas)"
    assert report.cohorts[1].frequency_bucket == "Frecuencia baja (1-2 citas)"


def test_segment_handles_missing_age_and_sex():
    patient = PatientRecord(
        id_paciente=3,
        nombre="Sin datos",
        fecha_nacimiento=None,
        edad=None,
        sexo=None,
        email=None,
        telefono=None,
        ciudad=None,
    )
    service = PatientSegmentationService(
        _InMemoryPatientRepository([patient]),
        _InMemoryAppointmentRepository([]),
    )

    report = service.segment()

    assert report.total_patients == 1
    assert report.cohorts[0].frequency_bucket == "Sin citas registradas"
    assert report.cohorts[0].age_segment == "Edad desconocida"
    assert report.cohorts[0].sexo == "No declarado"
