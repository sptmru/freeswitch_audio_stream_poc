# FreeSWITCH mod_audio_socket PoC

## Description

This is a simple Python ESL script which initiates a call to a SIP extension and bridges that to a WebSocket endpoint using [mod_audio_socket](https://github.com/amigniter/mod_audio_stream).

## Prerequisites

You'll need a FreeSWITCH server with configured ESL. Also, you'll need to install mod_audio_socket module using [this instruction](https://github.com/amigniter/mod_audio_stream/blob/main/README.md).

## Usage

To run Vosk Websocket server, you can use Docker Compose: `docker compose up -d vosk-server`.

You'll also need to install Python dependencies: `pip install -r requirements.txt` (and you will probably want to create virtualenv before that).

After that, create `.env` file (you can use `.env.example` as an example) and update parameters you want to change. You would definitely want to update `SIP_EXTENSION` to your SIP extension number, `WS_ENDPOINT` to your WebSocket endpoint (Vosk endpoint is `ws://localhost:2700` if you run it locally with Docker Compose), and, of course, FreeSWITCH ESL credentials (`FS_HOST`, `FS_ESL_PORT`, `FS_ESL_PASSWORD`).

That's it — now you can run the script: `python app.py`.
