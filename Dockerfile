FROM arm32v7/python:3.7
WORKDIR /app/cryptobot
RUN mkdir -p /python
COPY requirements.txt /python
RUN apt-get update
RUN apt-get -y install libatlas-base-dev
RUN python -m pip install --upgrade pip
RUN python -m pip install https://www.piwheels.org/simple/numpy/numpy-1.18.3-cp37-cp37m-linux_armv7l.whl#sha256=0ce00413e6c5506b3b46197d0516c295b64828a6c2ce3c08e7004970bb8ff958
RUN python -m pip install https://www.piwheels.org/simple/scipy/scipy-1.4.1-cp37-cp37m-linux_armv7l.whl#sha256=ef4e1b837ece171cb99a957a68d2320e7e3c649e0008ed4efb62851f2ff45bf0
RUN python -m pip install https://www.piwheels.org/simple/grpcio/grpcio-1.28.1-cp37-cp37m-linux_armv7l.whl#sha256=412a486f22257d975f06992d0888a3f9cfa85f2943d9f33177b660c6b3e435e6
RUN python -m pip install https://www.piwheels.org/simple/h5py/h5py-2.10.0-cp37-cp37m-linux_armv7l.whl#sha256=3734f3af6d58f38c84e1b965c02da9f0466356d832bb32ecfffcbe5aad886453
RUN python -m pip install https://github.com/lhelontra/tensorflow-on-arm/releases/download/v2.1.0/tensorflow-2.1.0-cp37-none-linux_armv7l.whl
RUN python -m pip install -r /python/requirements.txt
ENV command --version
CMD python ${command}
