FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

RUN apt-get update \
    && apt-get install -yqq git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY requirements_dev.txt /code/
RUN pip install -r requirements_dev.txt

ARG USERNAME=backend
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

USER $USERNAME
