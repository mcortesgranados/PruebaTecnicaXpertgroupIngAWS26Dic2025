"""Servicio que registra auditorías de limpieza masiva."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from ..models import CleaningAuditEntry, CleaningAuditReport, FieldResponsibility


class CleaningAuditService:
    def __init__(self, responsibilities: List[FieldResponsibility]):
        self._responsibilities = self._index_responsibilities(responsibilities)

    def register_changes(self, change_events: List[Dict[str, str]]) -> CleaningAuditReport:
        entries: List[CleaningAuditEntry] = []
        for event in change_events:
            key = (event["table"], event["field"])
            resp = self._responsibilities.get(key)
            owner = resp.owner if resp else "No asignado"
            contact = resp.contact if resp else "Sin contacto"
            entries.append(
                CleaningAuditEntry(
                    table=event["table"],
                    field=event["field"],
                    action=event["action"],
                    user=event["user"],
                    timestamp=event.get("timestamp") or datetime.utcnow().isoformat(),
                    owner=owner,
                    contact=contact,
                    note=event.get("note", ""),
                )
            )

        return CleaningAuditReport(
            generated_at=datetime.utcnow().isoformat(),
            entries=entries,
        )

    @staticmethod
    def _index_responsibilities(resps: List[FieldResponsibility]) -> Dict[tuple, FieldResponsibility]:
        return {(resp.table, resp.field): resp for resp in resps}
