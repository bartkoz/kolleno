FROM python:3.12

ENV PYTHONUNBUFFERED 1
ENV PIPENV_SYSTEM 1
ENV PYTHONPATH /opt/app

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /opt/app/
COPY .. /opt/app
RUN poetry config virtualenvs.create false \
    && poetry install --no-root
