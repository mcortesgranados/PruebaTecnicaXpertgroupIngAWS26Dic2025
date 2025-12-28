from pathlib import Path
import json

import pandas as pd

from src.core.services import ETLPipelineService


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset_hospital 2 AWS.json"


def _run_pipeline(tmp_path: Path):
    service = ETLPipelineService(DATASET, tmp_path)
    summary = service.run()
    clean_dir = tmp_path / "etl"
    return summary, clean_dir


def test_etl_outputs_respect_cardinality_and_integrity(tmp_path: Path):
    summary, clean_dir = _run_pipeline(tmp_path)
    patients_csv = clean_dir / "pacientes_cleaned.csv"
    appointments_csv = clean_dir / "citas_cleaned.csv"

    patients = pd.read_csv(patients_csv, dtype=str)
    appointments = pd.read_csv(appointments_csv, dtype=str)

    assert len(patients) == summary["patients_exported"]
    assert len(appointments) == summary["appointments_exported"]
    assert not appointments["id_paciente"].isna().any()

    patient_ids = set(patients["id_paciente"])
    appointment_ids = set(appointments["id_paciente"])
    assert appointment_ids.issubset(patient_ids)

    expected_columns = {"id_paciente", "nombre", "ciudad", "email", "telefono", "sexo", "categoria"}
    assert expected_columns.issubset(set(patients.columns))


def test_etl_formats_are_valid(tmp_path: Path):
    _, clean_dir = _run_pipeline(tmp_path)
    appointments_csv = clean_dir / "citas_cleaned.csv"
    appointments = pd.read_csv(appointments_csv, dtype=str)

    parsed_dates = pd.to_datetime(appointments["fecha_cita"], errors="coerce")
    assert not parsed_dates.isna().any()

    normalized_status = appointments["estado_cita"].fillna("").astype(str).str.lower()
    allowed = {"completada", "cancelada", "reprogramada", "programada", ""}
    assert normalized_status.isin(allowed).all()


def test_metrics_are_appended_with_every_run(tmp_path: Path):
    dataset = tmp_path / "tiny_dataset.json"
    payload = {
        "pacientes": [
            {"id_paciente": 100, "nombre": "Test", "ciudad": "X", "email": "t@t.com", "sexo": "M"}
        ],
        "citas_medicas": [
            {
                "id_cita": "X1",
                "id_paciente": 100,
                "fecha_cita": "2025-03-01",
                "estado_cita": "Completada",
                "especialidad": "General",
                "medico": "Dr. Test",
            }
        ],
    }
    dataset.write_text(json.dumps(payload), encoding="utf-8")

    service = ETLPipelineService(dataset, tmp_path)
    summary = service.run()
    metrics_path = tmp_path / "etl" / "etl_metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert isinstance(metrics, list)
    assert metrics[-1]["patients"] == summary["patients_exported"]
    assert metrics[-1]["appointments"] == summary["appointments_exported"]
    # Run again to ensure we append
    summary2 = service.run()
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert len(metrics) == 2
    assert metrics[-1]["patients"] == summary2["patients_exported"]
