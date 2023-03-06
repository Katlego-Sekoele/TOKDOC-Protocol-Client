from Utilities import constants
import shlex

def parse_message(message):
    message = stringify(message)

    checksum = get_checksum(message)
    message_size = get_message_size(message)
    parsed_response = get_parsed_response_content(message)

    return {
        constants.CHECKSUM_KEY: checksum,
        constants.MESSAGE_SIZE_KEY: message_size,
        constants.RESPONSE_KEY: parsed_response
    }


def get_checksum(message):
    return stringify(message)[:64]


def get_message_content(message) -> str:
    """
    :param message:
    :return: str -> the message content excluding the checksum and message size
    """
    message = stringify(message)
    size = get_message_size(message)
    offset = constants.CHECKSUM_LENGTH + constants.CRLF_LENGTH + constants.MESSAGE_SIZE_LENGTH + constants.CRLF_LENGTH
    return message[offset: offset + constants.CRLF_LENGTH + size]


def get_parsed_response_content(message) -> dict:
    """
    :param message:
    :return: str -> the message response content included in the {{START RESPONSE}}, {{END RESPONSE}}
    parsed into a dictionary
    """
    message = stringify(message)
    start = message.index(constants.START_RESPONSE) + len(constants.START_RESPONSE)
    end = message.index(constants.END_RESPONSE)
    content = message[start: end].strip('\r\n')

    content_list = shlex.split(content)

    content_dict = {
        constants.STATUS_CODE_KEY: int(content_list[0]),
        constants.STATUS_MESSAGE_KEY: content_list[1],
    }

    print()

    try:
        content_dict[constants.FILE_SIZE_KEY] = int(content_list[2])
    except ValueError:
        content_dict[constants.ACCESS_KEY_KEY] = content_list[2]

    return content_dict


def get_message_size(message) -> int:
    """
    :param message:
    :return: int -> message size as provided in the message
    """
    message = stringify(message)
    return int(message[
               constants.CHECKSUM_LENGTH + constants.CRLF_LENGTH:constants.CHECKSUM_LENGTH + constants.CRLF_LENGTH + constants.MESSAGE_SIZE_LENGTH].strip())


def stringify(message):
    """
        :param message: string or bytes of the message
        :return: the string formatted message
        """
    if isinstance(message, bytes):
        return bytes(message).decode()
    elif isinstance(message, str):
        return message
    else:
        raise TypeError('The message must either be of type bytes or string. You message was type', type(message))
