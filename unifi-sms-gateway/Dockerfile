# ARG BUILD_FROM
# FROM $BUILD_FROM

# WORKDIR /app

# COPY requirements.txt /app
# RUN apk update
# RUN apk add gcc
# RUN apk add gcc musl-dev libffi-dev
# RUN --mount=type=cache,target=/root/.cache/pip \
#     pip3 install -r requirements.txt

# COPY . /app

# ENTRYPOINT ["python3"]
# CMD ["sms.py"]

# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

WORKDIR /app

COPY requirements.txt /app

RUN apk update
RUN apk add gcc
RUN apk add gcc musl-dev libffi-dev
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY sms.py /app

ENTRYPOINT ["python3"]
CMD ["sms.py"]