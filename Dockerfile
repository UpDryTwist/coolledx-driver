FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_CACHE_DIR='/tmp/poetry_cache'\
    PATH="/app/.venv/bin:$PATH" \
    USER=dockeruser \
    USER_ID=1000 \
    GROUP=dockergroup \
    GROUP_ID=1000

COPY --chown=${USER}:${GROUP}--chmod=0755 pyproject.toml poetry.lock /app/

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.11-slim-bookworm AS runtime

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    USER=dockeruser \
    USER_ID=1000 \
    GROUP=dockergroup \
    GROUP_ID=1000

RUN apt-get update && apt-get install -y --no-install-recommends \
    gosu procps \
    fontconfig \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto \
    fonts-freefont-ttf \
    bluetooth \
    bluez \
    tshark \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN groupadd --gid "${GROUP_ID}" "${GROUP}" && \
    useradd \
        --uid "${USER_ID}" \
        --gid "${GROUP}" \
        --create-home \
        --home /var/empty \
        --shell /bin/nologin \
        "${USER}" && \
    mkdir -p /config /data /logs && \
    chown -R "${USER}":"${GROUP}" /config /logs && \
    chmod -R a+rwX /config /logs

COPY --from=builder --chown=${USER}:${GROUP} --chmod=0755 /app/.venv /app/.venv

COPY --chown=dockeruser:dockergroup --chmod=0755 src/coolledx /app/coolledx
COPY --chown=dockeruser:dockergroup --chmod=0755 run_scripts /app/run_scripts
COPY --chown=dockeruser:dockergroup --chmod=0755 utils       /app/utils
# COPY --chown=dockeruser:dockergroup --chmod=a+rw default_config /config

# USER "${USER}"

# Set up the environment variables we're expecting
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    LOGFILE=/logs/coolledx.log

# TODO:
#    CONFIGFILE=/config/coolledx_driver.yaml \

VOLUME /config /logs

# EXPOSE <port>
ENTRYPOINT ["/app/run_scripts/start_module.sh"]

CMD []
