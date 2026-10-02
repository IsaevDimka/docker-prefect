FROM ghcr.io/astral-sh/uv:0.12-python3.14-trixie-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0
WORKDIR /opt/flows
RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=uv.lock,target=uv.lock \
	--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
	uv sync --frozen --no-install-project --no-dev
COPY pipelines ./pipelines
COPY libs ./libs

FROM python:3.14-slim-trixie AS final
WORKDIR /opt/flows
COPY --from=builder /opt/flows /opt/flows
ENV PYTHONDONTWRITEBYTECODE=1 PATH="/opt/flows/.venv/bin:$PATH"
