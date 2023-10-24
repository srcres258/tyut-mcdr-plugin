
import socket

from remote_backup_util import message

class Messenger():
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.comm_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.target_socket: socket.socket = None
        self.target_addr: socket._RetAddress = None
    
    def socket_accept(self):
        self.comm_socket.bind((self.ip, self.port))
        self.comm_socket.listen(1)
        self.target_socket, self.target_addr = self.comm_socket.accept()
    
    def socket_bind(self):
        self.comm_socket.connect((self.ip, self.port))
        self.target_socket = self.comm_socket
    
    def send_data(self, data: bytes):
        lendata = len(data).to_bytes(8, "big")
        self.target_socket.send(lendata)
        self.target_socket.send(data)
    
    def send_str_utf8(self, st: str):
        st_data = st.encode("utf-8")
        self.send_data(st_data)
    
    def send_int_str_utf8(self, i: int):
        self.send_str_utf8(str(i))

    def __recv_data(self, length: int = 0) -> bytes:
        result = b''
        remaining = length
        while remaining > 0:
            data = self.target_socket.recv(length)
            result += data
            remaining -= len(data)
        return result

    def recv_data(self) -> bytes:
        lendata = self.target_socket.recv(8)
        my_len = int.from_bytes(lendata, "big")
        return self.__recv_data(my_len)
    
    def recv_str_utf8(self) -> str:
        return self.recv_data().decode("utf-8")
    
    def recv_int_str_utf8(self) -> int:
        return int(self.recv_str_utf8())

    def send_message(self, msg: message.Message):
        self.send_str_utf8(msg.msg_header)
        self.send_int_str_utf8(msg.msg_id)
        match msg.msg_header:
            case "request":
                self.send_str_utf8(msg.command)
                match msg.command:
                    case "get_version":
                        pass
                    case "get_file_content_sha1":
                        self.send_str_utf8(msg.command_arguments[0])
                    case "file_push_begin":
                        self.send_str_utf8(msg.command_arguments[0])
                        self.send_int_str_utf8(msg.command_arguments[1])
                        self.send_int_str_utf8(msg.command_arguments[2])
                    case "file_push_data":
                        self.send_data(msg.command_arguments[0])
                    case "file_push_end":
                        pass
                    case "bye":
                        pass
            case "respond":
                self.send_str_utf8(msg.command)
                match msg.command:
                    case "get_version":
                        self.send_str_utf8(msg.command_arguments[0])
                    case "get_file_content_sha1":
                        self.send_str_utf8(msg.command_arguments[0])
                    case "file_push_begin":
                        pass
                    case "file_push_data":
                        pass
                    case "file_push_end":
                        pass
                    case "bye":
                        pass
            case "ping":
                pass
            case "pong":
                pass
    
    def recv_message(self) -> message.Message:
        msg_header = self.recv_str_utf8()
        msg_id = self.recv_int_str_utf8()
        match msg_header:
            case "request":
                command = self.recv_str_utf8()
                command_arguments = []
                match command:
                    case "get_version":
                        pass
                    case "get_file_content_sha1":
                        command_arguments.append(self.recv_str_utf8())
                    case "file_push_begin":
                        command_arguments.append(self.recv_str_utf8())
                        command_arguments.append(self.recv_int_str_utf8())
                        command_arguments.append(self.recv_int_str_utf8())
                    case "file_push_data":
                        command_arguments.append(self.recv_data())
                    case "file_push_end":
                        pass
                    case "bye":
                        pass
                return message.Message(msg_header, msg_id, command, (*command_arguments,))
            case "respond":
                command = self.recv_str_utf8()
                command_arguments = []
                match command:
                    case "get_version":
                        command_arguments.append(self.recv_str_utf8())
                    case "get_file_content_sha1":
                        command_arguments.append(self.recv_str_utf8())
                    case "file_push_begin":
                        pass
                    case "file_push_data":
                        pass
                    case "file_push_end":
                        pass
                    case "bye":
                        pass
                return message.Message(msg_header, msg_id, command, (*command_arguments,))
            case "ping":
                return message.Message(msg_header, msg_id, "", tuple())
            case "pong":
                return message.Message(msg_header, msg_id, "", tuple())
