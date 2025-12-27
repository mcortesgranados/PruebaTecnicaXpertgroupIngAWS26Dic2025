import json
from pathlib import Path
from typing import Iterable

from ...core.models import AppointmentRecord
from ...core.ports import AppointmentRepository


class JsonAppointmentRepository(AppointmentRepository):
    def __init__(self, source: Path, dataset_key: str = "citas_medicas"):
        self.source = source
        self.dataset_key = dataset_key

    def list_appointments(self) -> Iterable[AppointmentRecord]:
        with self.source.open(encoding="utf-8") as stream:
            payload = json.load(stream)
            table = payload.get(self.dataset_key, [])
            for raw in table:
                yield AppointmentRecord.from_dict(raw)
