import os
import sys
import time
from socket import *
import pwinput
import getpass
from termcolor import colored

from RequestHandler import request, my_access_key
from Utilities import constants

serverName = 'localhost'  # e.g. 127.0.0.1 or www.google.com (in which case a DNS lookup will be automatically performed to get IP)
serverPort = 3000  # e.g. 3000
addressed, connected = False, False
client_socket = None
user_email = None
access_key = None


def list_request():
    return request(client_socket, constants.LIST,
                   parameters={constants.IP: serverName, constants.PORT: serverPort},
                   headers={constants.USER: user_email, constants.ACCESS_KEY: access_key},
                   filename=''
                   )


def auth_request(email, password):
    return request(client_socket, constants.AUTH,
                   parameters={constants.EMAIL: email, constants.PASSWORD: password, constants.IP: serverName,
                               constants.PORT: serverPort},
                   headers={},
                   filename=''
                   )


def exit_request():
    return request(client_socket, request_type=constants.EXIT)


def upload_request(file_location, authorized: list = None):
    head = {constants.USER: user_email, constants.ACCESS_KEY: access_key}
    if authorized is not None and len(authorized) > 0:
        # file is protected
        head[constants.AUTHORIZED] = authorized
    return request(client_socket, constants.UPLOAD,
                   parameters={constants.IP: serverName, constants.PORT: serverPort},
                   headers=head,
                   filename=file_location
                   )


def download_request(filename):
    return request(client_socket, constants.DOWNLOAD,
                   parameters={constants.IP: serverName, constants.PORT: serverPort},
                   headers={constants.USER: user_email, constants.ACCESS_KEY: access_key},
                   filename=filename
                   )


def main():
    """Receive input from user and handle them"""
    global serverName, serverPort, addressed, client_socket, connected, user_email, access_key
    user_input = ''

    # app lifecycle
    while user_input != constants.EXIT:
        # prompting and getting components from input
        user_input = input(colored('TOKDOC $', 'blue', attrs=['bold', 'reverse']) + ' ')
        input_list = user_input.split(' ')
        input_list[0] = input_list[0].upper()
        status_code = -1

        # incomplete command
        if len(input_list) < 2 and input_list[0] != 'DISCONNECT' and input_list[0] != constants.EXIT and input_list[
            0] != constants.LIST and input_list[0] != 'HELP':
            print(colored('Missing arguments', 'red'))
            continue

        if input_list[0] == 'HELP':
            def command_text(text):
                return colored(text, 'light_magenta', attrs=['bold'])

            print(f"""
connect -> auth -> data request -> disconnect -> exit
Do not include <> in commands.

> {command_text('help')} \t\t\t\t\t\t returns a list of commands and their functions

> {command_text('connect <ip>:<port>')} \t\t\t\t connect to the specified server
> {command_text('disconnect')} \t\t\t\t\t sign out and gracefully disconnect from the server

Control Requests
> {command_text('auth <username>')} \t\t\t\t log in to the specified account

Data requests
> {command_text('list')} \t\t\t\t\t\t list all accessible files
> {command_text('download <filename>')} \t\t\t\t download the specified file
> {command_text('upload <filepath>')} \t\t\t\t upload the specified file and mark as public
> {command_text('upload <filepath> <email>,<email>,...')} \t upload the specified file give access to the specified emails
                """
                  )
            continue

        # send connect request
        if input_list[0] == 'CONNECT':

            # server name and port missing or too many arguments
            if len(input_list) != 2:
                print(colored('Provide a server name and port in the format <name>:<port>', 'red'))
                continue

            server_address = input_list[1].split(':')

            # server name or port missing or too many arguments
            if len(server_address) != 2:
                print(colored('Provide a server name and port in the format <name>:<port>', 'red'))
                continue

            # getting server details
            serverName = server_address[0]
            serverPort = int(server_address[1])
            addressed = True

            # creating a socket
            client_socket = socket(AF_INET, SOCK_STREAM)
            # initiates the TCP connection
            try:
                client_socket.connect((serverName, serverPort))
                connected = True
                print(colored('Connected to:' + serverName + ":" + str(serverPort), 'green'))
                continue
            except ConnectionRefusedError as e:
                print(colored('Connection to server refused. Ensure IP and Port are correct', 'red'))
                continue
            except Exception as e:
                raise e

        # send auth command
        if input_list[0] == constants.AUTH:
            email = input_list[1]
            response_code = 501

            # works in fully fledged terminal
            password = pwinput.pwinput(prompt='Password: ', mask='*')
            # works in all run environments
            # password = getpass.getpass('Password: ')

            # send request and capture response_code
            response_code, content, key = auth_request(email, password)
            if int(response_code) == 201:
                user_email = email
                access_key = key

                print('\033[F' + colored('Logged in successfully', 'green'))
            elif int(response_code) == 501:
                print('\033[F' + colored('Password incorrect, please try again.', 'red'))
            elif int(response_code) == 503:
                print('\033[F' + colored('Error in signing up.', 'red'))
            else:
                print('\033[F' + colored('Error: ' + str(status_code), 'red'))
            continue
        # send exit request
        if input_list[0] == 'DISCONNECT':
            if connected:
                connected = False
                response_code, temp, temp = exit_request()
                # reset access key
                access_key = ' '

                if int(response_code) == 201:
                    print('\033[F' + colored('Disconnected', 'green'))
                else:
                    print('\033[F' + colored('Error: ' + str(status_code), 'red'))
            else:
                print('\033[F' + colored('Client is already disconnected', 'green'))
            continue

        # stop the program
        if input_list[0].upper() == 'EXIT':
            if connected:
                connected = False
                user_input = constants.EXIT
                exit_request()
            else:
                connected = False
                user_input = constants.EXIT
            continue

        # general errors
        if not connected:
            print(colored('Client not connected. Use CONNECT command', 'red'))
            continue
        if connected and (access_key is None or len(access_key.strip(' ')) == 0):
            print(colored('Client not authenticated. Use AUTH command to log in', 'red'))
            continue

        # send list request
        if input_list[0] == constants.LIST:

            status_code, content, temp = list_request()

            if int(status_code) == 201:
                # print all the files
                files_list_string = ''

                for file in content:
                    files_list_string += file + '\n'

                files_list_string = files_list_string.rstrip('\n')

                print('\033[F' + colored(files_list_string, 'yellow'))
            else:
                print('\033[F' + colored('Error: ' + str(status_code), 'red'))
            continue

        # send upload request
        if input_list[0] == constants.UPLOAD:
            try:
                # try read the file from the client machine and upload it
                if len(input_list) == 3:
                    # protected file
                    status_code, content, temp = upload_request(input_list[1].strip('"'), input_list[2].split(','))
                else:
                    # public file
                    status_code, content, temp = upload_request(input_list[1].strip('"'))
            except FileNotFoundError as e:
                print(colored('File not found', 'red'))

            if int(status_code) == 201:
                print('\033[F' + colored('Successfully uploaded', 'green'))
            elif int(status_code) == 505:
                print('\033[F' + colored('Some or all authorized users do not exist', 'red'))
            else:
                print(colored('error: ' + str(status_code), 'red'))
            continue

        # send download request
        if input_list[0] == constants.DOWNLOAD:
            status_code, content, temp = download_request(input_list[1].strip('"'))

            if int(status_code) == 201:
                print('\033[F' + colored('Successfully downloaded', 'green'))
            elif int(status_code) == 302:
                print('\033[F' + colored('Access denied', 'red'))
            elif int(status_code) == 301:
                print('\033[F' + colored('File not found', 'red'))
            else:
                print('\033[F' + colored('Error: ' + str(status_code), 'red'))
            continue


