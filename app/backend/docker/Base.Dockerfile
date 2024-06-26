ARG PYTHON_VERSION=3.12.2

FROM python:${PYTHON_VERSION}-slim-bullseye

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python"]