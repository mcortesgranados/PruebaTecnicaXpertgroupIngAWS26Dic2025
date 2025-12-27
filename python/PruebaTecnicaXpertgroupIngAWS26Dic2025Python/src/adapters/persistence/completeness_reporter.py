import json
from pathlib import Path
from typing import List

from ...core.models import CompletenessMetric
from ...core.ports import CompletenessReporter


class JsonCompletenessReporter(CompletenessReporter):
    def __init__(self, target: Path):
        self.target = target

    def export_metrics(self, metrics: List[CompletenessMetric]) -> None:
        payload = []
        for metric in metrics:
            payload.append(
                {
                    "field": metric.field,
                    "total": metric.total,
                    "missing": metric.missing,
                    "completeness_percentage": round(metric.completeness * 100, 2),
                    "per_city_missing": metric.per_city_missing,
                    "per_category_missing": metric.per_category_missing,
                }
            )
        with self.target.open("w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
