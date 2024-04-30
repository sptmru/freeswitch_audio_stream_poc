"""FreeSWITCH ESL app demonstrating https://github.com/amigniter/mod_audio_stream usage"""

import logging
import sys
import json
import socket
import threading
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


def esl_event_handler(event, conn):
    """
    Handle incoming FreeSWITCH ESL events.
    """
    event_name = event.getHeader("Event-Name")

    if event and event_name == "CHANNEL_PARK":
        uuid = event.getHeader("Unique-ID")
        logger.info("Call %s started", uuid)
        conn.api("uuid_answer", uuid)

    if event and event_name == "CHANNEL_ANSWER":
        uuid = event.getHeader("Unique-ID")
        logger.info("Call %s answered", uuid)
        connect_channel_with_ws_endpoint(
            conn, uuid, config.get('WS_ENDPOINT'))
        logger.info("Connected call %s to WS endpoint", uuid)

    if event and event_name == 'CUSTOM':
        log_recognition_result(event)

    if event and event_name == "CHANNEL_HANGUP":
        uuid = event.getHeader("Unique-ID")
        logger.info("Call %s ended", uuid)


def handle_esl_connection(client_socket, address):
    """
    Handle incoming ESL connection.
    """
    logger.info("Got ESL inbound connection at %s", address)
    conn = ESLconnection(client_socket.fileno())

    conn.events("plain", "ALL")
    while True:
        event = conn.recvEvent()
        esl_event_handler(event, conn)


def start_esl_server(host, port):
    """
    Start ESL server to listen for incoming connections from FreeSWITCH.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        logger.info("ESL server listening on %s:%s", host, port)
        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(
                target=handle_esl_connection, args=(client_socket, addr))
            thread.start()


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


def originate_call(esl_connection, extension):
    """
    Initiates an outbound call from FreeSWITCH to a specified extension.

    This method uses an existing ESLconnection object to originate an outbound
    call to the specified extension on the FreeSWITCH server.

    Args:
        esl_connection (ESLconnection): An existing connection object to the FreeSWITCH server.
        extension (str): The extension number to call.

    Returns:
        str or None: The UUID of the call if successfully originated, otherwise None.
    """
    response = esl_connection.api(
        "originate", f"user/{extension} &park() async")
    if response:
        uuid = response.getBody().split()[1]
        return uuid

    logger.error('Could not originate call')
    return None


def connect_channel_with_ws_endpoint(esl_conn, uuid, ws_endpoint):
    """
    Connects a channel to a WebSocket (WS) endpoint for audio streaming.

    This method connects a channel identified by its UUID to the specified
    WebSocket (WS) endpoint for audio streaming. It sends a command to FreeSWITCH
    via the provided ESLconnection object to establish the audio stream.

    Args:
        esl_conn (ESLconnection): An existing connection object to the FreeSWITCH server.
        uuid (str): The UUID of the channel to connect.
        ws_endpoint (str): The WebSocket (WS) endpoint URL for audio streaming.

    Returns:
        None
    """
    command = f'uuid_audio_stream {uuid} start {ws_endpoint} mono 8k'
    esl_conn.api(command)


def log_recognition_result(event):
    """
    Parses recognition result from FreeSWITCH event and logs it.

    Returns:
        None
    """
    if not event:
        return
    try:
        result = json.loads(event.getBody())
        if len(result['partial']) > 0:
            logger.info("Partial recognition result: %s",
                        result['partial'])
    except (json.JSONDecodeError, KeyError):
        pass


def main():
    """
    Main function
    """
    esl_conn = connect_to_freeswitch()
    if esl_conn is None:
        logger.error('Exiting...')
        sys.exit(1)

    esl_inbound_host = config.get('ESL_INBOUND_HOST', '0.0.0.0')
    esl_inbound_port = int(config.get('ESL_INBOUND_PORT', '8022'))

    start_esl_server(esl_inbound_host, esl_inbound_port)

    # uuid = originate_call(esl_conn, config.get('SIP_EXTENSION'))
    # connect_channel_with_ws_endpoint(esl_conn, uuid, config.get('WS_ENDPOINT'))


if __name__ == "__main__":
    main()
