FROM arm64v8/python:3.9-slim-buster
WORKDIR /app/cryptobot
RUN apt-get update
RUN apt-get install -y build-essential
RUN useradd -m -u 1000 -s /bin/bash cryptouser
USER cryptouser
COPY Pipfile .
COPY Pipfile.lock .
RUN python -m pip install --upgrade pip pipenv
RUN python -m pipenv install
ENV command --version
CMD python -m pipenv run python ${command}
