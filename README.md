# FreeSWITCH mod_audio_socket PoC

## Description

This is a simple Python ESL script which initiates a call to a SIP extension and bridges that to a Vosk WebSocket endpoint using [mod_audio_socket](https://github.com/amigniter/mod_audio_stream).

## Usage

Default configuration values are ready to use, so you can just start everything using Docker Compose: `docker compose up -d --build`. Once it's started, you can authorize on the FreeSWITCH server with any SIP client. Login credentials would be:

- SIP server: localhost
- Username: anything in range from 1000 to 1019
- Password: `extensionpassword` (could be changed in `docker-compose.yml`, variable `EXTENSION_PASSWORD`, service `freeswitch`, section `environment`)

When it's done, you need to dial 99999 (number could also be changed in `docker-compose.yml`, variable `NUMBER_TO_DIAL` in `esl-app` and in `freeswitch` services). The call will be answered and connected to the Websocket endpoint (by default it's Vosk recognition service endpoint, Vosk instance is deployed via Docker Compose along with other services. You can change WS endpoint address in `docker-compose.yml`, variable `WS_ENDPOINT` in `esl-app` service).

## Speech recognition

Once you're connected to Vosk WS endpoint, speech recognition would start working, and you'll see recognition results in `esl-app` logs (you can check logs this way: `docker compose logs -f esl-app`).

That's it — now you can run the script: `python app.py`.
