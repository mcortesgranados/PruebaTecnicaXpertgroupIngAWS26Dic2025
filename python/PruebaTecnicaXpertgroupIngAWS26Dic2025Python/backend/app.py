from __future__ import annotations

import ast
import importlib
import json
import sys
from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_PATH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_PATH))

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from src.adapters.ingestion.json_appointment_repository import JsonAppointmentRepository
from src.adapters.ingestion.json_patient_repository import JsonPatientRepository
from src.core.services import (
    DoctorNotificationService,
    DoctorUtilizationService,
    ETLPipelineService,
    ManagementKpiService,
    PatientTravelService,
)

DATASET = BASE_PATH / "dataset_hospital 2 AWS.json"
REPORT_DIR = BASE_PATH / "reports"
SCRIPTS_DIR = BASE_PATH / "scripts"
SCRIPT_PREFIX = "run_"

app = FastAPI(title="Hospital Insights API", version="1.0")


def _service_runner(case: str) -> Dict[str, Any]:
    if case == "doctor-notifications":
        patient_repo = JsonPatientRepository(DATASET)
        appointment_repo = JsonAppointmentRepository(DATASET)
        report = DoctorNotificationService(patient_repo, appointment_repo).analyze()
    elif case == "doctor-utilization":
        appointment_repo = JsonAppointmentRepository(DATASET)
        report = DoctorUtilizationService(appointment_repo).analyze()
    elif case == "patient-travel":
        patient_repo = JsonPatientRepository(DATASET)
        appointment_repo = JsonAppointmentRepository(DATASET)
        report = PatientTravelService(patient_repo, appointment_repo).analyze()
    elif case == "management-kpis":
        appointment_repo = JsonAppointmentRepository(DATASET)
        report = ManagementKpiService(appointment_repo).report()
    elif case == "etl":
        report = ETLPipelineService(DATASET, REPORT_DIR).run()
    else:
        raise ValueError("Unknown case")
    return report if isinstance(report, dict) else report.to_dict()


def _get_json_path(name: str) -> Path:
    return REPORT_DIR / f"{name}.json"


@dataclass(frozen=True)
class ScriptDescriptor:
    key: str
    module_name: str
    path: Path
    description: str


class ScriptInfo(BaseModel):
    key: str
    module: str
    description: str
    path: str


class ScriptRunResponse(BaseModel):
    key: str
    module: str
    status: str
    output: str
    result: Optional[Any]


class DatasetUploadResponse(BaseModel):
    status: str
    path: str
    size: int


@app.get(
    "/health",
    summary="Check API health",
    description="Parameters: None. GET /health returns dataset path & status to confirm the API is running.",
)
def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "dataset": str(DATASET)})


@app.get(
    "/reports",
    summary="List JSON reports",
    description="Parameters: None. GET /reports returns all `.json` reports stored under the `reports` folder.",
)
def list_reports() -> JSONResponse:
    files = [p.name for p in REPORT_DIR.glob("*.json")]
    return JSONResponse({"reports": sorted(files)})


@app.get(
    "/reports/html",
    summary="List generated HTML reports",
    description="Parameters: None. GET /reports/html returns the filenames of every `.html` report under the `reports` folder.",
)
def list_html_reports() -> JSONResponse:
    files = [p.name for p in REPORT_DIR.glob("*.html")]
    return JSONResponse({"html_reports": sorted(files)})


@app.get(
    "/reports/{name}",
    summary="Fetch a report in JSON",
    description="Parameters:\n- `name` (path): report base filename without `.json`. GET /reports/{name} returns the parsed JSON content.",
)
def get_report(name: str) -> JSONResponse:
    path = _get_json_path(name)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    content = json.loads(path.read_text(encoding="utf-8"))
    return JSONResponse(content)


@app.get(
    "/reports/{name}/html",
    summary="Fetch report HTML",
    description="""Parameters:
- `name` (path): report base filename without `.html`. GET /reports/{name}/html streams the corresponding HTML file.
Available HTML reports include:
html_reports: [
  "accessibility_summary.html",
  "age_consistency_summary.html",
  "age_specialty_mismatch_summary.html",
  "appointment_alerts_summary.html",
  "appointment_cost_audit_summary.html",
  "appointment_indicators_summary.html",
  "appointment_review_summary.html",
  "appointment_state_timeline_summary.html",
  "business_rules_catalog.html",
  "cancellation_risk_summary.html",
  "cleaning_audit_summary.html",
  "completeness_summary.html",
  "demand_forecast_summary.html",
  "doctor_notifications_summary.html",
  "doctor_utilization_summary.html",
  "duplicate_detection_summary.html",
  "executive_discrepancies_summary.html",
  "management_kpis_summary.html",
  "occupancy_dashboard_summary.html",
  "patient_segmentation_summary.html",
  "patient_travel_summary.html",
  "quality_kpis_summary.html",
  "referential_integrity_summary.html",
  "text_normalization_summary.html"
]""",
)
def get_report_html(name: str):
    path = REPORT_DIR / f"{name}.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="HTML report not found")
    return FileResponse(path)


