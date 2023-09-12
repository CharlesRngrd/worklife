FROM python:3.11-slim-buster

# Install Poetry and compilers
RUN apt-get update && apt-get install -y --no-install-recommends \
	curl gcc g++ libffi-dev make && \
	rm -rf /var/lib/apt/lists/* && \
	curl -sSL https://install.python-poetry.org/ | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry add httpx && poetry install && echo "Success"

ENV PATH=/root/.local/bin:$PATH
EXPOSE 80
