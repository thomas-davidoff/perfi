FROM python:3.13-slim-bookworm AS base

RUN apt-get update \
    && apt-get upgrade -y


ARG ENVIRONMENT=development
ARG APP_PORT=8000

RUN if [ "$ENVIRONMENT" = "development" ]; then \
        apt-get install -y libpq-dev gcc postgresql-client; \
    fi \
    && apt-get install -y curl \
    && apt-get clean


# version locked poetry to avoid issues
RUN pip install poetry==1.4.2

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
COPY perfi /app/perfi
COPY config /app/config

RUN poetry config installer.max-workers 10

# dev stage
FROM base AS development
ENV POETRY_VIRTUALENVS_PATH="/opt/perfi/"
RUN poetry install --with=dev,test --verbose --no-cache --no-interaction --no-ansi
RUN ln -s "$(poetry env info --path)" /opt/perfi/venv
ENV PATH="/opt/perfi/venv/bin:$PATH"
