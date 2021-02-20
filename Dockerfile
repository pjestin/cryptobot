FROM arm64v8/python:3.7-buster
WORKDIR /app/cryptobot
RUN apt-get update
RUN apt-get -y install build-essential libatlas-base-dev llvm python-openssl libhdf5-dev
RUN useradd -m -u 1000 -s /bin/bash cryptouser
USER cryptouser
RUN python -m pip install --upgrade pip
COPY requirements.txt /home/cryptouser
RUN python -m pip install -r /home/cryptouser/requirements.txt
ENV command --version
CMD python ${command}
