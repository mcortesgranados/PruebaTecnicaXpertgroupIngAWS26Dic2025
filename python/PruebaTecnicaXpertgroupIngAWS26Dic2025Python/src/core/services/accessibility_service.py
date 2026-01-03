"""
Servicio que cruza citas por paciente con su ciudad de residencia para detectar viajes.
Utiliza anotaciones diferidas para referencias de tipo; `collections` para contadores y agrupaciones; `statistics` para metricas agregadas; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""


from __future__ import annotations

from collections import defaultdict
from statistics import mean, pstdev
from typing import Dict, List, Optional

from ..models import AccessibilityEntry, AccessibilityReport
from ..ports import AppointmentRepository, PatientRepository


class AccessibilityService:
    """
    Representa accesibilidad servicio y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    def __init__(self, patient_repo: PatientRepository, appointment_repo: AppointmentRepository):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.patient_repo = patient_repo
        self.appointment_repo = appointment_repo

    def evaluate(self) -> AccessibilityReport:
        """
        Encapsula evaluate, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        patients = {p.id_paciente: p for p in self.patient_repo.list_patients()}
        appointments = list(self.appointment_repo.list_appointments())
        patient_cities: Dict[int, List[str]] = defaultdict(list)
        patient_counts: Dict[int, int] = defaultdict(int)

        for appointment in appointments:
            pid = appointment.id_paciente
            if pid is None:
                continue
            patient_counts[pid] += 1

        city_counts: Dict[str, List[int]] = defaultdict(list)
        patient_city_map: Dict[int, Optional[str]] = {}

        for patient in patients.values():
            city = (patient.ciudad or "").strip().lower()
            patient_city_map[patient.id_paciente] = city or None
            if patient_counts.get(patient.id_paciente):
                city_counts[city or "sin_ciudad"].append(patient_counts[patient.id_paciente])

        entries: List[AccessibilityEntry] = []
        all_counts = [count for count in patient_counts.values() if count > 0]
        overall_avg = mean(all_counts) if all_counts else 0
        overall_std = pstdev(all_counts) if len(all_counts) > 1 else 0
        for patient_id, patient in patients.items():
            count = patient_counts.get(patient_id, 0)
            if count == 0:
                continue
            residence = patient_city_map.get(patient_id)
            if residence is None:
                city_key = "sin_ciudad"
            else:
                city_key = residence
            stats = city_counts.get(city_key)
            note = "Paciente examinado sin desviaciones"
            flag = False
            if stats and len(stats) >= 2:
                avg = mean(stats)
                deviation = pstdev(stats)
                threshold = avg + 2 * deviation
                if deviation > 0 and count > threshold:
                    flag = True
                    note = "Paciente con volumen de citas superior al promedio local"
            else:
                if overall_std > 0 and count >= overall_avg + overall_std:
                    flag = True
                    note = "Paciente destaca por número de citas vs pares locales"

            if not flag:
                continue

            entries.append(
                AccessibilityEntry(
                    id_paciente=patient_id,
                    nombre=patient.nombre,
                    residencia=patient.ciudad,
                    appointment_cities=[],
                    total_citas=count,
                    note=note,
                )
            )

        entries.sort(key=lambda entry: (-entry.total_citas, entry.nombre))
        return AccessibilityReport(
            total_pacientes=len(patients),
            flagged=len(entries),
            entries=entries,
        )
