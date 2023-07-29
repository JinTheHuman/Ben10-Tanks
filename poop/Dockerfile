FROM python:3.10-alpine

# Socat needs to be installed for communication with the sidecar
RUN apk add socat build-base

# This directory needs to exist
RUN mkdir -p /codequest

# Copy your files
COPY src /codequest/src

RUN cd /codequest/src && g++ main.cpp -o game.out -std=c++11


# Copy run.sh
COPY run.sh /codequest
RUN chmod +x /codequest/run.sh

WORKDIR /codequest

CMD ["/bin/sh", "-c", "./run.sh"]