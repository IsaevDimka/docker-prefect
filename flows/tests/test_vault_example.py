import pytest

from pipelines.vault_example import flow as vault_flow


@pytest.fixture
def fake_vault(monkeypatch):
    monkeypatch.setattr(
        vault_flow,
        "load_secrets",
        lambda: {"greeting": "Hello from test", "api_key": "secret"},
    )


def test_vault_example_returns_keys(fake_vault):
    assert vault_flow.vault_example() == ["api_key", "greeting"]


def test_vault_example_fails_on_missing_keys(fake_vault):
    with pytest.raises(ValueError, match="db_dsn"):
        vault_flow.vault_example(required_keys=["api_key", "db_dsn"])
