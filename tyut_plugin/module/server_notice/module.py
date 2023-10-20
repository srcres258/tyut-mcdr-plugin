
import threading
import time
import random

from mcdreforged.api.all import *

from tyut_plugin.api.module import *
from tyut_plugin.api.util import *
from tyut_plugin.api.info import *

NOTICE_PERIOD_TIME: float = 60 * 5 # Unit: second(s)
NOTICE_CONTENTS: list[str] = [
    "欢迎加入TYUT呆梨服官方QQ群：681874322。",
    "服务器维护需要高昂成本，如有条件可适当捐助以维持服务器运行，感谢您的支持。",
    "服务器将于每日14点整和22点整定时重启以保证运行流畅，请提前做好准备以避免意外情况。",
]

class ServerNoticeModule(ModuleBase):
    def __init__(self):
        super().__init__("server_notice", name="服务器公告", msg_tag="公告", msg_tag_color=format.Color.YELLOW)

    def on_init(self):
        super().on_init()
        global instance
        instance = self

    def on_load(self, server: PluginServerInterface):
        super().on_load(server)
        self.sender_thread = NoticeSenderThread(self)
        server.register_event_listener('mcdr.server_startup', _on_server_startup)
        server.register_event_listener('mcdr.server_stop', _on_server_stop)
        self.sender_thread.daemon = True
        self.sender_thread.start()
        if server.is_server_startup():
            self.sender_thread.exec_capable = True

    def on_unload(self, server: PluginServerInterface):
        super().on_unload(server)
        self.sender_thread.running = False

    def on_stop(self):
        super().on_stop()
        global instance
        instance = None

instance: ServerNoticeModule = None

def _on_server_startup(server: PluginServerInterface):
    instance.sender_thread.exec_capable = True

def _on_server_stop(server: PluginServerInterface, exit_code: int):
    instance.sender_thread.exec_capable = False

class NoticeSenderThread(threading.Thread):
    def __init__(self, module: ServerNoticeModule):
        super().__init__(name="{} NoticeSenderThread".format(constants.PLUGIN_ID))
        self.module = module
        self.running = True
        self.exec_capable = False
        self.loop_sleep_period = 1
        self.time_passed = 0
        self.time_capable = False

    def run(self):
        while self.running:
            if self.exec_capable and self.time_capable:
                self.time_capable = False

                msg = random.choice(NOTICE_CONTENTS)
                self.module.broadcast_module_message(msg)

            time.sleep(self.loop_sleep_period)
            self.time_passed += self.loop_sleep_period
            if self.time_passed >= NOTICE_PERIOD_TIME:
                self.time_passed = 0
                self.time_capable = True
