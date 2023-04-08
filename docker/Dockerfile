FROM python:3
RUN pip3 install --no-cache-dir tinytuya
RUN pip3 install --no-cache-dir tuyapower
ADD run.py /
CMD ["python3", "run.py"]
EXPOSE 6666/udp
EXPOSE 6667/udp
