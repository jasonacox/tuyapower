#!/bin/bash
echo "Build and Push jasonacox/tuyapower to Docker Hub"
echo ""

# Determine version
TUYAPOWER=`pip3 index versions tuyapower 2>/dev/null | grep tuyapower | awk -F'[()]' '{print $2}'`
echo " - tuyapower = $TUYAPOWER"
TINYTUYA=`pip3 index versions tinytuya 2>/dev/null | grep tinytuya | awk -F'[()]' '{print $2}'`
echo " - tinytuya = $TINYTUYA"
VER="${TUYAPOWER}-${TINYTUYA}"
echo ""

# Build jasonacox/tuyapower:x.y.z
echo "* BUILD jasonacox/tuyapower:${VER}"
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 --push -t jasonacox/tuyapower:${VER} .
echo ""

# Build jasonacox/tuyapower:latest
echo "* BUILD jasonacox/tuyapower:latest"
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 --push -t jasonacox/tuyapower:latest .
echo ""

# Verify
echo "* VERIFY jasonacox/tuyapower:latest"
docker buildx imagetools inspect jasonacox/tuyapower | grep Platform
echo ""
