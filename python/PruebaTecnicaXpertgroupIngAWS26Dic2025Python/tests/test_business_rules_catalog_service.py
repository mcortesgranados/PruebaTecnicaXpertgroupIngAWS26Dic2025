from src.core.services import BusinessRulesCatalogService


def test_business_rules_catalog_contains_critical_entries():
    service = BusinessRulesCatalogService()
    catalog = service.define_catalog()

    ids = {rule.id for rule in catalog.rules}
    assert "rule-estado" in ids
    assert "rule-edad-especialidad" in ids
    assert "rule-email-format" in ids
    assert "rule-phone-format" in ids
    assert catalog.rules[0].details["valid_states"]
