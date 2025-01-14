ARG APP_USER=perfi
ARG APP_HOME=/opt/perfi

FROM arm64v8/node:23.6.0-alpine
ARG APP_USER
ARG APP_HOME

WORKDIR ${APP_HOME}

RUN apk add --no-cache libc6-compat bash curl

RUN adduser -D -u 1001 ${APP_USER} \
    && chown ${APP_USER}:${APP_USER} ${APP_HOME}

USER ${APP_USER}

COPY --chown=${APP_USER}:${APP_USER} package.json yarn.lock ./
COPY --chown=${APP_USER}:${APP_USER} ./src/ /app/src/
COPY --chown=${APP_USER}:${APP_USER} ./public/ /app/public
COPY --chown=${APP_USER}:${APP_USER} ./postcss.config.mjs /app/postcss.config.mjs
COPY --chown=${APP_USER}:${APP_USER} ./tailwind.config.ts /app/tailwind.config.ts
COPY --chown=${APP_USER}:${APP_USER} ./tsconfig.json /app/tsconfig.json
COPY --chown=${APP_USER}:${APP_USER} ./components.json /app/components.json

ENV NEXT_TELEMETRY_DISABLED 1

RUN yarn install --frozen-lockfile --no-scripts \
    && rm -rf /usr/local/share/.cache/yarn \
    && yarn cache clean

ENTRYPOINT [ "yarn" ]
CMD [ "run", "dev" ]
