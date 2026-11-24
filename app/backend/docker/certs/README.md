# Корневые сертификаты для исходящих HTTPS-запросов

## Зачем

`iss.moex.com` (MOEX ISS) с апреля 2026 отдаёт TLS-сертификаты, выпущенные УЦ
Минцифры: цепочка `*.moex.com` → `Russian Trusted Sub CA` → `Russian Trusted Root CA`.
Корневого сертификата этого УЦ нет в наборе Mozilla, который поставляется
в базовом образе `python:*-slim`, поэтому `requests` падал с ошибкой:

```
requests.exceptions.SSLError: HTTPSConnectionPool(host='iss.moex.com', port=443): Max retries exceeded
with url: /iss/securities/RIZ6.json (Caused by SSLError(SSLCertVerificationError(1,
'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain')))
```

`Base.Dockerfile` backend-а добавляет корневой сертификат в системное хранилище
образа и переключает `requests` (`REQUESTS_CA_BUNDLE`) и OpenSSL (`SSL_CERT_FILE`)
на это хранилище. Runtime-слой наследует и сертификат, и переменные окружения.

## Содержимое

| Файл | Источник | Действителен до |
| --- | --- | --- |
| `russian_trusted_root_ca.crt` | <https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt> | 27.02.2032 |

Проверить содержимое файла:

```bash
openssl x509 -in app/backend/docker/certs/russian_trusted_root_ca.crt -noout -subject -dates -fingerprint -sha256
```

Ожидаемый результат:

```
subject=C=RU, O=The Ministry of Digital Development and Communications, CN=Russian Trusted Root CA
notAfter=Feb 27 21:04:15 2032 GMT
sha256 Fingerprint=D2:6D:2D:02:31:B7:C3:9F:92:CC:73:85:12:BA:54:10:35:19:E4:40:5D:68:B5:BD:70:3E:97:88:CA:8E:CF:31
```

Промежуточный сертификат (`Russian Trusted Sub CA`) в образ добавлять не нужно:
сервер MOEX присылает его сам, в образе должен быть только корень.

## Обновление

По умолчанию загруженный с `gu-st.ru` файл содержит CRLF-переводы строк —
в репозитории файл хранится с LF, без изменений в самом сертификате.
После обновления файла нужно проверить отпечаток (см. выше) и переопубликовать
base-образ (см. ниже): runtime-слой наследует сертификат только из base-слоя.

## Сборка и публикация base-образа

Сертификат меняет base-слой, а base-образ собирается и публикуется вручную
(CI собирает только runtime поверх уже опубликованного тега из `app/backend/build.env`):

```bash
# 1. поднять BASE_IMAGE_NAME в app/backend/build.env (0.0.2 -> 0.0.3)
# 2. собрать и опубликовать
./bin/build-base-image.sh backend
./bin/push-base-image.sh backend
# 3. после merge runtime-образ пересоберётся в CI и унаследует новый base
```

Тот же порядок нужен при любом изменении `Base.Dockerfile` или `requirements.txt`.
Если тег не поднять, CI продолжит собирать runtime поверх старого base-слоя,
и правка в `Base.Dockerfile` не попадёт ни в один образ.