def test():
    """Used for testing"""
    # creating a socket
    client_socket = socket(AF_INET, SOCK_STREAM)
    # AF_INET -> indicates the underlying network is using IPv4
    # SOCK_STREAM -> TCP socket

    # initiates the TCP connection
    client_socket.connect((serverName, serverPort))

    # request(client_socket, constants.AUTH,
    #         parameters={constants.EMAIL: 'test@test.com', constants.PASSWORD: 't', constants.IP: '127.0.0.1',
    #                     constants.PORT: '3000'},
    #         headers={constants.USER: 'test@test.com'},
    #         filename='Networks_Assignment_1.pdf'
    #         )
    time.sleep(2)
    request(client_socket, constants.UPLOAD,
            parameters={constants.IP: '127.0.0.1', constants.PORT: '3000'},
            headers={constants.USER: 'test@test.com', constants.ACCESS_KEY: my_access_key},
            filename='Networks_Assignment_1.pdf'
            )
    time.sleep(2)

    print(request(client_socket, constants.LIST,
                  parameters={constants.IP: '127.0.0.1', constants.PORT: '3000'},
                  headers={constants.USER: 'test@test.com', constants.ACCESS_KEY: my_access_key},
                  filename='Networks_Assignment_1.pdf'
                  ))
    time.sleep(2)

    request(client_socket, constants.DOWNLOAD,
            parameters={constants.IP: '127.0.0.1', constants.PORT: '3000'},
            headers={constants.USER: 'test@test.com', constants.ACCESS_KEY: my_access_key},
            filename='Networks_Assignment_1.pdf'
            )
    time.sleep(2)

    ex = request(client_socket, request_type=constants.EXIT)

    time.sleep(2)

    request(client_socket, constants.DOWNLOAD,
            parameters={constants.IP: '127.0.0.1', constants.PORT: '3000'},
            headers={constants.USER: 'test@test.com', constants.ACCESS_KEY: my_access_key},
            filename='Networks_Assignment_1.pdf'
            )

    if ex:
        # closing the socket
        client_socket.close()


if __name__ == '__main__':
    os.system('color')
    main()
