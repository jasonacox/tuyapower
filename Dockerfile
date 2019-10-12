FROM python:3
ADD test.py /
ADD tuyapower /tuyapower
RUN pip install Crypto
RUN pip install pyaes
RUN pip install pytuya
ENV PYTHONPATH "${PYTONPATH}:/tuyapower"
CMD [ "python", "./test.py" ]
