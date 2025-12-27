from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple


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


@dataclass
class AppointmentRecord:
    id_cita: str
    id_paciente: int
    fecha_cita: Optional[str]
    especialidad: Optional[str]
    medico: Optional[str]
    costo: Optional[float]
    estado_cita: Optional[str]

    @staticmethod
    def from_dict(source: Dict[str, Any]) -> "AppointmentRecord":
        return AppointmentRecord(
            id_cita=source["id_cita"],
            id_paciente=source.get("id_paciente"),
            fecha_cita=source.get("fecha_cita"),
            especialidad=source.get("especialidad"),
            medico=source.get("medico"),
            costo=source.get("costo"),
            estado_cita=source.get("estado_cita"),
        )


@dataclass
class AppointmentIndicatorEntry:
    period_type: str  # 'daily' or 'weekly'
    period_value: str  # YYYY-MM-DD or YYYY-WW
    especialidad: str
    estado_cita: str
    medico: str
    count: int

    def to_dict(self) -> Dict[str, Any]:
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
    total_records: int
    missing_date: int
    entries: List[AppointmentIndicatorEntry] = field(default_factory=list)
    bottlenecks: List[AppointmentIndicatorEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
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
    id_cita: str
    id_paciente: Optional[int]
    falta_fecha: bool
    falta_medico: bool
    especialidad: Optional[str]
    note: str

    def to_dict(self) -> Dict[str, Any]:
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
    total_records: int
    alerts: int
    entries: List[AppointmentAlertEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "total_records": self.total_records,
                "alerts": self.alerts,
            },
            "alerts": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class SpecialtyCostSummary:
    especialidad: str
    count: int
    average: float
    std_dev: float

    @property
    def expected_min(self) -> float:
        return self.average - 2 * self.std_dev

    @property
    def expected_max(self) -> float:
        return self.average + 2 * self.std_dev

    def to_dict(self) -> Dict[str, Any]:
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
    id_cita: str
    id_paciente: Optional[int]
    especialidad: str
    costo: Optional[float]
    deviation: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_cita": self.id_cita,
            "id_paciente": self.id_paciente,
            "especialidad": self.especialidad,
            "costo": self.costo,
            "deviation": round(self.deviation, 2),
        }


@dataclass
class CostAuditReport:
    total_records: int
    analyzed_records: int
    summaries: List[SpecialtyCostSummary] = field(default_factory=list)
    anomalies: List[CostAnomalyEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
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
    id_cita: str
    transitions: List[Tuple[str, Optional[str]]]  # (status, fecha)
    doctors: List[str]
    reprogram_count: int
    final_estado: str

    def to_dict(self) -> Dict[str, Any]:
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
    medico: str
    week: str
    reprograms: int
    affected_citas: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "medico": self.medico,
            "week": self.week,
            "reprograms": self.reprograms,
            "affected_citas": self.affected_citas,
        }


@dataclass
class AppointmentStateTimelineReport:
    total_citas: int
    reprogrammed_citas: int
    entries: List[AppointmentStateHistoryEntry] = field(default_factory=list)
    occupancy_impacts: List[OccupancyImpactEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
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
    id_cita: str
    id_paciente: Optional[int]
    motivo: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_cita": self.id_cita,
            "id_paciente": self.id_paciente,
            "motivo": self.motivo,
        }


@dataclass
class ReferentialIntegrityReport:
    total_citas: int
    orphan_citas: int
    entries: List[ReferentialIntegrityEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "total_citas": self.total_citas,
                "orphan_citas": self.orphan_citas,
            },
            "orphan_entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class AppointmentReviewEntry:
    id_cita: str
    estado_cita: Optional[str]
    fecha_cita: Optional[str]
    medico: Optional[str]
    issues: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id_cita": self.id_cita,
            "estado_cita": self.estado_cita,
            "fecha_cita": self.fecha_cita,
            "medico": self.medico,
            "issues": self.issues,
        }


@dataclass
class AppointmentReviewReport:
    total_citas: int
    reviewed_citas: int
    entries: List[AppointmentReviewEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "total_citas": self.total_citas,
                "reviewed_citas": self.reviewed_citas,
            },
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class AgeSpecialtyMismatchEntry:
    id_cita: str
    id_paciente: Optional[int]
    especialidad: Optional[str]
    edad_calculada: Optional[int]
    expected_min: Optional[int]
    expected_max: Optional[int]
    note: str

    def to_dict(self) -> Dict[str, Any]:
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
    total_citas: int
    flagged_citas: int
    entries: List[AgeSpecialtyMismatchEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "total_citas": self.total_citas,
                "flagged_citas": self.flagged_citas,
            },
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class AccessibilityEntry:
    id_paciente: int
    nombre: str
    residencia: Optional[str]
    appointment_cities: List[str]
    total_citas: int
    note: str

    def to_dict(self) -> Dict[str, Any]:
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
    total_pacientes: int
    flagged: int
    entries: List[AccessibilityEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": {
                "total_pacientes": self.total_pacientes,
                "flagged": self.flagged,
            },
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class FieldQualityMetric:
    field: str
    completeness: float
    uniqueness: float
    format_valid: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "completeness": round(self.completeness * 100, 2),
            "uniqueness": round(self.uniqueness * 100, 2),
            "format_validity": round(self.format_valid * 100, 2),
        }


@dataclass
class TableQualityMetrics:
    table_name: str
    before: List[FieldQualityMetric] = field(default_factory=list)
    after: List[FieldQualityMetric] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_name": self.table_name,
            "before": [metric.to_dict() for metric in self.before],
            "after": [metric.to_dict() for metric in self.after],
        }


@dataclass
class QualityKpiReport:
    generated_at: str
    tables: List[TableQualityMetrics] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "tables": [table.to_dict() for table in self.tables],
        }


@dataclass
class BusinessRule:
    id: str
    title: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "details": self.details,
        }


@dataclass
class BusinessRulesCatalog:
    created_at: str
    rules: List[BusinessRule] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "created_at": self.created_at,
            "rules": [rule.to_dict() for rule in self.rules],
        }


@dataclass
class FieldResponsibility:
    table: str
    field: str
    owner: str
    contact: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table": self.table,
            "field": self.field,
            "owner": self.owner,
            "contact": self.contact,
            "notes": self.notes,
        }


@dataclass
class CleaningAuditEntry:
    table: str
    field: str
    action: str
    user: str
    timestamp: str
    owner: str
    contact: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
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
    generated_at: str
    entries: List[CleaningAuditEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class ExecutiveDiscrepancyEntry:
    category: str
    description: str
    count: int
    severity: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "description": self.description,
            "count": self.count,
            "severity": self.severity,
            "source": self.source,
        }


@dataclass
class ExecutiveDiscrepancyReport:
    generated_at: str
    channel: str
    entries: List[ExecutiveDiscrepancyEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "channel": self.channel,
            "entries": [entry.to_dict() for entry in self.entries],
        }


@dataclass
class FieldResponsibility:
    table: str
    field: str
    owner: str
    contact: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table": self.table,
            "field": self.field,
            "owner": self.owner,
            "contact": self.contact,
            "notes": self.notes,
        }


@dataclass
class CleaningAuditEntry:
    table: str
    field: str
    action: str
    user: str
    timestamp: str
    owner: str
    contact: str
    note: str

    def to_dict(self) -> Dict[str, Any]:
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
    generated_at: str
    entries: List[CleaningAuditEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "entries": [entry.to_dict() for entry in self.entries],
        }
