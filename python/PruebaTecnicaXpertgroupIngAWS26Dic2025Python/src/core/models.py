"""
Modulo encargado de modelos.
Utiliza anotaciones diferidas para referencias de tipo; `dataclasses` para estructurar modelos de datos; `datetime` para calculos y validaciones de fechas; `enum` para definir categorias con nombre; `typing` para contratos explicitos.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple


class PatientCategory(str, Enum):
    """
    Representa paciente categoria y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    CHILD = "child"
    ADULT = "adult"
    SENIOR = "senior"
    UNKNOWN = "unknown"


@dataclass
class PatientRecord:
    """
    Representa paciente Record y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_paciente: int
    nombre: str
    fecha_nacimiento: Optional[str]
    edad: Optional[int]
    sexo: Optional[str]
    email: Optional[str]
    telefono: Optional[str]
    ciudad: Optional[str] = None
    categoria: PatientCategory = PatientCategory.UNKNOWN

    @staticmethod
    def from_dict(source: Dict[str, Optional[str]]) -> "PatientRecord":
        """
        Encapsula from dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

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
    """
    Encapsula categorize paciente age, manteniendo Single Responsibility y
    dejando el contrato abierto para nuevas versiones (Open/Closed) mientras
    depende de abstracciones (Dependency Inversion).
    """

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
    """
    Encapsula categorize by value, manteniendo Single Responsibility y
    dejando el contrato abierto para nuevas versiones (Open/Closed) mientras
    depende de abstracciones (Dependency Inversion).
    """

    if age_years < 18:
        return PatientCategory.CHILD
    if age_years < 65:
        return PatientCategory.ADULT
    return PatientCategory.SENIOR


@dataclass
class CompletenessMetric:
    """
    Representa completitud Metric y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    field: str
    total: int
    missing: int
    completeness: float
    per_city_missing: Dict[str, float] = field(default_factory=dict)
    per_category_missing: Dict[str, float] = field(default_factory=dict)


@dataclass
class ImputationPlan:
    """
    Representa Imputation Plan y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    field: str
    strategy: str
    rationale: str


@dataclass
class AgeCorrectionLogEntry:
    """
    Representa Age Correction Log entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_paciente: int
    nombre: str
    fecha_nacimiento: Optional[str]
    edad_registrada: Optional[int]
    edad_calculada: Optional[int]
    action: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

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
    """
    Representa Age Consistency informe y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    cutoff_date: date
    total_records: int
    inconsistencies: int
    imputations: int
    missing_birthdate_records: int
    log_entries: List[AgeCorrectionLogEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

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
    """
    Representa duplicado Consolidation Log entrada y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    canonical_id: int
    canonical_nombre: str
    criteria: str
    duplicate_ids: List[int]
    note: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "canonical_id": self.canonical_id,
            "canonical_nombre": self.canonical_nombre,
            "criteria": self.criteria,
            "duplicate_ids": self.duplicate_ids,
            "note": self.note,
        }


@dataclass
class DuplicateConsolidationReport:
    """
    Representa duplicado Consolidation informe y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    total_records: int
    total_groups: int
    total_duplicates: int
    log_entries: List[DuplicateConsolidationLogEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

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
    """
    Representa texto normalizacion entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_paciente: int
    field: str
    original_value: Optional[str]
    normalized_value: Optional[str]
    method: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_paciente": self.id_paciente,
            "field": self.field,
            "original_value": self.original_value,
            "normalized_value": self.normalized_value,
            "method": self.method,
        }


@dataclass
class TextNormalizationReport:
    """
    Representa texto normalizacion informe y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    total_records: int
    normalized_fields: Dict[str, int]
    log_entries: List[TextNormalizationEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_records": self.total_records,
                "normalized_fields": self.normalized_fields,
            },
            "entries": [entry.to_dict() for entry in self.log_entries],
        }


@dataclass
class AppointmentRecord:
    """
    Representa cita Record y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_cita: str
    id_paciente: int
    fecha_cita: Optional[str]
    especialidad: Optional[str]
    medico: Optional[str]
    costo: Optional[float]
    estado_cita: Optional[str]
    ciudad: Optional[str] = None

    @staticmethod
    def from_dict(source: Dict[str, Any]) -> "AppointmentRecord":
        """
        Encapsula from dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return AppointmentRecord(
            id_cita=source["id_cita"],
            id_paciente=source.get("id_paciente"),
            fecha_cita=source.get("fecha_cita"),
            especialidad=source.get("especialidad"),
            medico=source.get("medico"),
            costo=source.get("costo"),
            estado_cita=source.get("estado_cita"),
            ciudad=source.get("ciudad") or source.get("ciudad_cita"),
        )


@dataclass
class AppointmentIndicatorEntry:
    """
    Representa cita Indicator entrada y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    period_type: str  # 'daily' or 'weekly'
    period_value: str  # YYYY-MM-DD or YYYY-WW
    especialidad: str
    estado_cita: str
    medico: str
    count: int

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "period_type": self.period_type,
            "period_value": self.period_value,
            "especialidad": self.especialidad,
            "estado_cita": self.estado_cita,
            "medico": self.medico,
            "count": self.count,
        }


@dataclass
class AppointmentIndicatorReport:
    """
    Representa cita Indicator informe y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    total_records: int
    missing_date: int
    entries: List[AppointmentIndicatorEntry] = field(default_factory=list)
    bottlenecks: List[AppointmentIndicatorEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_records": self.total_records,
                "missing_date": self.missing_date,
            },
            "entries": [entry.to_dict() for entry in self.entries],
            "bottlenecks": [entry.to_dict() for entry in self.bottlenecks],
        }


