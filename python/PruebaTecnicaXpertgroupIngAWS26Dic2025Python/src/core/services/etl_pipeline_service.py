"""Servicio que ejecuta el pipeline ETL completo desde JSON hasta tablas limpias."""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd


class ETLPipelineService:
    def __init__(self, dataset_path: Path, report_dir: Path):
        self.dataset_path = dataset_path
        self.report_dir = report_dir

    def run(self) -> Dict[str, Any]:
        start_iso = datetime.utcnow().isoformat()
        start_clock = time.perf_counter()

        patients_raw, appointments_raw = self.extract()
        patients_df, appointments_df, summary = self.transform(patients_raw, appointments_raw)
        self.load(patients_df, appointments_df)

        summary["patients_exported"] = len(patients_df)
        summary["appointments_exported"] = len(appointments_df)
        end_iso = datetime.utcnow().isoformat()
        duration = time.perf_counter() - start_clock
        summary.update(
            {
                "start_time": start_iso,
                "end_time": end_iso,
                "duration_seconds": round(duration, 3),
            }
        )

        self._persist_metrics(summary)
        return summary

    def extract(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        with self.dataset_path.open(encoding="utf-8") as stream:
            payload = json.load(stream)
        patients = payload.get("pacientes", [])
        appointments = payload.get("citas_medicas", [])
        return patients, appointments

    def transform(
        self,
        patients: List[Dict[str, Any]],
        appointments: List[Dict[str, Any]],
    ) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, Any]]:
        patients_df = pd.DataFrame(patients)
        appointments_df = pd.DataFrame(appointments)

        patients_df = self._clean_patients(patients_df)
        appointments_df = self._clean_appointments(appointments_df)

        orphan_ids = []
        if not patients_df.empty and not appointments_df.empty:
            mask = ~appointments_df["id_paciente"].isin(patients_df["id_paciente"])
            orphan_ids = appointments_df.loc[mask, "id_cita"].fillna("N/A").tolist()
            appointments_df = appointments_df.loc[~mask]

        summary = {
            "patients_raw": len(patients),
            "appointments_raw": len(appointments),
            "orphans": orphan_ids,
        }
        return patients_df, appointments_df, summary

    def load(self, patients_df: pd.DataFrame, appointments_df: pd.DataFrame) -> None:
        clean_dir = self.report_dir / "etl"
        clean_dir.mkdir(parents=True, exist_ok=True)

        self._write_table(patients_df, clean_dir / "pacientes_cleaned.csv", clean_dir / "pacientes_cleaned.parquet")
        self._write_table(appointments_df, clean_dir / "citas_cleaned.csv", clean_dir / "citas_cleaned.parquet")

    def _write_table(self, df: pd.DataFrame, csv_path: Path, parquet_path: Path) -> None:
        df.to_csv(csv_path, index=False, encoding="utf-8")
        try:
            df.to_parquet(parquet_path, index=False)
        except ImportError:
            parquet_path.write_text("", encoding="utf-8")

    def _persist_metrics(self, summary: Dict[str, Any]) -> None:
        metrics_path = self.report_dir / "etl" / "etl_metrics.json"
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        existing: List[Dict[str, Any]] = []
        if metrics_path.exists():
            try:
                existing = json.loads(metrics_path.read_text(encoding="utf-8")) or []
            except json.JSONDecodeError:
                existing = []
        entry = {
            "start_time": summary["start_time"],
            "end_time": summary["end_time"],
            "duration_seconds": summary["duration_seconds"],
            "patients": summary["patients_exported"],
            "appointments": summary["appointments_exported"],
            "orphans": len(summary.get("orphans", [])),
        }
        existing.append(entry)
        metrics_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")

    def _clean_patients(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df["nombre"] = df["nombre"].fillna("").str.strip().str.title()
        df["ciudad"] = df["ciudad"].fillna("").str.strip().str.title()
        df["email"] = df["email"].fillna("").str.strip().str.lower()
        if "telefono" not in df.columns:
            df["telefono"] = ""
        df["telefono"] = df["telefono"].fillna("").str.strip()
        df["sexo"] = df["sexo"].fillna("").str.strip().str.title()
        if "categoria" not in df.columns:
            df["categoria"] = ""
        df["categoria"] = df["categoria"].fillna("").astype(str)
        return df

    def _clean_appointments(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df["estado_cita"] = df["estado_cita"].fillna("").str.strip().str.lower()
        df["especialidad"] = df["especialidad"].fillna("").str.strip().str.title()
        df["medico"] = df["medico"].fillna("").str.strip().str.title()
        df["fecha_cita"] = pd.to_datetime(df["fecha_cita"], errors="coerce")
        df = df.dropna(subset=["fecha_cita"])
        return df
