
'''
A message consists of the following parts:
For "request" commands:
    - msg_header: str(utf-8, bytes)      i.e. "request"
    - msg_id: int(bytes)
    - command
    - command_argument 0
    - command_argument 1
    - ...
    - command_argument N
For "respond" commands:
    - msg_header: str(utf-8, bytes)      i.e. "respond"
    - msg_id: int(bytes)
    - command
    - command_argument 0
    - command_argument 1
    - ...
    - command_argument N
For "ping" commands:
    - msg_header: str(utf-8, bytes)      i.e. "ping"
For "pong" commands:
    - msg_header: str(utf-8, bytes)      i.e. "pong"
    
Each message section consists of the following components:
    - lendata: The length of the following message_section_content, 8 bytes from the high bit to the low bit.
    - message_section_content: The content of the message section.
'''

msg_headers = [
    "request",
    "respond",
    "ping",
    "pong"
]

commands = [
    '''
    Attain the version from the other host.
    Arguments:
    request:
        (no arguments)
    respond:
        0: str(utf-8) - The version.
    '''
    "get_version",

    '''
    Notify the other host to return the SHA-1 digest of the content of the given file back to this host.
    Arguments:
    request:
        0: str(utf-8) - The file's path.
    respond:
        0: str(utf-8) - The file's SHA-1 digest (hexadecimal). Filled with zero if the file does not exist.
    '''
    "get_file_content_sha1",

    '''
    Notify the other host that a file will begin to push.
    Arguments:
    request:
        0: str(utf-8) - The file's path.
        1: int(str(utf-8, bytes)) - The size (in bytes) of the data contained by this file to push.
        2: int(str(utf-8, bytes)) - The size (in bytes) of the data sent per time.
    respond:
        (no arguments)
    '''
    "file_push_begin",

    '''
    Push the data of the file mentioned just now.
    Arguments:
    request:
        0: bytes - The size of the data contained by this file to push.
    respond:
        (no arguments)
    '''
    "file_push_data",

    '''
    Notify the other host that a file will end its push.
    request:
        (no arguments)
    respond:
        (no arguments)
    '''
    "file_push_end",

    '''
    Notify the downloader that all tasks are done and the connection will come to end.
    Arguments:
    request:
        (no arguments)
    respond:
        (no arguments)
    '''
    "bye"
]

class Message():
    def __init__(self, msg_header: str, msg_id: int, command: str, command_arguments: tuple):
        self.msg_header = msg_header
        self.msg_id = msg_id
        self.command = command
        self.command_arguments = command_arguments
