# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim-buster as base

LABEL version="2022.2.0" maintainer="martin.ron@factorio.cz"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.2.0

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc libsndfile1
RUN apt-get clean

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY poetry.loc[k] .
COPY pyproject.toml .

FROM base as prod
RUN poetry config virtualenvs.create false \
  && poetry install --without dev --no-interaction --no-ansi --no-cache

COPY . /app/

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
# RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER appuser

ENTRYPOINT [ "python3", "weather_scraper/main.py" ]

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
# CMD ["python3", "mpc_oven/main.py", "--config", "configs/config.json"]
CMD [ "--config", "configs/config.json"]