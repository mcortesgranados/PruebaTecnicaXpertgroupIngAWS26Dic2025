"""Servicio para medir indicadores de citas por especialidad, estado y médico."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Iterable, Tuple

from ..models import (
    AppointmentIndicatorEntry,
    AppointmentIndicatorReport,
    AppointmentRecord,
)
from ..ports import AppointmentRepository


class AppointmentIndicatorService:
    def __init__(self, repository: AppointmentRepository):
        self.repository = repository

    def measure_indicators(self) -> AppointmentIndicatorReport:
        records = list(self.repository.list_appointments())
        daily_counts: Counter = Counter()
        weekly_counts: Counter = Counter()
        missing_dates = 0

        for record in records:
            parsed = self._parse_date(record.fecha_cita)
            if not parsed:
                missing_dates += 1
                continue

            day_key = self._compose_key(parsed.strftime("%Y-%m-%d"), record)
            iso_year, iso_week, _ = parsed.isocalendar()
            week_key = self._compose_key(f"{iso_year}-W{iso_week:02d}", record)
            daily_counts[day_key] += 1
            weekly_counts[week_key] += 1

        entries = self._build_entries("daily", daily_counts)
        entries.extend(self._build_entries("weekly", weekly_counts))
        bottlenecks = sorted(entries, key=lambda entry: entry.count, reverse=True)[:5]

        return AppointmentIndicatorReport(
            total_records=len(records),
            missing_date=missing_dates,
            entries=entries,
            bottlenecks=bottlenecks,
        )

    def _compose_key(self, period: str, record: AppointmentRecord) -> Tuple[str, str, str, str]:
        return (
            period,
            self._safe(record.especialidad, "sin_especialidad"),
            self._safe(record.estado_cita, "sin_estado"),
            self._safe(record.medico, "sin_medico"),
        )

    @staticmethod
    def _safe(value: str | None, fallback: str) -> str:
        if value and isinstance(value, str) and value.strip():
            return value.strip()
        return fallback

    @staticmethod
    def _parse_date(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    def _build_entries(
        self, period_type: str, counter: Counter
    ) -> Iterable[AppointmentIndicatorEntry]:
        entries = []
        for (period, especialidad, estado, medico), count in counter.items():
            entries.append(
                AppointmentIndicatorEntry(
                    period_type=period_type,
                    period_value=period,
                    especialidad=especialidad,
                    estado_cita=estado,
                    medico=medico,
                    count=count,
                )
            )
        entries.sort(key=lambda entry: (entry.period_value, entry.especialidad, entry.estado_cita, entry.medico))
        return entries
