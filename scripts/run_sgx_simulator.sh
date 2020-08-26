#!/usr/bin/env bash

set -e

: "${SGX_WALLET_TAG?Need to set SGX_WALLET_TAG}"

SGX_WALLET_IMAGE_NAME=skalenetwork/sgxwallet_sim:1.57.0-develop.1 #$SGX_WALLET_TAG
SGX_WALLET_CONTAINER_NAME=sgx_simulator

docker rm -f $SGX_WALLET_CONTAINER_NAME || true
docker pull $SGX_WALLET_IMAGE_NAME
docker run -d -p 1026-1028:1026-1028 --name $SGX_WALLET_CONTAINER_NAME $SGX_WALLET_IMAGE_NAME -s -y -d -V
