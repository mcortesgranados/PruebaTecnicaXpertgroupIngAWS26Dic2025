"""
Servicio para simular escenarios de demanda futura y brechas de capacidad.
Utiliza anotaciones diferidas para referencias de tipo; `collections` para contadores y agrupaciones; `datetime` para calculos y validaciones de fechas; `math` para funciones numericas auxiliares; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from math import ceil
from typing import Dict, List, Optional, Tuple

from ..models import DemandForecastEntry, DemandForecastReport
from ..ports import AppointmentRepository


class DemandForecastService:
    """
    Representa demanda pronostico servicio y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    MONTHS_AHEAD = 3
    BASE_CAPACITY = 15

    def __init__(self, appointment_repo: AppointmentRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.appointment_repo = appointment_repo

    def forecast(self) -> DemandForecastReport:
        """
        Encapsula pronostico, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        monthly_totals: Dict[str, int] = defaultdict(int)
        doctor_month: Dict[Tuple[str, str], int] = defaultdict(int)
        doctor_specialty: Dict[str, str] = {}
        parsed_dates: List[datetime] = []

        for appointment in self.appointment_repo.list_appointments():
            date = self._parse_date(appointment.fecha_cita)
            if not date:
                continue
            parsed_dates.append(date)
            month_key = self._format_month(date)
            monthly_totals[month_key] += 1
            doctor = appointment.medico or "Sin médico"
            doctor_month[(doctor, month_key)] += 1
            doctor_specialty[doctor] = appointment.especialidad or "General"

        if not parsed_dates:
            return DemandForecastReport(
                generated_at=datetime.utcnow().isoformat(),
                avg_monthly_growth=0.0,
                months_ahead=self.MONTHS_AHEAD,
            )

        sorted_months = sorted(monthly_totals.keys())
        avg_growth = self._compute_avg_growth(sorted_months, monthly_totals)
        last_month = sorted_months[-1]
        future_months = self._build_future_months(last_month, self.MONTHS_AHEAD)

        entries: List[DemandForecastEntry] = []
        for doctor in doctor_specialty.keys():
            last_count = doctor_month.get((doctor, last_month), 0)
            capacity = max(int(round(last_count * 1.2)), self.BASE_CAPACITY)
            specialty = doctor_specialty.get(doctor, "General")
            for idx, month in enumerate(future_months, start=1):
                predicted = int(round(last_count * ((1 + avg_growth) ** idx))) if last_count else 0
                gap = predicted - capacity
                entries.append(
                    DemandForecastEntry(
                        doctor=doctor,
                        specialty=specialty,
                        month=month,
                        predicted_demand=predicted,
                        capacity=capacity,
                        gap=gap,
                    )
                )

        sorted_entries = sorted(entries, key=lambda entry: entry.predicted_demand, reverse=True)
        total_capacity = sum(entry.capacity for entry in sorted_entries)

        return DemandForecastReport(
            generated_at=datetime.utcnow().isoformat(),
            avg_monthly_growth=avg_growth,
            months_ahead=len(future_months),
            future_months=future_months,
            total_capacity=total_capacity,
            entries=sorted_entries,
        )

    @staticmethod
    def _parse_date(value: Optional[str]) -> Optional[datetime]:
        """
        Encapsula parse date, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _format_month(value: datetime) -> str:
        """
        Encapsula format month, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return f"{value.year}-{value.month:02d}"

    @staticmethod
    def _build_future_months(last_month: str, count: int) -> List[str]:
        """
        Encapsula build future months, manteniendo Single Responsibility y
        dejando el contrato abierto para nuevas versiones (Open/Closed) mientras
        depende de abstracciones (Dependency Inversion).
        """

        year, month = map(int, last_month.split("-"))
        months: List[str] = []
        for _ in range(count):
            month += 1
            if month > 12:
                year += 1
                month = 1
            months.append(f"{year}-{month:02d}")
        return months

    def _compute_avg_growth(self, months: List[str], totals: Dict[str, int]) -> float:
        """
        Encapsula compute avg growth, manteniendo Single Responsibility y
        dejando el contrato abierto para nuevas versiones (Open/Closed) mientras
        depende de abstracciones (Dependency Inversion).
        """

        rates: List[float] = []
        for previous, current in zip(months, months[1:]):
            prev_value = totals.get(previous, 0)
            curr_value = totals.get(current, 0)
            if prev_value == 0:
                continue
            rates.append((curr_value - prev_value) / prev_value)
        return sum(rates) / len(rates) if rates else 0.0
