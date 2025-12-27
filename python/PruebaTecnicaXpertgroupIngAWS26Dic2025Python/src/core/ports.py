from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from .models import CompletenessMetric, ImputationPlan, PatientRecord


class PatientRepository(ABC):
    @abstractmethod
    def list_patients(self) -> Iterable[PatientRecord]:
        """Devuelve todos los pacientes disponibles."""


class CompletenessReporter(ABC):
    @abstractmethod
    def export_metrics(self, metrics: List[CompletenessMetric]) -> None:
        """Persiste métricas de completitud para seguimiento."""


class ImputationStrategy(ABC):
    @abstractmethod
    def suggest(self, records: Iterable[PatientRecord]) -> List[ImputationPlan]:
        """Genera sugerencias de imputación para campos incompletos."""
