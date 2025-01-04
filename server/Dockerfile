FROM python:3.13-slim-bookworm

RUN pip install poetry==1.4.2

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

COPY perfi /app/perfi
COPY config /app/config

RUN poetry config installer.max-workers 10

RUN poetry install --without=test --verbose --no-cache


ENV APP_PORT=8000
ENV APP_HOST=0.0.0.0


EXPOSE 8000

# ENTRYPOINT ["poetry", "run", "python", "-m", "perfi.entry"]
