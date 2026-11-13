# syntax=docker/dockerfile:1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e

# Image for the local and public compose stacks (docker-compose*.yml), which
# set the command of each service (`python run.py api <APP> ...`, alembic, the
# mock OIDC server).
#
# Production builds lsp-api/Dockerfile instead. This file mirrors it, except:
# - the base is the public python:slim image on the same Debian release, not
#   the hardened dhi.io image, which needs a login;
# - no entrypoint.sh: its config templating is for Kubernetes, locally the
#   TOML files and environment variables do that job;
# - no Azure libraries, which gen-epix-api does not use;
# - no OCI labels;
# - the build context is this repository, not lsp-api with gen-epix-api inside.
#
# cert/ is excluded by .dockerignore: the image serves plain HTTP, and run.py
# enables TLS whenever cert/key.pem and cert/cert.pem exist.

ARG PYTHON_VERSION=3.14.6
FROM python:${PYTHON_VERSION}-slim-trixie AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install the Microsoft ODBC 18 driver from the Debian 13 package feed.
# See https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && curl -fsSLO https://packages.microsoft.com/config/debian/13/packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql18 \
    unixodbc \
    unixodbc-dev \
    && echo "SECLEVEL=0" >> /etc/odbcinst.ini \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ARG UID=1001
ARG GID=1001

# Create writable directories for read-only root filesystem support
RUN mkdir -p /app/tmp /app/cache /app/logs && \
    chown -R "${UID}:${GID}" /app

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
# pyodbc is CPU architecture dependent and needs to be installed from source in github actions,
# so it is not included in the requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt pyodbc==5.3.* --no-cache-dir

# Copy the source code into the container.
COPY --chown=${UID}:${GID} . /app

# Expose the port that the application listens on.
EXPOSE 8000

# Health check for CASEDB on 8000; the compose files set their own per service.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail --silent --max-time 5 http://127.0.0.1:8000/v1/health || exit 1

# Switch to non-root user
USER ${UID}:${GID}
