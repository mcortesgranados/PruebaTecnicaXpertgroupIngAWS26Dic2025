from pathlib import Path

from src.core.services import ETLPipelineService


class _DummyPath(Path):  # type: ignore[assignment]
    pass


def test_transform_cleans_text_and_prunes_orphans(tmp_path):
    service = ETLPipelineService(tmp_path / "dataset.json", tmp_path)
    patients = [
        {"id_paciente": 1, "nombre": " ana ", "ciudad": "bogotá", "email": "A@Example.COM", "sexo": "f"},
    ]
    appointments = [
        {"id_cita": "C1", "id_paciente": 1, "fecha_cita": "2025-01-01", "estado_cita": "Completada", "especialidad": "Pediatría", "medico": "dr. p"},
        {"id_cita": "C2", "id_paciente": 2, "fecha_cita": "2025-01-05", "estado_cita": "Cancelada", "especialidad": "General", "medico": "dr. g"},
        {"id_cita": "C3", "id_paciente": 1, "fecha_cita": "invalid date", "estado_cita": "Completada", "especialidad": "General", "medico": "dr. g"},
    ]

    patients_df, appointments_df, summary = service.transform(patients, appointments)

    assert summary["patients_raw"] == 1
    assert summary["appointments_raw"] == 3
    assert summary["orphans"] == ["C2"]
    assert appointments_df["id_cita"].tolist() == ["C1"]
    assert patients_df.iloc[0]["nombre"] == "Ana"
    assert patients_df.iloc[0]["email"] == "a@example.com"
