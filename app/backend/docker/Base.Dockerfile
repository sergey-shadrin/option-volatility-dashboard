ARG PYTHON_VERSION=3.12.2

FROM --platform=linux/amd64 python:${PYTHON_VERSION}-slim-bullseye as build

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python"]