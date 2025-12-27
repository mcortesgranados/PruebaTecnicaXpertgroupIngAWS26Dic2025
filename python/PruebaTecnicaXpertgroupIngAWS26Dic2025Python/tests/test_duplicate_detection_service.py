from src.core.models import PatientCategory, PatientRecord
from src.core.services import DuplicateDetectionService
from src.core.ports import PatientRepository


class DummyRepository(PatientRepository):
    def __init__(self, patients):
        self._patients = patients

    def list_patients(self):
        return iter(self._patients)


def test_duplicate_detection_identifies_groups_and_archives_ids():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre="Ana Pérez",
            fecha_nacimiento="1990-01-01",
            edad=35,
            sexo="Female",
            email="ana@example.com",
            telefono="111",
            ciudad="Bogotá",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Ana Pérez",
            fecha_nacimiento="1990-01-01",
            edad=34,
            sexo="Female",
            email=None,
            telefono=None,
            ciudad="Bogotá",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=3,
            nombre="Ana Pérez",
            fecha_nacimiento="1992-05-10",
            edad=33,
            sexo="Female",
            email="ana3@example.com",
            telefono="333",
            ciudad="Bogotá",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=4,
            nombre="Carlos Gómez",
            fecha_nacimiento="1980-02-02",
            edad=45,
            sexo="Male",
            email="carlos@example.com",
            telefono="444",
            ciudad="Medellín",
            categoria=PatientCategory.ADULT,
        ),
    ]

    service = DuplicateDetectionService(DummyRepository(patients))
    report = service.detect_duplicates()

    assert report.total_records == 4
    assert report.total_groups == 2
    assert report.total_duplicates == 2
    assert len(report.log_entries) == 2

    birthdate_entry = next(entry for entry in report.log_entries if entry.criteria == "nombre+fecha_nacimiento")
    city_entry = next(entry for entry in report.log_entries if entry.criteria == "nombre+ciudad")

    assert birthdate_entry.canonical_id == 1
    assert birthdate_entry.duplicate_ids == [2]

    assert city_entry.canonical_id == 1
    assert city_entry.duplicate_ids == [3]
