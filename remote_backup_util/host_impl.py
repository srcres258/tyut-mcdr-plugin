
from remote_backup_util import messenger, message, constants, exception, host

class SimpleServerHost(host.ServerHost):
    def __init__(self, messenging_callback, ip: str = "localhost", port: int = 14285, async_exec: bool = True):
        super().__init__(ip, port, async_exec)
        self.messenging_callback = messenging_callback

    def do_messenging(self):
        self.messenging_callback(self)

class SimpleClientHost(host.ClientHost):
    def __init__(self, messenging_callback, ip: str = "localhost", port: int = 14285, async_exec: bool = True):
        super().__init__(ip, port, async_exec)
        self.messenging_callback = messenging_callback

    def do_messenging(self):
        self.messenging_callback(self)
