ARG BUILD_FROM
FROM $BUILD_FROM

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

WORKDIR /app

COPY src/requirements.txt /app

RUN apk update
RUN apk add gcc
RUN apk add gcc musl-dev libffi-dev
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY src/. /app

ENTRYPOINT ["python3"]
CMD ["sms.py"]
