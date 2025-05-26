# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# If this is set to a non-empty string it is equivalent to specifying the -O option. If set to an integer, it is equivalent to specifying -O multiple times.
# ENV PYTHONOPTIMIZE=1

WORKDIR /app

# See https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-setup-tools?tabs=ubuntu-install&view=sql-server-ver16#ubuntu
# Install ODBC driver
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg && \
    curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql18 \
    unixodbc \
    unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Modify the ODBC configuration to include SECLEVEL
# see: https://github.com/openssl/openssl/issues/17476
RUN echo "SECLEVEL=0" >> /etc/odbcinst.ini

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
# pyodbc is CPU architecture dependent and needs to be installed from source in github actions,
# so it is not included in the requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt pyodbc==5.2.* --no-cache-dir

# Copy the source code into the container.
COPY . /app

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
HEALTHCHECK CMD curl --fail http://127.0.0.1:8000/v1/health || exit 1
# CMD ["fastapi", "run", "gen_epix/casedb/app.py", "--port", "8000"]
# CMD ["sh", "-c", "gunicorn --preload -k uvicorn.workers.UvicornWorker gen_epix.casedb.app:FAST_API"]