@dataclass
class AppointmentAlertEntry:
    """
    Representa cita Alert entrada y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_cita: str
    id_paciente: Optional[int]
    falta_fecha: bool
    falta_medico: bool
    especialidad: Optional[str]
    note: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_cita": self.id_cita,
            "id_paciente": self.id_paciente,
            "falta_fecha": self.falta_fecha,
            "falta_medico": self.falta_medico,
            "especialidad": self.especialidad,
            "note": self.note,
        }


@dataclass
class AppointmentAlertReport:
    """
    Representa cita Alert informe y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    total_records: int
    alerts: int
    entries: List[AppointmentAlertEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_records": self.total_records,
                "alerts": self.alerts,
            },
            "alerts": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class SpecialtyCostSummary:
    """
    Representa Specialty costo Summary y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    especialidad: str
    count: int
    average: float
    std_dev: float

    @property
    def expected_min(self) -> float:
        """
        Encapsula expected min, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return self.average - 2 * self.std_dev

    @property
    def expected_max(self) -> float:
        """
        Encapsula expected max, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return self.average + 2 * self.std_dev

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "especialidad": self.especialidad,
            "count": self.count,
            "average": round(self.average, 2),
            "std_dev": round(self.std_dev, 2),
            "expected_range": {
                "min": round(self.expected_min, 2),
                "max": round(self.expected_max, 2),
            },
        }


@dataclass
class CostAnomalyEntry:
    """
    Representa costo Anomaly entrada y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_cita: str
    id_paciente: Optional[int]
    especialidad: str
    costo: Optional[float]
    deviation: float

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_cita": self.id_cita,
            "id_paciente": self.id_paciente,
            "especialidad": self.especialidad,
            "costo": self.costo,
            "deviation": round(self.deviation, 2),
        }


@dataclass
class CostAuditReport:
    """
    Representa costo auditoria informe y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    total_records: int
    analyzed_records: int
    summaries: List[SpecialtyCostSummary] = field(default_factory=list)
    anomalies: List[CostAnomalyEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_records": self.total_records,
                "analyzed_records": self.analyzed_records,
            },
            "summaries": [entry.to_dict() for entry in self.summaries],
            "anomalies": [entry.to_dict() for entry in self.anomalies],
        }


@dataclass
class AppointmentStateHistoryEntry:
    """
    Representa cita estado History entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_cita: str
    transitions: List[Tuple[str, Optional[str]]]  # (status, fecha)
    doctors: List[str]
    reprogram_count: int
    final_estado: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_cita": self.id_cita,
            "transitions": [
                {"estado": estado, "fecha": fecha} for estado, fecha in self.transitions
            ],
            "doctors": self.doctors,
            "reprogram_count": self.reprogram_count,
            "final_estado": self.final_estado,
        }


@dataclass
class OccupancyImpactEntry:
    """
    Representa ocupacion Impact entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    medico: str
    week: str
    reprograms: int
    affected_citas: int

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "medico": self.medico,
            "week": self.week,
            "reprograms": self.reprograms,
            "affected_citas": self.affected_citas,
        }


@dataclass
class AppointmentStateTimelineReport:
    """
    Representa cita estado linea de tiempo informe y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    total_citas: int
    reprogrammed_citas: int
    entries: List[AppointmentStateHistoryEntry] = field(default_factory=list)
    occupancy_impacts: List[OccupancyImpactEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_citas": self.total_citas,
                "reprogrammed_citas": self.reprogrammed_citas,
            },
            "entries": [entry.to_dict() for entry in self.entries],
            "occupancy_impacts": [entry.to_dict() for entry in self.occupancy_impacts],
        }


