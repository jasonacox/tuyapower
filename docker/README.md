# TuyaPower Container

![Docker Pulls](https://img.shields.io/docker/pulls/jasonacox/tuyapower)

A docker container version of the tuyapower library is available on DockerHub and can be used to grab power data without installing the python libraries.

## Docker Usage

_Tested on Linux and MacOS._

```bash
# Friendly Output
# Run tuyapower container - replace with device ID, IP and VERS
docker run -e PLUGID="01234567891234567890" \
    -e PLUGIP="10.0.1.x" \
    -e PLUGKEY="0123456789abcdef" \
    -e PLUGVERS="3.3" \
    jasonacox/tuyapower

# JSON Output
# Run tuyapower container - replace with device ID, IP and VERS
docker run -e PLUGID="01234567891234567890" \
    -e PLUGIP="10.0.1.x" \
    -e PLUGKEY="0123456789abcdef" \
    -e PLUGVERS="3.3" \
    -e PLUGJSON="yes" \
    jasonacox/tuyapower

```
