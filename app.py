"""FreeSWITCH ESL app demonstrating https://github.com/amigniter/mod_audio_stream usage"""

import logging
import sys
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

if config.get('LOG_TO_FILE', 'False'):
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
        "originate", f"user/{extension} &echo() async")
    if response:
        # uuid = response.getBody().decode().split(' ')[1]
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


def main():
    """
    Main function
    """
    esl_conn = connect_to_freeswitch()
    if esl_conn is None:
        logger.error('Exiting...')
        sys.exit(1)

    uuid = originate_call(esl_conn, config.get('SIP_EXTENSION'))
    connect_channel_with_ws_endpoint(esl_conn, uuid, config.get('WS_ENDPOINT'))


if __name__ == "__main__":
    main()
