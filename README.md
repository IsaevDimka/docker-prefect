# docker-prefect

Local [Prefect 3](https://docs.prefect.io/v3/) stack in Docker: server + docker worker + Postgres + HashiCorp Vault,
with example flows, deployments via `prefect.yaml` and CI.

```shell
make init
```

| Service        | Image                                         | URL                                   |
|----------------|-----------------------------------------------|---------------------------------------|
| prefect-server | `prefecthq/prefect:3.8.7-python3.14`          | http://localhost:4200                 |
| prefect-worker | `prefect` + `prefect-docker`, `prefect-vault` | docker work pool `docker-pool`        |
| vault          | `hashicorp/vault:2.1.1` (dev mode)            | http://localhost:8200 (token `vault`) |
| postgres       | `postgres:18.6-alpine`                        | Prefect database                      |

## Requirements

* Docker
* [uv](https://docs.astral.sh/uv/) — only for running flow linters/tests locally

## How it works

```
make init
 ├─ flows-build      docker build flows/ -> docker-prefect-flows:local (flow code + dependencies)
 ├─ docker-up        postgres, vault, prefect-server
 │                   prefect-init (one-shot, scripts/init.py):
 │                     - work pool `docker-pool` (type docker)
 │                     - secrets in Vault: secret/prefect (kv v2)
 │                     - VaultSecret block `vault` in Prefect
 │                   prefect-worker — runs every flow run in its own container from the flows image
 └─ prefect-deploy   prefect deploy --all using flows/prefect.yaml
```

Flows read secrets via `libs/vault.py`: inside Prefect through the `VaultSecret` block (`vault`),
locally straight from Vault when `VAULT_ADDR` and `VAULT_TOKEN` are set.

Vault runs in dev mode and keeps data in memory: secrets are lost when the container restarts,
and `prefect-init` seeds them again on the next `docker compose up` (manually added keys are kept while Vault is up).

## Commands

```shell
make prefect-run DEPLOYMENT=hello/hello                   # run a deployment and wait for the result
make prefect-run DEPLOYMENT=vault-example/vault-example

make vault-get                                            # show secret/prefect
make vault-put KEY=api_key VALUE=xxx                      # add/update a key

make flows-build prefect-deploy                           # after changing flow code
make flows-lint flows-test                                # ruff + pytest (locally via uv)

make docker-stop / docker-start / docker-clear
```

## Adding a flow

1. Code goes to `flows/pipelines/<name>/flow.py`, tests to `flows/tests/`.
2. Add a deployment to `flows/prefect.yaml` (`work_pool: *work_pool`).
3. `make flows-build prefect-deploy`.

Run a flow locally without the docker worker:

```shell
cd flows
PREFECT_API_URL=http://localhost:4200/api VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=vault \
    uv run python -m pipelines.vault_example.flow
```

## CI

* `.github/workflows/ci.yml` — on PRs and pushes to `master`:
  * **quality** — `ruff` + `pytest` (Prefect test harness, no Docker);
  * **e2e** — `make init`, then real runs of `hello` and `vault-example` through the worker.
* `.github/workflows/release.yml` — on a `v*` tag builds a multi-arch flows image and pushes it to
  `ghcr.io/<owner>/docker-prefect-flows`.

## Not for production

Vault in dev mode with a root token, Postgres passwords and the token in `.env` are for local development only.
For a real environment: Vault in server mode with AppRole (`prefect_vault.auth.VaultAppRole`),
and secrets coming from CI / a secret store rather than the repository.
