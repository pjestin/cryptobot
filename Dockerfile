FROM python:3.11-slim-bookworm
WORKDIR /app/cryptobot
RUN apt-get update
RUN apt-get install -y build-essential libatlas-base-dev
RUN adduser --uid 1000 --shell /bin/bash cryptouser
USER cryptouser
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
ENV command --version
CMD python ${command}
