"""
Servicio que compila reportes ejecutivos y simula envío a gobernanza.
Utiliza anotaciones diferidas para referencias de tipo; `json` para serializar y deserializar cargas JSON; `datetime` para calculos y validaciones de fechas; `pathlib.Path` para manejar rutas multiplataforma; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ..models import ExecutiveDiscrepancyEntry, ExecutiveDiscrepancyReport


class ExecutiveDiscrepancyService:
    """
    Representa ejecutivo discrepancia servicio y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    CHANNEL = "gobernanza@hospital.local"
    DEFINITION = [
        {
            "category": "Referencialidad",
            "description": "Pacientes huérfanos detectados en citas_medicas.",
            "severity": "high",
            "source": "referential_integrity_log.json",
            "path": "summary.orphan_citas",
        },
        {
            "category": "Alertas de agenda",
            "description": "Citas sin médico/fecha detectadas.",
            "severity": "high",
            "source": "appointment_alerts_log.json",
            "path": "summary.alerts",
        },
        {
            "category": "Revisión ejecutiva",
            "description": "Citas completadas/canceladas sin datos críticos.",
            "severity": "medium",
            "source": "appointment_review_log.json",
            "path": "summary.reviewed_citas",
        },
        {
            "category": "Anomalías de costos",
            "description": "Citas con costos fuera de rango (>2σ).",
            "severity": "medium",
            "source": "appointment_cost_audit_log.json",
            "path": "anomalies",
        },
        {
            "category": "Reprogramaciones",
            "description": "Citas con múltiples reprogramaciones.",
            "severity": "medium",
            "source": "reports/appointment_state_timeline_log.json",
            "path": "summary.reprogrammed_citas",
        },
    ]

    def __init__(self, report_dir: Path):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.report_dir = report_dir

    def compile(self) -> ExecutiveDiscrepancyReport:
        """
        Encapsula compile, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        entries: List[ExecutiveDiscrepancyEntry] = []
        for definition in self.DEFINITION:
            path = self.report_dir / definition["source"]
            count = self._read_value(path, definition["path"])
            if count < 1:
                continue
            entries.append(
                ExecutiveDiscrepancyEntry(
                    category=definition["category"],
                    description=definition["description"],
                    count=count,
                    severity=definition["severity"],
                    source=str(path.name),
                )
            )

        return ExecutiveDiscrepancyReport(
            generated_at=datetime.utcnow().isoformat(),
            channel=self.CHANNEL,
            entries=entries,
        )

    @staticmethod
    def _read_value(path: Path, path_expr: str) -> int:
        """
        Encapsula read value, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        if not path.exists():
            return 0
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return 0
        for part in path_expr.split("."):
            if isinstance(data, list) and part.isdigit():
                idx = int(part)
                data = data[idx] if idx < len(data) else {}
            else:
                data = data.get(part, {})
            if data == {}:
                break
        if isinstance(data, list):
            return len(data)
        if isinstance(data, dict):
            return 0
        return int(data or 0)
