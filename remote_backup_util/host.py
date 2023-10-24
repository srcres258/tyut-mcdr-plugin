
import abc
import threading

from remote_backup_util import messenger, message, constants, exception

class Host(abc.ABC):
    def __init__(self, ip: str = "localhost", port: int = 14285, async_exec: bool = True):
        self.ip = ip
        self.port = port
        self.messenger = messenger.Messenger(ip, port)
        self.host_thread = None
        if async_exec:
            self.host_thread = HostThread(self)
        self.cur_msg_id = 0

    @abc.abstractmethod
    def init_messenger(self):
        pass

    @abc.abstractmethod
    def do_messenging(self):
        pass

    def start_messenger(self):
        if self.host_thread:
            self.host_thread.start()
        else:
            self.exec_messenger()

    def exec_messenger(self):
        self.messenger.send_message(message.Message("request", self.next_msg_id(), "get_version", tuple()))
        get_version_replied = False
        replied_version = ""
        while not get_version_replied:
            ver_msg = self.messenger.recv_message()
            if ver_msg.command == "get_version":
                match ver_msg.msg_header:
                    case "request":
                        self.messenger.send_message(message.Message("respond", self.next_msg_id(), "get_version", (constants.VERSION,)))
                    case "respond":
                        replied_version = ver_msg.command_arguments[0]
                        get_version_replied = True
        if replied_version != constants.VERSION:
            raise exception.IllegalVersionException(ver_msg.command_arguments[0], constants.VERSION)
        self.do_messenging()
    
    def next_msg_id(self) -> int:
        msg_id = self.cur_msg_id
        self.cur_msg_id += 1
        return msg_id

class HostThread(threading.Thread):
    def __init__(self, host: Host) -> None:
        super().__init__(name="remote_backup_util HostThread")
        self.host = host

    def run(self):
        self.host.exec_messenger()

class ServerHost(Host):
    def init_messenger(self):
        self.messenger.socket_accept()

class ClientHost(Host):
    def init_messenger(self):
        self.messenger.socket_bind()
