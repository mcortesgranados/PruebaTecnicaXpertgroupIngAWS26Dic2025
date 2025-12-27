from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional


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


@dataclass
class AgeCorrectionLogEntry:
    id_paciente: int
    nombre: str
    fecha_nacimiento: Optional[str]
    edad_registrada: Optional[int]
    edad_calculada: Optional[int]
    action: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_paciente": self.id_paciente,
            "nombre": self.nombre,
            "fecha_nacimiento": self.fecha_nacimiento,
            "edad_registrada": self.edad_registrada,
            "edad_calculada": self.edad_calculada,
            "action": self.action,
            "note": self.note,
        }


@dataclass
class AgeConsistencyReport:
    cutoff_date: date
    total_records: int
    inconsistencies: int
    imputations: int
    missing_birthdate_records: int
    log_entries: List[AgeCorrectionLogEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cutoff_date": self.cutoff_date.isoformat(),
            "summary": {
                "total_records": self.total_records,
                "inconsistencies": self.inconsistencies,
                "imputations": self.imputations,
                "missing_birthdate_records": self.missing_birthdate_records,
            },
            "changes": [entry.to_dict() for entry in self.log_entries],
        }


@dataclass
class DuplicateConsolidationLogEntry:
    canonical_id: int
    canonical_nombre: str
    criteria: str
    duplicate_ids: List[int]
    note: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "canonical_id": self.canonical_id,
            "canonical_nombre": self.canonical_nombre,
            "criteria": self.criteria,
            "duplicate_ids": self.duplicate_ids,
            "note": self.note,
        }


@dataclass
class DuplicateConsolidationReport:
    total_records: int
    total_groups: int
    total_duplicates: int
    log_entries: List[DuplicateConsolidationLogEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "total_records": self.total_records,
                "total_groups": self.total_groups,
                "total_duplicates": self.total_duplicates,
            },
            "groups": [entry.to_dict() for entry in self.log_entries],
        }


@dataclass
class TextNormalizationEntry:
    id_paciente: int
    field: str
    original_value: Optional[str]
    normalized_value: Optional[str]
    method: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_paciente": self.id_paciente,
            "field": self.field,
            "original_value": self.original_value,
            "normalized_value": self.normalized_value,
            "method": self.method,
        }


@dataclass
class TextNormalizationReport:
    total_records: int
    normalized_fields: Dict[str, int]
    log_entries: List[TextNormalizationEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "total_records": self.total_records,
                "normalized_fields": self.normalized_fields,
            },
            "entries": [entry.to_dict() for entry in self.log_entries],
        }
