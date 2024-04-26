ARG BASE_IMAGE_NAME=""

FROM ${BASE_IMAGE_NAME}

WORKDIR /app

COPY src .

USER www-data

ENTRYPOINT ["python"]
CMD ["main.py"]