@dataclass
class ReferentialIntegrityEntry:
    """
    Representa referencial integridad entrada y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    id_cita: str
    id_paciente: Optional[int]
    motivo: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_cita": self.id_cita,
            "id_paciente": self.id_paciente,
            "motivo": self.motivo,
        }


@dataclass
class ReferentialIntegrityReport:
    """
    Representa referencial integridad informe y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    total_citas: int
    orphan_citas: int
    entries: List[ReferentialIntegrityEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_citas": self.total_citas,
                "orphan_citas": self.orphan_citas,
            },
            "orphan_entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class AppointmentReviewEntry:
    """
    Representa cita revision entrada y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_cita: str
    estado_cita: Optional[str]
    fecha_cita: Optional[str]
    medico: Optional[str]
    issues: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_cita": self.id_cita,
            "estado_cita": self.estado_cita,
            "fecha_cita": self.fecha_cita,
            "medico": self.medico,
            "issues": self.issues,
        }


@dataclass
class AppointmentReviewReport:
    """
    Representa cita revision informe y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    total_citas: int
    reviewed_citas: int
    entries: List[AppointmentReviewEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_citas": self.total_citas,
                "reviewed_citas": self.reviewed_citas,
            },
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class AgeSpecialtyMismatchEntry:
    """
    Representa Age Specialty Mismatch entrada y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    id_cita: str
    id_paciente: Optional[int]
    especialidad: Optional[str]
    edad_calculada: Optional[int]
    expected_min: Optional[int]
    expected_max: Optional[int]
    note: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_cita": self.id_cita,
            "id_paciente": self.id_paciente,
            "especialidad": self.especialidad,
            "edad_calculada": self.edad_calculada,
            "expected_min": self.expected_min,
            "expected_max": self.expected_max,
            "note": self.note,
        }


@dataclass
class AgeSpecialtyMismatchReport:
    """
    Representa Age Specialty Mismatch informe y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    total_citas: int
    flagged_citas: int
    entries: List[AgeSpecialtyMismatchEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_citas": self.total_citas,
                "flagged_citas": self.flagged_citas,
            },
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class AccessibilityEntry:
    """
    Representa accesibilidad entrada y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_paciente: int
    nombre: str
    residencia: Optional[str]
    appointment_cities: List[str]
    total_citas: int
    note: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_paciente": self.id_paciente,
            "nombre": self.nombre,
            "residencia": self.residencia,
            "appointment_cities": self.appointment_cities,
            "total_citas": self.total_citas,
            "note": self.note,
        }


@dataclass
class AccessibilityReport:
    """
    Representa accesibilidad informe y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    total_pacientes: int
    flagged: int
    entries: List[AccessibilityEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "summary": {
                "total_pacientes": self.total_pacientes,
                "flagged": self.flagged,
            },
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class PatientSegment:
    """
    Representa paciente Segment y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    age_segment: str
    sexo: str
    frequency_bucket: str
    count: int

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "age_segment": self.age_segment,
            "sexo": self.sexo,
            "frequency_bucket": self.frequency_bucket,
            "count": self.count,
        }


@dataclass
class PatientSegmentationReport:
    """
    Representa paciente segmentacion informe y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    generated_at: str
    total_patients: int
    cohorts: List[PatientSegment] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "total_patients": self.total_patients,
            "cohorts": [entry.to_dict() for entry in self.cohorts],
        }


@dataclass
class CitySpecialtyOccupancy:
    """
    Representa ciudad Specialty ocupacion y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    city: str
    specialty: str
    completed: int
    canceled: int
    reprogrammed: int

    @property
    def total(self) -> int:
        """
        Encapsula total, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return self.completed + self.canceled + self.reprogrammed

    @property
    def completion_rate(self) -> float:
        """
        Encapsula completion rate, manteniendo Single Responsibility y dejando
        el contrato abierto para nuevas versiones (Open/Closed) mientras depende
        de abstracciones (Dependency Inversion).
        """

        return (self.completed / self.total) if self.total else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "city": self.city,
            "specialty": self.specialty,
            "completed": self.completed,
            "canceled": self.canceled,
            "reprogrammed": self.reprogrammed,
            "total": self.total,
            "completion_rate": round(self.completion_rate, 3),
        }


