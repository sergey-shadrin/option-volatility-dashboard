FROM python:3.12.2-slim-bullseye

RUN pip install --no-cache-dir pip-tools

CMD ["python"]