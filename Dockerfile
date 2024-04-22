FROM python:3.12 as builder

RUN pip install poetry==1.7.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.12-slim as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN useradd rollbot && mkdir /app

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src/rollbot /app/rollbot
RUN chown -R rollbot:rollbot /app

USER rollbot
WORKDIR /app

ENTRYPOINT ["python", "-m", "rollbot"]
