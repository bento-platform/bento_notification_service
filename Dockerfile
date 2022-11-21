FROM ghcr.io/bento-platform/bento_base_image:python-debian-2022.10.11

# TODO: change USER
USER root
RUN sudo apt-get install libpq-dev python-dev

WORKDIR /notification

# Create data directory
RUN mkdir -p /notification/data

COPY . .
RUN ls /notification

RUN ["pip", "install", "-r", "requirements.txt"]

# Run
COPY startup.sh ./startup.sh
ENTRYPOINT [ "sh", "./startup.sh" ]