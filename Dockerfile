FROM ubuntu:latest
LABEL authors="sonic"

ENTRYPOINT ["top", "-b"]