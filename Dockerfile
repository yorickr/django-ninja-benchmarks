FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=on POETRY_VIRTUALENVS_CREATE=false
WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN pip install poetry
RUN poetry install

COPY common_django_settings.py /app/common_django_settings.py
COPY app_drf /app/
COPY app_flask_marshmallow /app/
COPY app_ninja /app/
COPY network_service.py /app/network_service.py
