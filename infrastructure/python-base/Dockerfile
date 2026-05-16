# NebulaX shared Python base image.
#
# Every Python service in this project FROM nebulax-python-base:latest.
# Build with: ./scripts/build_base.sh
#
# Standardizes:
#   - Python 3.11 on Debian slim (drops the mix of 3.9/3.10-alpine/3.10-slim)
#   - System packages that multiple services were installing independently
#   - The pip deps used across 80%+ of services
#
# Service-specific deps stay in each service's requirements.txt; pip will report
# "Requirement already satisfied" for anything already in this base, so layer
# reuse is automatic.

FROM python:3.11-slim-bookworm

# System packages used across multiple services:
#   - gcc/build-essential: build wheels that lack a binary for slim
#   - libffi-dev, libssl-dev: paramiko, cryptography
#   - libpq-dev: psycopg2 / asyncpg
#   - curl: handy for healthchecks in service entrypoints
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libffi-dev \
        libssl-dev \
        libpq-dev \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /tmp/base-requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --default-timeout=1000 -r /tmp/base-requirements.txt

# Sanity: print the installed common set on build so logs show what's baked in.
RUN python -c "import requests, schedule, flask, paramiko, redis, faker, jwt; print('nebulax-python-base ready')"
