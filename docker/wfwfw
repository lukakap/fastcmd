FROM python:3.10-slim

WORKDIR /app

COPY requirements-dev.lock requirements-dev.lock

RUN python -m pip install --upgrade pip \
    && pip install -r requirements-dev.lock
