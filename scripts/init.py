"""Bootstrap the local Prefect environment.

1. Create the docker work pool `docker-pool`.
2. Put example secrets into Vault (kv v2, mount `secret`, path `prefect`).
3. Save the `VaultSecret` block named `vault`, which flows use to read secrets.

Vault in dev mode keeps data in memory, so the script is idempotent
and re-runs on every `docker compose up`.
"""

import asyncio
import os
import sys

from hvac.exceptions import InvalidPath
from prefect.client.orchestration import get_client
from prefect.client.schemas.actions import WorkPoolCreate
from prefect.exceptions import ObjectAlreadyExists
from prefect_docker.worker import DockerWorker
from prefect_vault import VaultSecret
from prefect_vault.auth import VaultToken

WORK_POOL_NAME = "docker-pool"
VAULT_BLOCK_NAME = "vault"
VAULT_MOUNT_POINT = "secret"
VAULT_SECRET_PATH = "prefect"  # noqa: S105

EXAMPLE_SECRETS = {
    "greeting": "Hello from Vault",
    "api_key": "dummy-api-key",
}


async def create_work_pool() -> None:
    async with get_client() as client:
        try:
            await client.create_work_pool(
                WorkPoolCreate(
                    name=WORK_POOL_NAME,
                    type=DockerWorker.type,
                    base_job_template=DockerWorker.get_default_base_job_template(),
                ),
            )
            print(f"work pool {WORK_POOL_NAME!r} created")
        except ObjectAlreadyExists:
            print(f"work pool {WORK_POOL_NAME!r} already exists")


def init_vault() -> None:
    vault_secret = VaultSecret(
        vault_auth=VaultToken(
            vault_url=os.environ["VAULT_ADDR"],
            token=os.environ["VAULT_TOKEN"],
        ),
    )

    try:
        existing = vault_secret.get_secret(VAULT_SECRET_PATH, mount_point=VAULT_MOUNT_POINT) or {}
    except InvalidPath:
        existing = {}

    # keep values that were set manually
    secrets = {**EXAMPLE_SECRETS, **existing}
    vault_secret.put_secret(path=VAULT_SECRET_PATH, secret=secrets, mount_point=VAULT_MOUNT_POINT)
    print(f"vault: {VAULT_MOUNT_POINT}/{VAULT_SECRET_PATH} keys={sorted(secrets)}")

    vault_secret.save(VAULT_BLOCK_NAME, overwrite=True)
    print(f"block VaultSecret/{VAULT_BLOCK_NAME!r} saved")


def main() -> int:
    asyncio.run(create_work_pool())
    init_vault()
    return 0


if __name__ == "__main__":
    sys.exit(main())
