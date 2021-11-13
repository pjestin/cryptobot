FROM arm32v7/python:3.9-slim-bullseye
WORKDIR /app/cryptobot
RUN apt-get update
RUN apt-get install -y build-essential libatlas-base-dev
RUN adduser --uid 1000 --shell /bin/bash cryptouser
USER cryptouser
COPY Pipfile .
COPY Pipfile.lock .
RUN python -m pip install --upgrade pip pipenv
RUN python -m pipenv install --deploy
ENV command --version
CMD python -m pipenv run python ${command}
