import os
import time
from socket import *
from Utilities.test_functions import test_message
from Utilities import message_serializer
from Utilities import message_parser
from Utilities import constants

CHECKSUM_CRLF_LENGTH = 66
MESSAGE_SIZE_CRLF_LENGTH = 18
DEFAULT_BUFFER = 1024
my_access_key = ' '


def receive_message(connection_socket):
    checksum = connection_socket.recv(CHECKSUM_CRLF_LENGTH)  # checksum + CRLF
    message_size = connection_socket.recv(MESSAGE_SIZE_CRLF_LENGTH)  # message size + CRLF
    message = b''

    while len(message) < int(message_size.decode().strip()):
        message += connection_socket.recv(int(message_size.decode()))  # receive the rest of the message

    return checksum + message_size + message, checksum.decode()[
                                              :-2].encode(), message_size + message  # message that was sent


def save_file(client_socket, filename, filesize):
    file = b''

    while len(file) < filesize:
        file += client_socket.recv(DEFAULT_BUFFER)

    saved = open(filename, 'wb')
    saved.write(file)
    saved.close()


def get_list(client_socket, filesize):
    text_bytes = b''

    while len(text_bytes) < filesize - 2:
        text_bytes += client_socket.recv(DEFAULT_BUFFER)

    text_string = text_bytes.decode()
    return text_string.split('\r\n')


def request(client_socket: socket, request_type: str, parameters: dict = {}, headers: dict = {}, filename: str = ''):
    """Facilitates request and responses to and from the server"""
    global my_access_key

    # sending data over the socket
    message = b''
    content = b''

    if request_type == constants.AUTH:
        message, content = message_serializer.build_auth_requests(
            parameters=parameters
        )
    elif request_type == constants.LIST:
        message, content = message_serializer.build_list_requests(
            parameters=parameters,
            headers=headers
        )
    elif request_type == constants.UPLOAD:
        message, content = message_serializer.build_upload_requests(
            parameters=parameters,
            headers=headers,
            filelocation=filename
        )
    elif request_type == constants.DOWNLOAD:
        message, content = message_serializer.build_download_requests(
            parameters=parameters,
            headers=headers,
            filename=filename
        )
    elif request_type == constants.EXIT:
        message, content = message_serializer.build_exit_requests()
        my_access_key = ' '

    # send to socket
    client_socket.send(message)
    client_socket.send(content)

    # receive from socket
    try:
        full_message, checksum, message_no_checksum = receive_message(client_socket)
        parsed = message_parser.parse_message(full_message)
    except:
        return 500, '', ' '

    returned_content = ''
    if request_type == constants.AUTH and parsed['response']['status_code'] == 201:
        my_access_key = parsed['response']['access_key']
    elif request_type == constants.DOWNLOAD and parsed['response']['status_code'] == 201:
        save_file(client_socket, filename, parsed['response']['file_size'])
    elif request_type == constants.LIST and parsed['response']['status_code'] == 201:
        returned_content = get_list(client_socket, parsed['response']['file_size'])
    elif request_type == constants.EXIT and parsed['response']['status_code'] == 201:
        returned_content = True

    status_code = parsed['response']['status_code']

    return status_code, returned_content, my_access_key
