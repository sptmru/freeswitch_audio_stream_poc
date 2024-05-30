"""TCP server example for https://github.com/sptmru/freeswitch_mod_audio_stream"""

import socket
import sys
import logging
from io import BytesIO
from dotenv import dotenv_values
from pydub import AudioSegment

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


def analyze_audio_data(data):
    """
    Analyze the incoming audio data and estimate format details.
    """
    audio = AudioSegment.from_raw(
        BytesIO(data), sample_width=2, frame_rate=44100, channels=1)

    sample_rate = audio.frame_rate
    bit_depth = audio.sample_width * 8
    num_channels = audio.channels

    return sample_rate, bit_depth, num_channels


def handle_connection(conn):
    """
    Handle incoming connection, analyze audio data, and save audio data to received_audio.raw file
    """
    with open('received_audio.raw', 'wb') as f:
        logger.info("Opened file to save received audio data")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            sample_rate, bit_depth, num_channels = analyze_audio_data(data)
            logger.info("Estimated Audio Format: Sample Rate = %d Hz, Bit Depth = %d bits, Channels = %d",
                        sample_rate, bit_depth, num_channels)
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