@app.post(
    "/run/{case}",
    summary="Run built-in service",
    description="Parameters:\n- `case` (path): one of `doctor-notifications`, `doctor-utilization`, `patient-travel`, `management-kpis`, `etl`. POST /run/{case} returns the summary generated by the service.",
)
def post_run(case: str) -> JSONResponse:
    try:
        summary = _service_runner(case)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return JSONResponse(summary)


@app.post(
    "/dataset/upload",
    summary="Upload dataset file",
    description="Parameters:\n- `file` (form): JSON file that replaces the current dataset.\nPOST /dataset/upload overwrites `dataset_hospital 2 AWS.json` so subsequent services operate on the new data.",
    response_model=DatasetUploadResponse,
)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetUploadResponse:
    if file.content_type != "application/json":
        raise HTTPException(status_code=415, detail="Dataset must be a JSON file")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded dataset cannot be empty")
    DATASET.write_bytes(content)
    return DatasetUploadResponse(
        status="replaced",
        path=str(DATASET.relative_to(BASE_PATH)),
        size=len(content),
    )


def _extract_docstring(script_path: Path) -> str:
    try:
        module_ast = ast.parse(script_path.read_text(encoding="utf-8"))
        doc = ast.get_docstring(module_ast)
        return doc.strip() if isinstance(doc, str) else ""
    except (SyntaxError, UnicodeDecodeError):
        return ""


def _discover_scripts() -> Dict[str, ScriptDescriptor]:
    if not SCRIPTS_DIR.exists():
        return {}
    scripts: Dict[str, ScriptDescriptor] = {}
    for path in sorted(SCRIPTS_DIR.glob("run_*.py")):
        normalized = path.stem
        if normalized.startswith(SCRIPT_PREFIX):
            normalized = normalized[len(SCRIPT_PREFIX) :]
        normalized = normalized.lower()
        description = _extract_docstring(path)
        scripts[normalized] = ScriptDescriptor(
            key=normalized,
            module_name=f"scripts.{path.stem}",
            path=path,
            description=description,
        )
    return scripts


SCRIPT_REGISTRY = _discover_scripts()


def _normalize_script_key(script_key: str) -> str:
    cleaned = script_key.replace("-", "_").strip().lower()
    if cleaned.startswith(SCRIPT_PREFIX):
        cleaned = cleaned[len(SCRIPT_PREFIX) :]
    return cleaned


def _resolve_script(script_key: str) -> ScriptDescriptor:
    normalized = _normalize_script_key(script_key)
    descriptor = SCRIPT_REGISTRY.get(normalized)
    if not descriptor:
        raise HTTPException(status_code=404, detail="Script not found")
    return descriptor


def _load_script_module(descriptor: ScriptDescriptor):
    try:
        module = importlib.import_module(descriptor.module_name)
        importlib.reload(module)
        return module
    except ImportError as exc:
        raise HTTPException(status_code=500, detail=f"Unable to import {descriptor.module_name}: {exc}")


@app.get(
    "/scripts",
    summary="List available scripts",
    description="Parameters: None. GET /scripts returns every script under `scripts/run_*.py` along with its description.",
    response_model=List[ScriptInfo],
)
def list_scripts() -> List[ScriptInfo]:
    return [
        ScriptInfo(
            key=descriptor.key,
            module=descriptor.module_name,
            description=descriptor.description or "No description available.",
            path=str(descriptor.path.relative_to(BASE_PATH)),
        )
        for descriptor in sorted(SCRIPT_REGISTRY.values(), key=lambda descriptor: descriptor.key)
    ]


@app.get(
    "/scripts/{script_key}",
    summary="Describe a script",
    description="Parameters:\n- `script_key` (path): normalized key derived from the filename after `run_`. GET /scripts/{script_key} returns metadata for that script.",
    response_model=ScriptInfo,
)
def get_script(script_key: str) -> ScriptInfo:
    descriptor = _resolve_script(script_key)
    return ScriptInfo(
        key=descriptor.key,
        module=descriptor.module_name,
        description=descriptor.description or "No description available.",
        path=str(descriptor.path.relative_to(BASE_PATH)),
    )


@app.post(
    "/scripts/{script_key}/run",
    summary="Execute a script",
    description="Parameters:\n- `script_key` (path): normalized key derived from the filename after `run_`. POST /scripts/{script_key}/run executes the module's `main()` and returns stdout/result.",
    response_model=ScriptRunResponse,
)
def run_script(script_key: str) -> ScriptRunResponse:
    descriptor = _resolve_script(script_key)
    module = _load_script_module(descriptor)
    if not hasattr(module, "main"):
        raise HTTPException(status_code=422, detail="Script does not expose a main() entry point")
    buffer = StringIO()
    try:
        with redirect_stdout(buffer):
            result = module.main()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=f"{descriptor.module_name} failed: {exc}") from exc
    return ScriptRunResponse(
        key=descriptor.key,
        module=descriptor.module_name,
        status="completed",
        output=buffer.getvalue().strip(),
        result=jsonable_encoder(result),
    )
