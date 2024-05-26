#!/bin/sh

sed -i "s|LOG_LEVEL=info|LOG_LEVEL=${LOG_LEVEL:-info}|" .env
sed -i "s|LOG_TO_FILE=false|LOG_TO_FILE=${LOG_TO_FILE:-false}|" .env
sed -i "s|LOG_FILE=fs_esl.log|LOG_FILE=${LOG_FILE:-fs_esl.log}|" .env
sed -i "s|TCP_RECEIVER_HOST=0.0.0.0|TCP_RECEIVER_HOST=${TCP_RECEIVER_HOST:-0.0.0.0}|" .env
sed -i "s|TCP_RECEIVER_PORT==6000|TCP_RECEIVER_PORT=${TCP_RECEIVER_PORT:-6000}|" .env

python tcp_receiver.py
