"""Servicio para identificar y documentar duplicados potenciales."""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from ..models import DuplicateConsolidationLogEntry, DuplicateConsolidationReport, PatientRecord
from ..ports import PatientRepository


class DuplicateDetectionService:
    def __init__(self, repository: PatientRepository):
        self.repository = repository

    def detect_duplicates(self) -> DuplicateConsolidationReport:
        records = list(self.repository.list_patients())
        log_entries: List[DuplicateConsolidationLogEntry] = []
        total_groups = 0
        total_duplicates = 0
        archived_ids = set()

        criteria_set = [
            ("nombre+fecha_nacimiento", self._key_by_birthdate),
            ("nombre+ciudad", self._key_by_city),
        ]

        for criteria_name, key_fn in criteria_set:
            grouped = self._group_by(records, key_fn)
            for key, group in grouped.items():
                if len(group) < 2:
                    continue
                canonical, others = self._select_canonical(group)
                new_duplicates = [
                    r
                    for r in others
                    if r.id_paciente != canonical.id_paciente and r.id_paciente not in archived_ids
                ]
                if not new_duplicates:
                    continue
                archived_ids.update(r.id_paciente for r in new_duplicates)
                total_groups += 1
                total_duplicates += len(new_duplicates)
                log_entries.append(
                    DuplicateConsolidationLogEntry(
                        canonical_id=canonical.id_paciente,
                        canonical_nombre=canonical.nombre,
                        criteria=criteria_name,
                        duplicate_ids=[r.id_paciente for r in new_duplicates],
                        note=(
                            "Se identificaron registros con el mismo nombre y "
                            f"{'fecha de nacimiento' if 'fecha' in criteria_name else 'ciudad'} y "
                            "se archivaron los ids reemplazados."
                        ),
                    )
                )

        return DuplicateConsolidationReport(
            total_records=len(records),
            total_groups=total_groups,
            total_duplicates=total_duplicates,
            log_entries=log_entries,
        )

    def _group_by(
        self, records: Iterable[PatientRecord], key_fn: Callable[[PatientRecord], Optional[Tuple[str, str]]]
    ) -> Dict[Tuple[str, str], List[PatientRecord]]:
        groups: Dict[Tuple[str, str], List[PatientRecord]] = defaultdict(list)
        for record in records:
            key = key_fn(record)
            if key is None:
                continue
            groups[key].append(record)
        return groups

    @staticmethod
    def _select_canonical(group: List[PatientRecord]) -> Tuple[PatientRecord, List[PatientRecord]]:
        sorted_group = sorted(group, key=lambda r: (-DuplicateDetectionService._completeness_score(r), r.id_paciente))
        canonical = sorted_group[0]
        others = sorted_group[1:]
        return canonical, others

    @staticmethod
    def _completeness_score(record: PatientRecord) -> int:
        score = 0
        for attr in ("fecha_nacimiento", "edad", "sexo", "email", "telefono", "ciudad"):
            value = getattr(record, attr)
            if value:
                score += 1
        return score

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.split()).lower()

    @classmethod
    def _key_by_birthdate(cls, record: PatientRecord) -> Optional[Tuple[str, str]]:
        if not record.nombre or not record.fecha_nacimiento:
            return None
        return cls._normalize(record.nombre), record.fecha_nacimiento

    @classmethod
    def _key_by_city(cls, record: PatientRecord) -> Optional[Tuple[str, str]]:
        if not record.nombre or not record.ciudad:
            return None
        return cls._normalize(record.nombre), cls._normalize(record.ciudad)
