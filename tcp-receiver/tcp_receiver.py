"""TCP server example for https://github.com/sptmru/freeswitch_mod_audio_stream"""

import socket
import sys
import logging
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


HOST = config.get('TCP_RECEIVER_HOST', "0.0.0.0")
PORT = int(config.get('TCP_RECEIVER_PORT', 6000))


def handle_connection(conn):
    """
    Handle incoming connection and save incoming audio data to received_audio.raw file
    """
    with open('received_audio.raw', 'wb') as f:
        logger.info("Opened file to save received audio data")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
            f.flush()
        logger.info(
            'Connection closed, audio data received and saved to received_audio.raw')


def main():
    """
    Main function
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        logger.info('Server listening on %s:%s', HOST, PORT)

        while True:
            conn, addr = s.accept()
            logger.info('Connected by %s', addr)
            handle_connection(conn)
            conn.close()


if __name__ == "__main__":
    main()
