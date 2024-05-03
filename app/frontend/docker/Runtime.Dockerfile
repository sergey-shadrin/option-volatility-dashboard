ARG BASE_IMAGE_NAME=""

FROM ${BASE_IMAGE_NAME}

COPY src/nginx_conf /etc/nginx
COPY src/data /data