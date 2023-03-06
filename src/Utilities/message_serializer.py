import os

from Utilities.constants import *
from Utilities.codes import *
from Utilities.checksum_utility import *


def build_auth_requests(parameters):
    """
        :param status: codes.Status object
        :return: str -> string formatted response message according to TOKDOC protocol
        """
    message = (
            START +
            CRLF + CRLF +
            START_METHOD +
            CRLF +
            AUTH + SPACE + parameters[constants.EMAIL] + SPACE + parameters[constants.PASSWORD] +
            CRLF +
            END_METHOD +
            CRLF + CRLF +
            END
            )

    message_size = len(message.encode())
    message = (str(message_size) + (MESSAGE_SIZE_LENGTH - len(str(message_size))) * " " +
               CRLF + message)

    checksum = generate_checksum(message)
    return (checksum + CRLF + message).encode(), b''


def build_exit_requests():
    """
        :param status: codes.Status object
        :return: str -> string formatted response message according to TOKDOC protocol
        """
    message = (
            START +
            CRLF + CRLF +
            START_METHOD +
            CRLF +
            EXIT +
            CRLF +
            END_METHOD +
            CRLF + CRLF +
            END
            )

    message_size = len(message.encode())
    message = (str(message_size) + (MESSAGE_SIZE_LENGTH - len(str(message_size))) * " " +
               CRLF + message)

    checksum = generate_checksum(message)
    return (checksum + CRLF + message).encode(), b''


def build_list_requests(parameters, headers):
    """
        :param headers:
        :param parameters:
        :return: str -> string formatted response message according to TOKDOC protocol
        """
    message = (
            START + CRLF + CRLF +
            START_METHOD +
            CRLF +
            DATA + SPACE + LIST + SPACE + parameters[constants.IP] + COLON + str(parameters[constants.PORT]) +
            CRLF +
            END_METHOD +
            CRLF + CRLF +
            START_HEADERS +
            CRLF +
            USER + COLON + headers[constants.USER] + CRLF +
            ACCESS_KEY + COLON + headers[constants.ACCESS_KEY] + CRLF
        )

    message += (
            END_HEADERS +
            CRLF + CRLF +
            START_FILE + CRLF +
            FILE_SIZE + COLON + '0' + CRLF +
            END_FILE +
            CRLF + CRLF +
            END
    )

    message_size = len(message.encode())
    message = (str(message_size) + (MESSAGE_SIZE_LENGTH - len(str(message_size))) * " " +
               CRLF + message)

    checksum = generate_checksum(message)
    return (checksum + CRLF + message).encode(), b''


def build_upload_requests(parameters: dict, headers: dict, filelocation: str):
    """
        :param filename:
        :param headers:
        :param parameters:
        :return: str -> string formatted response message according to TOKDOC protocol
        """

    file = b''
    filename = filelocation
    if '/' not in filelocation and '\\' not in filelocation:
        with open(os.getcwd() + '/' + filelocation, 'rb') as f:
            file = f.read()
            f.close()
    else:
        filelocation = filelocation.replace('\\','/')
        filename = filelocation[filelocation.rfind('/') + 1:]
        filelocation = filelocation[:filelocation.rfind('/') + 1]

        with open((filelocation + filename).replace('\\', '/'), 'rb') as f:
            file = f.read()
            f.close()

    message = (
            START +
            CRLF + CRLF +
            START_METHOD +
            CRLF +
            DATA + SPACE + UPLOAD + SPACE + parameters[constants.IP] + COLON + str(parameters[constants.PORT]) + SPACE + filename +
            CRLF +
            END_METHOD +
            CRLF + CRLF +
            START_HEADERS +
            CRLF +
            USER + COLON + headers[constants.USER] + CRLF +
            ACCESS_KEY + COLON + headers[constants.ACCESS_KEY] + CRLF
        )

    if constants.AUTHORIZED in headers:
        message += (
            AUTHORIZED + COLON + '('
        )
        emails_string = ''

        if headers[constants.USER] not in headers[constants.AUTHORIZED]:
            headers[constants.AUTHORIZED].append(headers[constants.USER])

        for email in headers[constants.AUTHORIZED]:
            emails_string += email + ','

        emails_string = emails_string.rstrip(',')
        message += (
            emails_string + ')' + CRLF
        )

    file_size = len(file)

    message += (
            END_HEADERS +
            CRLF + CRLF +
            START_FILE + CRLF +
            FILE_SIZE + COLON + str(file_size) + CRLF +
            END_FILE +
            CRLF + CRLF +
            END
    )

    message_size = len(message.encode())
    message = (str(message_size) + (MESSAGE_SIZE_LENGTH - len(str(message_size))) * " " +
               CRLF + message)

    checksum = generate_checksum(message)
    return (checksum + CRLF + message).encode(), file


def build_download_requests(parameters: dict, headers: dict, filename: str):
    """
        :param filename:
        :param headers:
        :param parameters:
        :return: str -> string formatted response message according to TOKDOC protocol
        """
    message = (
            START +
            CRLF + CRLF +
            START_METHOD +
            CRLF +
            DATA + SPACE + DOWNLOAD + SPACE + parameters[constants.IP] + COLON + str(parameters[constants.PORT]) + SPACE + filename +
            CRLF +
            END_METHOD +
            CRLF + CRLF +
            START_HEADERS +
            CRLF +
            USER + COLON + headers[constants.USER] + CRLF +
            ACCESS_KEY + COLON + headers[constants.ACCESS_KEY] + CRLF
        )

    file = b''

    file_size = len(file)

    message += (
            END_HEADERS +
            CRLF + CRLF +
            START_FILE + CRLF +
            FILE_SIZE + COLON + str(file_size) + CRLF +
            END_FILE +
            CRLF + CRLF +
            END
    )

    message_size = len(message.encode())
    message = (str(message_size) + (MESSAGE_SIZE_LENGTH - len(str(message_size))) * " " +
               CRLF + message)

    checksum = generate_checksum(message)
    return (checksum + CRLF + message).encode(), file

