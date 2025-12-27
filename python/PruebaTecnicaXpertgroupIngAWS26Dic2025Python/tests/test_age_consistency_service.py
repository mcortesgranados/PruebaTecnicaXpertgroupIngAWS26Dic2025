from datetime import date

from src.core.models import PatientCategory, PatientRecord
from src.core.services import AgeConsistencyService
from src.core.ports import PatientRepository


class DummyRepository(PatientRepository):
    def __init__(self, patients):
        self._patients = patients

    def list_patients(self):
        return iter(self._patients)


def test_age_consistency_service_captures_inconsistencies_and_imputations():
    records = [
        PatientRecord(
            id_paciente=1,
            nombre="Paciente consistente",
            fecha_nacimiento="2000-01-01",
            edad=25,
            sexo="Female",
            email="consistent@example.com",
            telefono="111",
            ciudad="Bogotá",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Paciente inconsistente",
            fecha_nacimiento="1990-06-01",
            edad=20,
            sexo="Male",
            email=None,
            telefono=None,
            ciudad="Medellín",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=3,
            nombre="Paciente sin edad",
            fecha_nacimiento="1988-12-31",
            edad=None,
            sexo="Female",
            email=None,
            telefono="123",
            ciudad="Cali",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=4,
            nombre="Paciente sin fecha ni edad",
            fecha_nacimiento=None,
            edad=None,
            sexo=None,
            email=None,
            telefono=None,
            ciudad=None,
            categoria=PatientCategory.UNKNOWN,
        ),
    ]

    service = AgeConsistencyService(DummyRepository(records))
    report = service.audit_ages(date(2025, 12, 31))

    assert report.total_records == 4
    assert report.inconsistencies == 1
    assert report.imputations == 1
    assert report.missing_birthdate_records == 1
    assert len(report.log_entries) == 3

    entry_by_id = {entry.id_paciente: entry for entry in report.log_entries}

    inconsistent_entry = entry_by_id[2]
    assert inconsistent_entry.action == "inconsistent_age"
    assert inconsistent_entry.edad_calculada == 35

    imputed_entry = entry_by_id[3]
    assert imputed_entry.action == "imputed_age"
    assert imputed_entry.edad_calculada == 37

    missing_entry = entry_by_id[4]
    assert missing_entry.action == "missing_birthdate"
    assert missing_entry.edad_calculada is None
