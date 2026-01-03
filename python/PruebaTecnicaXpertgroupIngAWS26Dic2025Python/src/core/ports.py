"""
Modulo encargado de puertos.
Utiliza anotaciones diferidas para referencias de tipo; `abc` para declarar contratos abstractos; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from .models import AppointmentRecord, CompletenessMetric, ImputationPlan, PatientRecord


class PatientRepository(ABC):
    @abstractmethod
    def list_patients(self) -> Iterable[PatientRecord]:
        """
        Encapsula list patients, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """



class AppointmentRepository(ABC):
    @abstractmethod
    def list_appointments(self) -> Iterable[AppointmentRecord]:
        """
        Encapsula list appointments, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """



class CompletenessReporter(ABC):
    @abstractmethod
    def export_metrics(self, metrics: List[CompletenessMetric]) -> None:
        """
        Encapsula export metrics, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """



class ImputationStrategy(ABC):
    @abstractmethod
    def suggest(self, records: Iterable[PatientRecord]) -> List[ImputationPlan]:
        """
        Encapsula suggest, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """
