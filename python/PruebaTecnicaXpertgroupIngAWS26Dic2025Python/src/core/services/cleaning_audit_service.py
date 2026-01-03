"""
Servicio que registra auditorías de limpieza masiva.
Utiliza anotaciones diferidas para referencias de tipo; `datetime` para calculos y validaciones de fechas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from ..models import CleaningAuditEntry, CleaningAuditReport, FieldResponsibility


class CleaningAuditService:
    """
    Representa limpieza auditoria servicio y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    def __init__(self, responsibilities: List[FieldResponsibility]):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self._responsibilities = self._index_responsibilities(responsibilities)

    def register_changes(self, change_events: List[Dict[str, str]]) -> CleaningAuditReport:
        """
        Encapsula register changes, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

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
        """
        Encapsula index responsibilities, manteniendo Single Responsibility y
        dejando el contrato abierto para nuevas versiones (Open/Closed) mientras
        depende de abstracciones (Dependency Inversion).
        """

        return {(resp.table, resp.field): resp for resp in resps}
