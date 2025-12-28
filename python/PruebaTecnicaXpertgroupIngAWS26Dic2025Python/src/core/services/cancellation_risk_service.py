"""Servicio para estimar la probabilidad de cancelación basada en historial."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from math import exp
from typing import Dict, List, Optional

from ..models import CancellationRiskEntry, CancellationRiskReport
from ..ports import AppointmentRepository


class CancellationRiskService:
    _specialty_weights: Dict[str, float] = {
        "pediatría": 0.4,
        "geriatría": 0.3,
        "cardiología": 0.35,
        "cirugía": 0.25,
        "general": 0.2,
    }
    _risk_threshold = 0.6

    def __init__(self, appointment_repo: AppointmentRepository):
        self.appointment_repo = appointment_repo

    def analyze(self) -> CancellationRiskReport:
        appointments = sorted(
            list(self.appointment_repo.list_appointments()),
            key=self._sort_key,
        )
        patient_history: Dict[int, Dict[str, Optional[datetime]]] = {}
        entries: List[CancellationRiskEntry] = []
        total = 0
        high_risk = 0
        specialty_acc: Dict[str, List[float]] = defaultdict(list)

        for appointment in appointments:
            total += 1
            specialty_label = self._normalize_specialty(appointment.especialidad)
            prev = (
                patient_history.get(appointment.id_paciente)
                if appointment.id_paciente is not None
                else None
            )
            days_since_last = (
                self._compute_days_between(prev["last_date"], appointment.fecha_cita)
                if prev and prev.get("last_date")
                else None
            )
            score, factors = self._score_appointment(
                appointment,
                prev_status=prev.get("last_status") if prev else None,
                days_since_last=days_since_last,
                specialty=specialty_label,
            )
            if score >= self._risk_threshold:
                high_risk += 1
            entries.append(
                CancellationRiskEntry(
                    id_cita=appointment.id_cita,
                    id_paciente=appointment.id_paciente,
                    especialidad=specialty_label,
                    estado_cita=appointment.estado_cita,
                    risk_score=score,
                    days_since_last=days_since_last,
                    factors=factors,
                )
            )
            specialty_acc[specialty_label].append(score)
            if appointment.id_paciente is not None:
                patient_history[appointment.id_paciente] = {
                    "last_status": appointment.estado_cita,
                    "last_date": self._parse_date(appointment.fecha_cita),
                }

        sorted_entries = sorted(entries, key=lambda entry: entry.risk_score, reverse=True)
        top_entries = sorted_entries[:20]
        avg_risk = sum(entry.risk_score for entry in entries) / max(total, 1)
        specialty_summary = {
            spec: sum(scores) / len(scores) if scores else 0.0
            for spec, scores in specialty_acc.items()
        }

        return CancellationRiskReport(
            generated_at=datetime.utcnow().isoformat(),
            total_records=total,
            high_risk_count=high_risk,
            average_risk=avg_risk,
            specialty_risk=specialty_summary,
            entries=top_entries,
        )

    def _score_appointment(
        self,
        appointment,
        *,
        prev_status: Optional[str],
        days_since_last: Optional[int],
        specialty: str,
    ) -> tuple[float, List[str]]:
        weight = -1.2
        factors: List[str] = []

        if prev_status:
            normalized = prev_status.strip().lower()
            if normalized == "cancelada":
                weight += 1.1
                factors.append("Cancelación previa")
            if normalized == "reprogramada":
                weight += 0.6
                factors.append("Reprogramada previa")
        if days_since_last is not None:
            if days_since_last <= 3:
                weight += 0.9
                factors.append("Intervalo corto (<4 días)")
            elif days_since_last <= 7:
                weight += 0.4
                factors.append("Intervalo ajustado (<8 días)")
        if appointment.estado_cita and appointment.estado_cita.strip().lower() == "cancelada":
            weight += 1.4
            factors.append("Estado actual Cancelada")
        specialty_weight = self._specialty_weights.get(specialty.lower(), 0.1)
        weight += specialty_weight
        if specialty_weight > 0:
            factors.append(f"Especialidad: {specialty.title()}")

        score = self._sigmoid(weight)
        return score, factors

    def _compute_days_between(self, previous: datetime, current_str: Optional[str]) -> Optional[int]:
        current = self._parse_date(current_str)
        if not current or not previous:
            return None
        delta = current - previous
        return max(delta.days, 0)

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1 / (1 + exp(-value))

    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @classmethod
    def _normalize_specialty(cls, specialty: Optional[str]) -> str:
        if not specialty:
            return "General"
        return specialty.strip().lower()

    def _sort_key(self, appointment) -> tuple:
        date = self._parse_date(appointment.fecha_cita) or datetime.min
        pid = appointment.id_paciente if appointment.id_paciente is not None else -1
        return (pid, date)
