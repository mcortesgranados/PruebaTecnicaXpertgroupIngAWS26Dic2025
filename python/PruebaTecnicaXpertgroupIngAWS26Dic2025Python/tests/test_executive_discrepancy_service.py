import json
from pathlib import Path

from src.core.services import ExecutiveDiscrepancyService


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_compile_reads_all_definition_sources(tmp_path):
    report_dir = tmp_path

    _write(
        report_dir / "referential_integrity_log.json",
        {"summary": {"orphan_citas": 5}, "orphan_entries": []},
    )
    _write(
        report_dir / "appointment_alerts_log.json",
        {"summary": {"alerts": 3}, "alerts": []},
    )
    _write(
        report_dir / "appointment_review_log.json",
        {"summary": {"reviewed_citas": 2}, "entries": []},
    )
    _write(
        report_dir / "appointment_cost_audit_log.json",
        {"summary": {"analyzed_records": 10}, "anomalies": [{"id_cita": "C1"}, {"id_cita": "C2"}]},
    )
    nested = report_dir / "reports"
    _write(
        nested / "appointment_state_timeline_log.json",
        {"summary": {"reprogrammed_citas": 4}, "entries": []},
    )

    service = ExecutiveDiscrepancyService(report_dir)
    report = service.compile()

    assert report.channel == ExecutiveDiscrepancyService.CHANNEL
    assert len(report.entries) == 5
    counts = {entry.category: entry.count for entry in report.entries}
    assert counts["Referencialidad"] == 5
    assert counts["Alertas de agenda"] == 3
    assert counts["Revisión ejecutiva"] == 2
    assert counts["Anomalías de costos"] == 2
    assert counts["Reprogramaciones"] == 4


def test_compile_ignores_missing_sources(tmp_path):
    report = ExecutiveDiscrepancyService(tmp_path).compile()
    assert report.entries == []
