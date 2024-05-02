#!/bin/sh

sed -i "s|FS_HOST=[^"]*|FS_HOST=${FS_HOST:-host.docker.internal}|" .env
sed -i "s|FS_ESL_PORT=[^"]*|FS_ESL_PORT=${FS_ESL_PORT:-8021}|" .env
sed -i "s|FS_ESL_PASSWORD=[^"]*|FS_ESL_PASSWORD=${FS_ESL_PASSWORD:-ClueCon}|" .env
sed -i "s|LOG_LEVEL=[^"]*|LOG_LEVEL=${LOG_LEVEL:-info}|" .env
sed -i "s|LOG_TO_FILE=[^"]*|LOG_TO_FILE=${LOG_TO_FILE:-false}|" .env
sed -i "s|LOG_FILE=[^"]*|LOG_FILE=${LOG_FILE:-fs_esl.log}|" .env
sed -i "s|WS_ENDPOINT=[^"]*|WS_ENDPOINT=${WS_ENDPOINT:-ws://vosk-server:2700}|" .env
sed -i "s|NUMBER_TO_DIAL==[^"]*|NUMBER_TO_DIAL=${NUMBER_TO_DIAL:-99999}|" .env

python app.py
