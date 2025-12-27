from src.core.models import FieldResponsibility
from src.core.services import CleaningAuditService


def test_cleaning_audit_assigns_responsibles():
    responsibilities = [
        FieldResponsibility(
            table="pacientes",
            field="email",
            owner="QA",
            contact="qa@example.com",
        )
    ]
    service = CleaningAuditService(responsibilities)
    report = service.register_changes(
        [
            {"table": "pacientes", "field": "email", "action": "Limpieza", "user": "qa_user"}
        ]
    )

    assert report.entries[0].owner == "QA"
    assert report.entries[0].contact == "qa@example.com"
