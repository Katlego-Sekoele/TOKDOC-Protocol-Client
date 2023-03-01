import datetime
import hashlib
import os
import platform

from Utilities import constants


def test_message() -> str:
    """
    :return: str -> a DATA message
    """
    if platform.system() == 'Windows':
        file_size = os.stat('.\\Utilities\\test.png').st_size
    else:
        file_size = os.stat('./Utilities/test.png').st_size

    message = (constants.START +
               constants.CRLF + constants.CRLF +
               constants.START_METHOD +
               constants.CRLF +
               constants.DATA + constants.SPACE + constants.UPLOAD + constants.SPACE + '127.0.0.1:3000' + constants.SPACE + 'tested.png' +
               constants.CRLF +
               constants.END_METHOD +
               constants.CRLF + constants.CRLF +
               constants.START_HEADERS +
               constants.CRLF +
               constants.USER + ':test@test.com' +
               constants.CRLF +
               constants.ACCESS_KEY + ':' + generate_access_key_decoded('test@test.com') +
               constants.CRLF +
               constants.TIMESTAMP + ':' + str(datetime.datetime.utcnow().isoformat()) +
               constants.CRLF +
               constants.AUTHORIZED + ':' + '(test@test.com,test2@test2.com)' +
               constants.CRLF +
               constants.END_HEADERS +
               constants.CRLF + constants.CRLF +
               constants.START_FILE +
               constants.CRLF +
               constants.FILE_SIZE + ":" + str(file_size) +
               constants.CRLF +
               constants.END_FILE +
               constants.CRLF + constants.CRLF +
               constants.END)

    message_length = len(message)

    message_length = str(message_length) + (16 - len(str(message_length))) * " "

    message = message_length + constants.CRLF + message

    hashed = hashlib.sha256(message.encode()).hexdigest()

    message = hashed + constants.CRLF + message

    return message


def generate_access_key_decoded(email) -> str:
    """
    Generates an access key for the provided email
    :param email:
    :return: str -> access key
    """
    server_key = ' ' * 64
    pre_hash = server_key + email
    return hashlib.sha256(pre_hash.encode()).hexdigest()
