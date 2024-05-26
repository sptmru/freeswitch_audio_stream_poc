"""FreeSWITCH ESL app demonstrating https://github.com/amigniter/mod_audio_stream usage"""

import logging
import sys
import json
from ESL import ESLconnection
from dotenv import dotenv_values

log_level_mapping = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

config = dotenv_values('.env')

log_level = config.get('LOG_LEVEL', 'INFO')
log_level = log_level_mapping.get(log_level.upper(), logging.INFO)

logger = logging.getLogger('freeswitch_audio_stream_poc')
logging.basicConfig(level=log_level)

log_console_handler = logging.StreamHandler(sys.stdout)
log_console_handler.setLevel(log_level)
log_console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(log_console_handler)

if config.get('LOG_TO_FILE', 'True'):
    log_file = config.get('LOG_FILE', 'fs_esl.log')
    log_file_handler = logging.FileHandler(log_file)
    log_file_handler.setLevel(log_level)
    log_file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_file_handler)


def connect_to_freeswitch():
    """
    Connects to a FreeSWITCH server using ESL (Event Socket Library).

    This function establishes a connection to a FreeSWITCH server using ESL
    (Event Socket Library) and returns the connection object if successful.

    Returns:
        ESLconnection or None: The ESLconnection object if connection is successful,
        otherwise None.
    """
    con = ESLconnection(config.get('FS_HOST'), config.get(
        'FS_ESL_PORT'), config.get('FS_ESL_PASSWORD'))
    if con.connected():
        logger.info('Connected to FreeSWITCH')
        return con

    logger.error('Could not connect to FreeSWITCH!')
    return None


def log_recognition_result(event):
    """
    Parses recognition result from FreeSWITCH event and logs it.

    Returns:
        None
    """
    if not event or event.getBody() is None:
        return
    try:
        result = json.loads(event.getBody())
        if len(result['partial']) > 0:
            logger.info("Partial recognition result: %s",
                        result['partial'])
    except (json.JSONDecodeError, KeyError):
        pass


def connect_channel_with_endpoint(esl_conn, uuid, endpoint):
    """
    Connects a channel to a WebSocket (WS) or TCP endpoint for audio streaming.

    This method connects a channel identified by its UUID to the specified
    WebSocket (WS) or TCP endpoint for audio streaming. It sends a command to FreeSWITCH
    via the provided ESLconnection object to establish the audio stream.

    Args:
        esl_conn (ESLconnection): An existing connection object to the FreeSWITCH server.
        uuid (str): The UUID of the channel to connect.
        endpoint (str): The WebSocket (WS) or TCP endpoint URL for audio streaming.

    Returns:
        None
    """
    command = f'uuid_audio_stream {uuid} start {endpoint} mono 8k'
    esl_conn.api(command)


def esl_event_handler(event, conn):
    """
    Handle FreeSWITCH ESL events.
    """
    if not event:
        return

    event_name = event.getHeader("Event-Name")
    match event_name:
        case "CHANNEL_PARK":
            destination_number = event.getHeader("Caller-Destination-Number")
            if destination_number == config.get('NUMBER_TO_DIAL'):
                uuid = event.getHeader("Unique-ID")
                logger.info("Call %s started", uuid)
                conn.api("uuid_answer", uuid)
        case "CHANNEL_ANSWER":
            uuid = event.getHeader("Unique-ID")
            destination_number = event.getHeader("Caller-Destination-Number")
            if destination_number == config.get('NUMBER_TO_DIAL'):
                logger.info("Call %s answered", uuid)
                connect_channel_with_endpoint(
                    conn, uuid, config.get('ENDPOINT'))
                logger.info("Connected call %s to the endpoint", uuid)
        case "CUSTOM":
            if event.getHeader("Event-Subclass") == "mod_audio_stream::json":
                log_recognition_result(event)
        case _:
            if event_name != "SERVER_DISCONNECTED":
                logger.debug("Received event: %s", event_name)


def main():
    """
    Main function
    """
    esl_conn = connect_to_freeswitch()
    if esl_conn is None:
        logger.error('Exiting...')
        sys.exit(1)

    esl_conn.events("plain", "ALL")
    while True:
        event = esl_conn.recvEvent()
        esl_event_handler(event, esl_conn)


if __name__ == "__main__":
    main()
