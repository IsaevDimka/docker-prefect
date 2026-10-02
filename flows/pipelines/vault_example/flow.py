from prefect import flow, get_run_logger, task

from libs.vault import load_secrets


@task
def read_secrets() -> dict[str, str]:
    return load_secrets()


@flow(name="vault-example")
def vault_example(required_keys: list[str] | None = None) -> list[str]:
    logger = get_run_logger()
    secrets = read_secrets()

    missing = sorted(set(required_keys or []) - secrets.keys())
    if missing:
        raise ValueError(f"missing secrets in vault: {missing}")

    # never log secret values, only keys
    logger.info("loaded secrets: %s", sorted(secrets))
    logger.info(secrets.get("greeting", "no greeting in vault"))
    return sorted(secrets)


if __name__ == "__main__":
    vault_example()
