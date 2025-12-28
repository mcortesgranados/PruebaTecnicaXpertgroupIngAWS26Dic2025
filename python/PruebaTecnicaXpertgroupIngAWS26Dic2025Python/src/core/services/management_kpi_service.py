"""Servicio que genera KPIs ejecutivos para gerencia (espera y costo)."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import mean
from typing import Dict, List, Optional

from ..models import AppointmentRecord, ManagementKpiEntry, ManagementKpiReport
from ..ports import AppointmentRepository


class ManagementKpiService:
    def __init__(self, appointment_repo: AppointmentRepository):
        self.appointment_repo = appointment_repo

    def report(self) -> ManagementKpiReport:
        patient_timeline: Dict[int, List[AppointmentRecord]] = defaultdict(list)
        specialty_costs: Dict[str, List[float]] = defaultdict(list)
        specialty_waits: Dict[str, List[float]] = defaultdict(list)
        global_waits: List[float] = []
        global_costs: List[float] = []

        for appointment in self.appointment_repo.list_appointments():
            if appointment.fecha_cita:
                patient_timeline[appointment.id_paciente].append(appointment)
            cost = appointment.costo
            if cost is not None and appointment.estado_cita and appointment.estado_cita.strip().lower() == "completada":
                specialty = self._normalize_specialty(appointment.especialidad)
                specialty_costs[specialty].append(cost)
                global_costs.append(cost)

        for patient_id, appointments in patient_timeline.items():
            sorted_appts = sorted(
                appointments,
                key=lambda appt: self._parse_date(appt.fecha_cita) or datetime.min,
            )
            for prev, curr in zip(sorted_appts, sorted_appts[1:]):
                prev_date = self._parse_date(prev.fecha_cita)
                curr_date = self._parse_date(curr.fecha_cita)
                if prev_date and curr_date:
                    wait_hours = (curr_date - prev_date).days
                    if wait_hours >= 0:
                        global_waits.append(wait_hours)
                        specialty = self._normalize_specialty(curr.especialidad)
                        specialty_waits[specialty].append(wait_hours)

        entries: List[ManagementKpiEntry] = []
        for specialty in set(list(specialty_costs) + list(specialty_waits)):
            costs = specialty_costs.get(specialty, [])
            waits = specialty_waits.get(specialty, [])
            avg_cost = mean(costs) if costs else 0.0
            avg_wait = mean(waits) if waits else 0.0
            count = len(costs)
            entries.append(
                ManagementKpiEntry(
                    specialty=specialty,
                    appointment_count=count,
                    average_cost=avg_cost,
                    average_wait_days=avg_wait,
                )
            )

        overall_cost = mean(global_costs) if global_costs else 0.0
        overall_wait = mean(global_waits) if global_waits else 0.0

        return ManagementKpiReport(
            generated_at=datetime.utcnow().isoformat(),
            overall_average_cost=overall_cost,
            overall_average_wait_days=overall_wait,
            specialty_entries=sorted(entries, key=lambda e: e.specialty),
        )

    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _normalize_specialty(value: Optional[str]) -> str:
        if not value:
            return "General"
        return value.strip().title()
