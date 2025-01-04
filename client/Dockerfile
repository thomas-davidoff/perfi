FROM node:23.5.0-alpine

# Install libc6-compat and bash
RUN apk add --no-cache libc6-compat bash

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



# # Run the next build process and generate the artifacts
# RUN npm run build

# FROM node:23.5.0-alpine

# RUN apk update && apk upgrade && adduser -D nextuser && apk add --no-cache bash

# WORKDIR /app
# COPY --from=build --chown=nextuser:nextuser /app/public ./public
# COPY --from=build --chown=nextuser:nextuser /app/.next/standalone ./
# COPY --from=build --chown=nextuser:nextuser /app/.next/static ./.next/static
# USER nextuser
# EXPOSE 3000

# ENV HOST=0.0.0.0 PORT=3000 NODE_ENV=production
# # CMD ['yarn', 'run', 'dev']