@dataclass
class OccupancyDashboardReport:
    """
    Representa ocupacion tablero informe y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    total_appointments: int
    entries: List[CitySpecialtyOccupancy] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "total_appointments": self.total_appointments,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class DoctorNotificationEntry:
    """
    Representa medico notificacion entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    doctor: str
    id_paciente: int
    nombre: str
    patterns: List[str]
    severity: str
    appointment_dates: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "doctor": self.doctor,
            "id_paciente": self.id_paciente,
            "nombre": self.nombre,
            "patterns": self.patterns,
            "severity": self.severity,
            "appointment_dates": self.appointment_dates,
        }


@dataclass
class DoctorNotificationReport:
    """
    Representa medico notificacion informe y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    total_alerts: int
    entries: List[DoctorNotificationEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "total_alerts": self.total_alerts,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class DoctorUtilizationEntry:
    """
    Representa medico utilizacion entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    doctor: str
    specialty: str
    completed: int
    scheduled: int
    utilization_rate: float
    cancellation_rate: float
    deviation: float
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "doctor": self.doctor,
            "specialty": self.specialty,
            "completed": self.completed,
            "scheduled": self.scheduled,
            "utilization_rate": round(self.utilization_rate, 3),
            "cancellation_rate": round(self.cancellation_rate, 3),
            "deviation": round(self.deviation, 3),
            "status": self.status,
        }


@dataclass
class DoctorUtilizationReport:
    """
    Representa medico utilizacion informe y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    threshold: float
    cancellation_threshold: float
    entries: List[DoctorUtilizationEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "threshold": self.threshold,
            "cancellation_threshold": self.cancellation_threshold,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class PatientTravelEntry:
    """
    Representa paciente viaje entrada y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_paciente: int
    nombre: str
    residence: str
    travel_cities: List[str]
    travel_count: int
    severity: str
    last_travel_dates: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_paciente": self.id_paciente,
            "nombre": self.nombre,
            "residence": self.residence,
            "travel_cities": self.travel_cities,
            "travel_count": self.travel_count,
            "severity": self.severity,
            "last_travel_dates": self.last_travel_dates,
        }


@dataclass
class PatientTravelReport:
    """
    Representa paciente viaje informe y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    total_travelers: int
    entries: List[PatientTravelEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "total_travelers": self.total_travelers,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class ManagementKpiEntry:
    """
    Representa gestion KPI entrada y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    specialty: str
    appointment_count: int
    average_cost: float
    average_wait_days: float

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "specialty": self.specialty,
            "appointment_count": self.appointment_count,
            "average_cost": round(self.average_cost, 2),
            "average_wait_days": round(self.average_wait_days, 2),
        }


@dataclass
class ManagementKpiReport:
    """
    Representa gestion KPI informe y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    overall_average_cost: float
    overall_average_wait_days: float
    specialty_entries: List[ManagementKpiEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "overall_average_cost": round(self.overall_average_cost, 2),
            "overall_average_wait_days": round(self.overall_average_wait_days, 2),
            "specialty_entries": [entry.to_dict() for entry in self.specialty_entries],
        }


@dataclass
class DemandForecastEntry:
    """
    Representa demanda pronostico entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    doctor: str
    specialty: str
    month: str
    predicted_demand: int
    capacity: int
    gap: int

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "doctor": self.doctor,
            "specialty": self.specialty,
            "month": self.month,
            "predicted_demand": self.predicted_demand,
            "capacity": self.capacity,
            "gap": self.gap,
        }


@dataclass
class DemandForecastReport:
    """
    Representa demanda pronostico informe y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    avg_monthly_growth: float
    months_ahead: int
    future_months: List[str] = field(default_factory=list)
    total_capacity: int = 0
    entries: List[DemandForecastEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "avg_monthly_growth": round(self.avg_monthly_growth, 4),
            "months_ahead": self.months_ahead,
            "future_months": self.future_months,
            "total_capacity": self.total_capacity,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class CancellationRiskEntry:
    """
    Representa Cancellation Risk entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id_cita: str
    id_paciente: Optional[int]
    especialidad: Optional[str]
    estado_cita: Optional[str]
    risk_score: float
    days_since_last: Optional[int]
    factors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id_cita": self.id_cita,
            "id_paciente": self.id_paciente,
            "especialidad": self.especialidad,
            "estado_cita": self.estado_cita,
            "risk_score": round(self.risk_score, 3),
            "days_since_last": self.days_since_last,
            "factors": self.factors,
        }


