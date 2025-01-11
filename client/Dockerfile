FROM node:23.5.0-alpine

# Install libc6-compat and bash
RUN apk add --no-cache libc6-compat bash curl

WORKDIR /app

COPY package.json yarn.lock ./
RUN yarn install

EXPOSE 3000

ENV HOST=0.0.0.0 PORT=3000 NODE_ENV=development

COPY ./src/ /app/src/
COPY ./public/ /app/public
COPY ./postcss.config.mjs /app/postcss.config.mjs
COPY ./tailwind.config.ts /app/tailwind.config.ts
COPY ./tsconfig.json /app/tsconfig.json
COPY ./components.json /app/components.json
