ARG POETRY_VERSION
ARG PYTHON_VERSION
ARG APP_USER=perfi
ARG APP_HOME=/opt/perfi


FROM python:${PYTHON_VERSION}-slim-bookworm@sha256:1127090f9fff0b8e7c3a1367855ef8a3299472d2c9ed122948a576c39addeaf1 AS base

ARG POETRY_VERSION
ARG APP_USER
ARG APP_HOME

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    postgresql-client \
    libpq-dev \
    build-essential \
    && apt-get clean \
    && useradd -ms /bin/bash ${APP_USER} \
    && chown ${APP_USER}:${APP_USER} ${APP_HOME}

USER ${APP_USER}
ENV PATH=/home/${APP_USER}/.local/bin:${APP_HOME}/.venv/bin:$PATH

COPY --chown=${APP_USER}:${APP_USER} pyproject.toml poetry.lock ${APP_HOME}/
COPY --chown=${APP_USER}:${APP_USER} perfi ${APP_HOME}/perfi
COPY --chown=${APP_USER}:${APP_USER} config ${APP_HOME}/config
COPY --chown=${APP_USER}:${APP_USER} cli ${APP_HOME}/cli

RUN pip install --user poetry==${POETRY_VERSION} \
    && poetry config virtualenvs.in-project true \
    && poetry config installer.max-workers 10

RUN poetry sync --without dev,test --no-ansi --no-interaction --no-cache


FROM base AS development

RUN poetry install --with dev,test --no-ansi --no-interaction --no-cache

ENTRYPOINT [ "perfi" ]
CMD [ "run" ]
