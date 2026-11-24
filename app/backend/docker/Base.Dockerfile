ARG PYTHON_VERSION=3.12.2

FROM --platform=linux/amd64 python:${PYTHON_VERSION}-slim-bullseye as build

# iss.moex.com отдаёт сертификаты, выпущенные УЦ Минцифры (Russian Trusted Root CA),
# а в наборе корневых сертификатов Mozilla, который лежит в python:*-slim, его нет.
# Добавляем корневой сертификат УЦ в системное хранилище образа: без этого requests
# падает с CERTIFICATE_VERIFY_FAILED (self signed certificate in certificate chain).
COPY docker/certs/russian_trusted_root_ca.crt /usr/local/share/ca-certificates/russian_trusted_root_ca.crt
RUN update-ca-certificates

# requests по умолчанию использует не системное хранилище, а собственный бандл certifi,
# поэтому явно указываем и ему, и OpenSSL на обновлённый системный бандл.
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python"]
