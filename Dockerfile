FROM python:3.10-slim-buster

ENV PYTHONPATH "${PYTHONPATH}:/CodeReviewAI"

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  POETRY_VERSION=1.7.0 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN apt-get update && apt-get install -y libpq-dev

RUN apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
  && pip install "poetry-core==1.8.1" "poetry==$POETRY_VERSION" && poetry --version

WORKDIR /CodeReviewAI
COPY ./poetry.lock ./pyproject.toml /CodeReviewAI/

COPY . /CodeReviewAI

RUN poetry install

RUN chmod +x /CodeReviewAI/run_fastapi.sh
CMD ["bash", "/CodeReviewAI/run_fastapi.sh"]
