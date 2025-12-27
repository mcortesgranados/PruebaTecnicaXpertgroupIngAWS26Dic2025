"""Servicio que normaliza campos de texto críticos antes de los cruces."""

from __future__ import annotations

import unicodedata
from typing import Iterable, List, Optional

from ..models import PatientRecord, TextNormalizationEntry, TextNormalizationReport
from ..ports import PatientRepository


class TextNormalizationService:
    NORMALIZATION_METHOD = "strip() + lower() + remove_tildes"

    def __init__(self, repository: PatientRepository):
        self.repository = repository

    def normalize(self) -> TextNormalizationReport:
        records = list(self.repository.list_patients())
        log_entries: List[TextNormalizationEntry] = []
        normalized_counts = {"nombre": 0, "ciudad": 0}

        for record in records:
            changes = self._process_record(record)
            for entry in changes:
                log_entries.append(entry)
                normalized_counts[entry.field] += 1

        return TextNormalizationReport(
            total_records=len(records),
            normalized_fields=normalized_counts,
            log_entries=log_entries,
        )

    def _process_record(self, record: PatientRecord) -> List[TextNormalizationEntry]:
        entries: List[TextNormalizationEntry] = []
        for field in ("nombre", "ciudad"):
            original = getattr(record, field)
            normalized = self._normalize_text(original)
            if normalized is None:
                continue
            if original and normalized == original:
                continue

            entries.append(
                TextNormalizationEntry(
                    id_paciente=record.id_paciente,
                    field=field,
                    original_value=original,
                    normalized_value=normalized,
                    method=self.NORMALIZATION_METHOD,
                )
            )
        return entries

    @staticmethod
    def _normalize_text(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        cleaned = cleaned.strip().lower()
        normalized = unicodedata.normalize("NFKD", cleaned)
        without_tildes = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return without_tildes
