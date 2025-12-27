from src.core.models import PatientCategory, PatientRecord
from src.core.services import TextNormalizationService
from src.core.ports import PatientRepository


class DummyRepository(PatientRepository):
    def __init__(self, patients):
        self._patients = patients

    def list_patients(self):
        return iter(self._patients)


def test_text_normalization_service_detects_diacritics_and_spaces():
    patients = [
        PatientRecord(
            id_paciente=1,
            nombre=" María López ",
            fecha_nacimiento="1985-01-01",
            edad=40,
            sexo="Female",
            email=None,
            telefono=None,
            ciudad=" Bogotá ",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Roberto Díaz",
            fecha_nacimiento="1990-05-05",
            edad=35,
            sexo="Male",
            email=None,
            telefono=None,
            ciudad=None,
            categoria=PatientCategory.ADULT,
        ),
    ]

    service = TextNormalizationService(DummyRepository(patients))
    report = service.normalize()

    assert report.total_records == 2
    assert report.normalized_fields["nombre"] == 2
    assert report.normalized_fields["ciudad"] == 1
    assert len(report.log_entries) == 3

    first_entry = next(entry for entry in report.log_entries if entry.id_paciente == 1 and entry.field == "nombre")
    assert first_entry.normalized_value == "maria lopez"
    assert "strip()" in first_entry.method
    assert "lower()" in first_entry.method
    city_entry = next(entry for entry in report.log_entries if entry.field == "ciudad")
    assert city_entry.normalized_value == "bogota"
