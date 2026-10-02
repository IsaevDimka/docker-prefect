import os
from typing import Any

from prefect_vault import VaultSecret
from prefect_vault.auth import VaultToken


def load_secrets(
    path: str | None = None,
    mount_point: str | None = None,
    block_name: str | None = None,
) -> dict[str, Any]:
    """Read secrets from Vault (kv v2).

    If VAULT_ADDR and VAULT_TOKEN are set, connects to Vault directly (local run via
    `uv run python -m ...`); otherwise uses the VaultSecret block created by scripts/init.py.
    """
    path = path or os.getenv("VAULT_SECRET_PATH", "prefect")
    mount_point = mount_point or os.getenv("VAULT_MOUNT_POINT", "secret")
    block_name = block_name or os.getenv("VAULT_BLOCK", "vault")

    vault_addr, vault_token = os.getenv("VAULT_ADDR"), os.getenv("VAULT_TOKEN")
    if vault_addr and vault_token:
        vault_secret = VaultSecret(vault_auth=VaultToken(vault_url=vault_addr, token=vault_token))
    else:
        vault_secret = VaultSecret.load(block_name)

    return vault_secret.get_secret(path, mount_point=mount_point) or {}