@dataclass
class CancellationRiskReport:
    """
    Representa Cancellation Risk informe y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    total_records: int
    high_risk_count: int
    average_risk: float
    specialty_risk: Dict[str, float] = field(default_factory=dict)
    entries: List[CancellationRiskEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "total_records": self.total_records,
            "high_risk_count": self.high_risk_count,
            "average_risk": round(self.average_risk, 4),
            "specialty_risk": {k: round(v, 4) for k, v in self.specialty_risk.items()},
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class FieldQualityMetric:
    """
    Representa Field calidad Metric y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    field: str
    completeness: float
    uniqueness: float
    format_valid: float

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "field": self.field,
            "completeness": round(self.completeness * 100, 2),
            "uniqueness": round(self.uniqueness * 100, 2),
            "format_validity": round(self.format_valid * 100, 2),
        }


@dataclass
class TableQualityMetrics:
    """
    Representa Table calidad Metrics y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    table_name: str
    before: List[FieldQualityMetric] = field(default_factory=list)
    after: List[FieldQualityMetric] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "table_name": self.table_name,
            "before": [metric.to_dict() for metric in self.before],
            "after": [metric.to_dict() for metric in self.after],
        }


@dataclass
class QualityKpiReport:
    """
    Representa calidad KPI informe y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    tables: List[TableQualityMetrics] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "tables": [table.to_dict() for table in self.tables],
        }


@dataclass
class BusinessRule:
    """
    Representa negocio Rule y mantiene Single Responsibility para ese
    concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    id: str
    title: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "details": self.details,
        }


@dataclass
class BusinessRulesCatalog:
    """
    Representa negocio reglas catalogo y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    created_at: str
    rules: List[BusinessRule] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "created_at": self.created_at,
            "rules": [rule.to_dict() for rule in self.rules],
        }


@dataclass
class FieldResponsibility:
    """
    Representa Field Responsibility y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    table: str
    field: str
    owner: str
    contact: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "table": self.table,
            "field": self.field,
            "owner": self.owner,
            "contact": self.contact,
            "notes": self.notes,
        }


@dataclass
class CleaningAuditEntry:
    """
    Representa limpieza auditoria entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    table: str
    field: str
    action: str
    user: str
    timestamp: str
    owner: str
    contact: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "table": self.table,
            "field": self.field,
            "action": self.action,
            "user": self.user,
            "timestamp": self.timestamp,
            "owner": self.owner,
            "contact": self.contact,
            "note": self.note,
        }


@dataclass
class CleaningAuditReport:
    """
    Representa limpieza auditoria informe y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    entries: List[CleaningAuditEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class ExecutiveDiscrepancyEntry:
    """
    Representa ejecutivo discrepancia entrada y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    category: str
    description: str
    count: int
    severity: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "category": self.category,
            "description": self.description,
            "count": self.count,
            "severity": self.severity,
            "source": self.source,
        }


@dataclass
class ExecutiveDiscrepancyReport:
    """
    Representa ejecutivo discrepancia informe y mantiene Single
    Responsibility para ese concepto del dominio, permitiendo extender el
    comportamiento sin modificar su contrato (Open/Closed) y apoyandose en
    abstracciones (Dependency Inversion).
    """

    generated_at: str
    channel: str
    entries: List[ExecutiveDiscrepancyEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "channel": self.channel,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class FieldResponsibility:
    """
    Representa Field Responsibility y mantiene Single Responsibility para
    ese concepto del dominio, permitiendo extender el comportamiento sin
    modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    table: str
    field: str
    owner: str
    contact: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "table": self.table,
            "field": self.field,
            "owner": self.owner,
            "contact": self.contact,
            "notes": self.notes,
        }


@dataclass
class CleaningAuditEntry:
    """
    Representa limpieza auditoria entrada y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    table: str
    field: str
    action: str
    user: str
    timestamp: str
    owner: str
    contact: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "table": self.table,
            "field": self.field,
            "action": self.action,
            "user": self.user,
            "timestamp": self.timestamp,
            "owner": self.owner,
            "contact": self.contact,
            "note": self.note,
        }


@dataclass
class CleaningAuditReport:
    """
    Representa limpieza auditoria informe y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    generated_at: str
    entries: List[CleaningAuditEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Encapsula to dict, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        return {
            "generated_at": self.generated_at,
            "entries": [entry.to_dict() for entry in self.entries],
        }
