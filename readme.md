# Readme
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Pre-requisites

First, clone this repo:

```
git clone git@github.com:thomas-davidoff/perfi.git
```

### System dependencies: Running the app with Docker

#### Docker && Docker Compose V2

If on MacOS, installation of Docker Desktop should be sufficient. Head over to the [Docker docs](https://docs.docker.com/desktop/setup/install/mac-install/) to view detailed installation instructions. If you already have Docker Desktop installed, verify you are using the latest version. Update to the latest version by navigating to Docker Desktop > Settings > Software Update.

**Note**: If on Apple silicon, you may also have to install Rosetta 2. To do so, run `softwareupdate --install-rosetta`.

Verify your docker installation by running `docker --version` in your tty. Also verify that docker compose **v2** is installed. V2 is included by default with a fresh installation of Docker Desktop. To check your version of Docker Desktop, run `docker compose version`.

### System dependencies: Contributing and running the app on your host machine

If running the application on your host machine, you'll need a few things:

- Python installed (see server/pyproject.toml for required version)
- Poetry installed ( `pipx install poetry` )
- Node installed
- Yarn installed


### Application dependencies

If running the application with Docker, you can skip this.

Install node dependencies:
```
cd client
yarn install
```

Install python dependencies:
```
poetry install
```

### Environment variables

For both the frontend and backend, you'll need a few env vars to start the application.

If running using Docker, most of the service-related environment variables will be injected at run time.

#### Frontend env vars

Place the following keys in a file at `client/.env.local`: Generate a base64 encoded key with your tool of choice to place as the `NEXTAUTH_SECRET`. Env vars that are provided by docker compose (and thus not necessary to run locally) are marked as such:

```
NEXTAUTH_SECRET=""
NEXT_PUBLIC_API_BASE_URL=http://backend:8000 # not required if running with docker compose
NEXT_PUBLIC_BASE_URL=http://localhost:3000 # not required if running with docker compose
NEXTAUTH_URL=http://localhost:3000 # not required if running with docker compose
NEXT_TELEMETRY_DISABLED=1 # recommended
```


#### Backend env vars

The backend will load the appropriate env file depending on which environment is being used. For `ENVIRONMENT=test`, the `.env.test` env file will be loaded. Same for any other environment. For local dev, create a file at `server/.env.development` and place the following variables. Env vars that are provided by docker compose (and thus not necessary to run locally) are marked as such:

```
# App config
UPLOAD_FOLDER=uploads
APP_NAME=perfi-api
APP_PORT=8000 # optional with docker compose
APP_HOST=localhost # optional with docker compose

# Database conf
DB_PASS="" # generate a password
DB_HOST=localhost # optional with docker compose
DB_PORT=5432 # optional with docker compose
DB_USER=perfi_dev # optional with docker compose
DB_NAME=perfi # optional with docker compose

# JWT conf
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=300 # optional
REFRESH_TOKEN_EXPIRE_DAYS=30 # optional
```

Generate a 256-bit key and add it to your env file you just created:

```
echo 'import secrets; print(f"SECRET_KEY={secrets.token_bytes(32).hex()}")' | python >> server/.env.development
```

Lastly, create a file named `.env.db` at the root of the project, and add the password for the db you set in your `.env.development` file there too. It's just there to reconcile the passwords.

`.env.db`:
```
POSTGRES_PASSWORD="the same password"
```

## Running the application

### Docker Compose

If using docker compose, start the application with `docker compose up -d`. This builds your images and starts the services defined in `docker-compose.yml` in the background. If the images successfully start, you can visit the homepage at `localhost:3000/login`. API docs will be at `localhost:8000/docs`.

Check the status of running services quickly with `docker compose ps`. If you see that the client or backend are failing, you can investigate the logs with `docker compose logs backend` (or frontend), or check the healthcheck logs with `docker inspect pf-backend | jq -r '.[0].State.Health'`.

Before interacting with the application, you'll need to make sure you perform migrations.

To run migrations, just run `docker compose exec backend perfi db upgrade`. To ensure that no migrations are pending afterwards, run `docker compose exec backend perfi db check`. You should see `Database is up-to-date.`.

### On host machine

If running on host machine, you can start each service individually.

First, start the database service using docker compose with `docker compose scale db=1 test_db=1`. This starts an instance of the dev database and test database. Your db should now be accessible at `localhost:5432`:

```
$ pg_isready --dbname=perfi --host=localhost --port=5432 --username=perfi_dev
localhost:5432 - accepting connections
```

In your backend directory, start a poetry shell, then run migrations and start the application:

```
$ cd server
$ poetry shell
(perfi-py3.13) $ perfi db upgrade
Database has been upgraded to the latest migration.
(perfi-py3.13) $ perfi run
...
INFO:     Application startup complete.
```

In another tty, navigate to the client directory and start the frontend:
```
$ cd client
$ yarn run dev
```

## Running tests

### With docker compose

Tests and test configuration are not mounted by default with the development container. Db connection strings also point to the existing dev db. For this reason, `docker-compose.test.yml` exists, which mount additional local files and have env var overrides.

Running tests with docker compose is a work in progress, in so far as to figuring out the optimal way to modify test behavior on the fly. Currently, default flags and options are defined in `pyproject.toml` in the `[tool.pytest.ini_options]` section.

To run tests with docker compose, run them as a job:

```
docker compose -f docker-compose.test.yml run --rm test
```

### From host machine

Alternatively, if you have the required system and app dependencies installed, you can run tests directly. Before running the command, you'll need to ensure that the test_db is up and running if it isn't already. Use the command `docker compose scale test_db=1` to start just the test db, then run:

```
$ cd server
$ poetry shell
(perfi-py3.13) $ pytest
```

### Contributing

Install pre-commit with pip to run linters prior to committing with `pip install pre-commit`.

You can run pre-commit before attempting a commit with `pre-commit run --all-files`.
