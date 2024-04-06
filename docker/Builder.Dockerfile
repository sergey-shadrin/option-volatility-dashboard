ARG PYTHON_VERSION=3.12.2

FROM python:${PYTHON_VERSION}-slim-bullseye

RUN pip install --no-cache-dir pip-tools

CMD ["python"]