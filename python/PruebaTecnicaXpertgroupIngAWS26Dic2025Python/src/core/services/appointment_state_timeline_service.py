"""Servicio para consolidar histórico de estados y reprogramaciones."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, Iterable, List, Tuple

from ..models import (
    AppointmentStateHistoryEntry,
    AppointmentStateTimelineReport,
    AppointmentRecord,
    OccupancyImpactEntry,
)
from ..ports import AppointmentRepository


class AppointmentStateTimelineService:
    def __init__(self, repository: AppointmentRepository):
        self.repository = repository

    def analyze(self) -> AppointmentStateTimelineReport:
        records = list(self.repository.list_appointments())
        grouped = self._group_by_id(records)
        entries: List[AppointmentStateHistoryEntry] = []
        reprogrammed_count = 0
        occupancy: Dict[Tuple[str, str], Dict[str, set | int]] = defaultdict(lambda: {"reprograms": 0, "citas": set()})

        for id_cita, group in grouped.items():
            sorted_group = sorted(group, key=lambda item: self._sort_key(item))
            transitions: List[Tuple[str, str | None]] = []
            doctors = []
            reprogram_count = 0

            for record in sorted_group:
                status = (record.estado_cita or "sin_estado").strip()
                parsed_date = self._parse_date(record.fecha_cita)
                date_display = parsed_date.isoformat() if parsed_date else None
                transitions.append((status, date_display))
                if status.lower().startswith("reprogram"):
                    reprogram_count += 1
                    doctor = self._normalize_doctor(record.medico)
                    if doctor and parsed_date:
                        week = f"{parsed_date.isocalendar()[0]}-W{parsed_date.isocalendar()[1]:02d}"
                        key = (doctor, week)
                        occupancy[key]["reprograms"] += 1
                        occupancy[key]["citas"].add(id_cita)
                if record.medico:
                    normalized = self._normalize_doctor(record.medico)
                    if normalized and normalized not in doctors:
                        doctors.append(normalized)

            final_status = transitions[-1][0] if transitions else "sin_estado"
            if reprogram_count > 0:
                reprogrammed_count += 1

            entries.append(
                AppointmentStateHistoryEntry(
                    id_cita=id_cita,
                    transitions=transitions,
                    doctors=doctors,
                    reprogram_count=reprogram_count,
                    final_estado=final_status,
                )
            )

        occupancy_impacts = [
            OccupancyImpactEntry(
                medico=medico,
                week=week,
                reprograms=data["reprograms"],
                affected_citas=len(data["citas"]),
            )
            for (medico, week), data in occupancy.items()
        ]
        occupancy_impacts.sort(key=lambda entry: (-entry.reprograms, entry.medico, entry.week))

        return AppointmentStateTimelineReport(
            total_citas=len(grouped),
            reprogrammed_citas=reprogrammed_count,
            entries=entries,
            occupancy_impacts=occupancy_impacts,
        )

    @staticmethod
    def _group_by_id(records: Iterable[AppointmentRecord]) -> Dict[str, List[AppointmentRecord]]:
        grouped: Dict[str, List[AppointmentRecord]] = defaultdict(list)
        for record in records:
            grouped[record.id_cita].append(record)
        return grouped

    @staticmethod
    def _sort_key(record: AppointmentRecord) -> Tuple[datetime, int]:
        parsed = AppointmentStateTimelineService._parse_date(record.fecha_cita)
        sort_date = parsed or datetime.min
        return sort_date, hash(record.id_cita)

    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _normalize_doctor(value: str | None) -> str | None:
        if not value:
            return None
        normalized = " ".join(value.split())
        return normalized
