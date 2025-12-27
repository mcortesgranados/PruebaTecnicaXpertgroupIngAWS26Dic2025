from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Iterable, List, Optional


class PatientCategory(str, Enum):
    CHILD = "child"
    ADULT = "adult"
    SENIOR = "senior"
    UNKNOWN = "unknown"


@dataclass
class PatientRecord:
    id_paciente: int
    nombre: str
    fecha_nacimiento: Optional[str]
    edad: Optional[int]
    sexo: Optional[str]
    email: Optional[str]
    telefono: Optional[str]
    ciudad: Optional[str]
    categoria: PatientCategory = PatientCategory.UNKNOWN

    @staticmethod
    def from_dict(source: Dict[str, Optional[str]]) -> "PatientRecord":
        edad_value = source.get("edad")
        category = categorize_patient_age(edad_value, source.get("fecha_nacimiento"))
        return PatientRecord(
            id_paciente=source["id_paciente"],
            nombre=source.get("nombre") or "",
            fecha_nacimiento=source.get("fecha_nacimiento"),
            edad=edad_value,
            sexo=source.get("sexo"),
            email=source.get("email"),
            telefono=source.get("telefono"),
            ciudad=source.get("ciudad"),
            categoria=category,
        )


def categorize_patient_age(age: Optional[int], birthdate: Optional[str]) -> PatientCategory:
    if isinstance(age, int):
        return categorize_by_value(age)
    if birthdate:
        try:
            fecha = datetime.fromisoformat(birthdate)
            delta = datetime.utcnow().year - fecha.year
            return categorize_by_value(delta)
        except ValueError:
            pass
    return PatientCategory.UNKNOWN


def categorize_by_value(age_years: int) -> PatientCategory:
    if age_years < 18:
        return PatientCategory.CHILD
    if age_years < 65:
        return PatientCategory.ADULT
    return PatientCategory.SENIOR


@dataclass
class CompletenessMetric:
    field: str
    total: int
    missing: int
    completeness: float
    per_city_missing: Dict[str, float] = field(default_factory=dict)
    per_category_missing: Dict[str, float] = field(default_factory=dict)


@dataclass
class ImputationPlan:
    field: str
    strategy: str
    rationale: str
