import hashlib

import Utilities.constants as constants


def get_checksum(message: str) -> str:
    """
    :param message:
    :return: str -> the checksum provided in the message
    """
    return message[:constants.CHECKSUM_LENGTH]


def generate_checksum(message: str) -> str:
    """
    :param message:
    :return: str -> a sha256 checksum of the given message
    """
    return hashlib.sha256(message.encode()).hexdigest()
