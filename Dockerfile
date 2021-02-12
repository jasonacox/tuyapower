FROM python:3
ADD test.py /
ADD tuyapower /tuyapower
RUN pip install pycryptodome # or pycrypto, pyaes, Crypto
RUN pip install tinytuya
ENV PYTHONPATH "${PYTONPATH}:/tuyapower"
CMD [ "python", "./test.py" ]
