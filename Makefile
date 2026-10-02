# suppress output, run `make XXX V=` to be verbose
V := @

THIS_FILE := $(lastword $(MAKEFILE_LIST))

include .env

PREFECT_CLI := docker compose run --rm prefect-cli

.DEFAULT_GOAL : help
help:
	@make -pRrq  -f $(THIS_FILE) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'

.PHONY: init
init: \
	docker-clear \
	flows-build \
	docker-up \
	prefect-deploy

.PHONY: docker-down
docker-down:
	$(V)docker compose --profile cli down --volumes --remove-orphans

.PHONY: docker-clear
docker-clear: docker-down
docker-clear:
	$(V)echo "Remove ./volumes"
	$(V)rm -rf ./volumes

.PHONY: docker-up
docker-up:
	$(V)docker compose pull --ignore-buildable
	$(V)docker compose build
	$(V)docker compose up -d

.PHONY: docker-start
docker-start:
	$(V)docker compose up -d

.PHONY: docker-stop
docker-stop:
	$(V)docker compose down

# ---- flows ----

.PHONY: flows-build
flows-build:
	$(V)docker build -t $(FLOWS_IMAGE) flows

.PHONY: prefect-deploy
prefect-deploy:
	$(V)$(PREFECT_CLI) prefect --no-prompt deploy --all

# make prefect-run DEPLOYMENT=hello/hello
.PHONY: prefect-run
prefect-run: DEPLOYMENT=hello/hello
prefect-run:
	$(V)$(PREFECT_CLI) prefect deployment run '$(DEPLOYMENT)' --watch

.PHONY: flows-lint
flows-lint:
	$(V)cd flows && uv sync --frozen && uv run ruff check . ../scripts && uv run ruff format --check . ../scripts

.PHONY: flows-test
flows-test:
	$(V)cd flows && uv sync --frozen && uv run pytest

# ---- vault ----

.PHONY: vault-get
vault-get:
	$(V)docker compose exec vault vault kv get secret/prefect

# make vault-put KEY=api_key VALUE=xxx
.PHONY: vault-put
vault-put:
	$(V)test -n "$(KEY)" || (echo "usage: make vault-put KEY=<key> VALUE=<value>" && exit 1)
	$(V)docker compose exec vault vault kv patch secret/prefect $(KEY)='$(VALUE)'
