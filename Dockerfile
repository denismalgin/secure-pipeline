
# ── Stage 1: install dependencies ────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# copy only requirements to cache them in a separate layer,
# if requirements.txt doesn't change, the dependencies will be cached and not reinstalled
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime image ────────────────────────────────────────────────────
# start fresh from python:3.12-slim
# This dramatically shrinks the attack surface Trivy has to scan
FROM python:3.12-slim AS runtime

# create a non-root user, if the app process is ever compromised, the attacker has no root access to the host.
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

WORKDIR /app

# copy only the installed packages from the builder stage
COPY --from=builder /install /usr/local

COPY app/ ./app/

USER appuser

EXPOSE 8000

# Docker (and ECS/k8s) use this to know when the container is healthy
# The pipeline's deploy step waits for this before removing the old container
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
