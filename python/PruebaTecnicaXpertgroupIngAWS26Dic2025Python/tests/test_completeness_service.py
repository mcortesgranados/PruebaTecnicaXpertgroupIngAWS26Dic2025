import pytest

from src.core.models import ImputationPlan, PatientCategory, PatientRecord
from src.core.services import CompletenessService
from src.core.ports import ImputationStrategy, PatientRepository


class DummyRepository(PatientRepository):
    def __init__(self, patients):
        self._patients = patients

    def list_patients(self):
        return iter(self._patients)


class DummyImputer(ImputationStrategy):
    def __init__(self):
        self.called = False

    def suggest(self, records):
        self.called = True
        return [
            ImputationPlan(
                field="email",
                strategy="usar plantilla",
                rationale="prueba",
            )
        ]


@pytest.fixture
def sample_patients():
    return [
        PatientRecord(
            id_paciente=1,
            nombre="Paciente 1",
            fecha_nacimiento="1990-01-01",
            edad=32,
            sexo="Female",
            email="user@example.com",
            telefono="123",
            ciudad="Bogota",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=2,
            nombre="Paciente 2",
            fecha_nacimiento="1985-01-01",
            edad=37,
            sexo="Male",
            email=None,
            telefono=None,
            ciudad="Medellin",
            categoria=PatientCategory.ADULT,
        ),
        PatientRecord(
            id_paciente=3,
            nombre="Paciente 3",
            fecha_nacimiento="2009-01-01",
            edad=13,
            sexo="Female",
            email=None,
            telefono="456",
            ciudad=None,
            categoria=PatientCategory.CHILD,
        ),
    ]


def test_completeness_metrics_and_plan(sample_patients):
    repo = DummyRepository(sample_patients)
    imputer = DummyImputer()
    service = CompletenessService(repo, imputer)

    metrics, plans = service.evaluate()

    assert imputer.called
    email_metric = next(m for m in metrics if m.field == "email")
    assert email_metric.total == 3
    assert email_metric.missing == 2
    assert email_metric.per_city_missing["Bogota"] == 0.0
    assert email_metric.per_city_missing["Medellin"] == 100.0
    assert len(plans) == 1
