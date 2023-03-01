import datetime
import hashlib
import os
import platform

import Utilities.message_serializer as message_serializer

from socket import *

from Utilities import constants
from Utilities.test_functions import test_message

serverName = 'localhost'  # e.g. 127.0.0.1 or www.google.com (in which case a DNS lookup will be automatically performed to get IP)
serverPort = 3000  # e.g. 3000

# creating a socket
client_socket = socket(AF_INET, SOCK_STREAM)
# AF_INET -> indicates the underlying network is using IPv4
# SOCK_STREAM -> TCP socket

# initiates the TCP connection
client_socket.connect((serverName, serverPort))


# sending data over the socket
data = test_message()
file = open('./Utilities/test.png', 'rb').read()

client_socket.send(data.encode())
client_socket.send(file)

# receiving data from the socket
# response = client_socket.recv(buffer_size_to_read_into)

# closing the socket
client_socket.close()