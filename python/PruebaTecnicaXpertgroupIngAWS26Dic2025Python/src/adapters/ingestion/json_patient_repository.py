import json
from pathlib import Path
from typing import Iterable

from ...core.models import PatientRecord
from ...core.ports import PatientRepository


class JsonPatientRepository(PatientRepository):
    def __init__(self, source: Path, dataset_key: str = "pacientes"):
        self.source = source
        self.dataset_key = dataset_key

    def list_patients(self) -> Iterable[PatientRecord]:
        with self.source.open(encoding="utf-8") as stream:
            payload = json.load(stream)
            table = payload.get(self.dataset_key, [])
            for raw in table:
                yield PatientRecord.from_dict(raw)
