
import threading
import time

from mcdreforged.api.all import *

from tyut_plugin.api.module import *
from tyut_plugin.api.util import *
from tyut_plugin.api.info import *

class TimeAnnouncementModule(ModuleBase):
    def __init__(self):
        super().__init__("time_announcement", name="服务器报时", msg_tag="整点报时", msg_tag_color=format.Color.LIGHT_PURPLE)

    def on_init(self):
        super().on_init()
        global instance
        instance = self

    def on_load(self, server: PluginServerInterface):
        super().on_load(server)
        self.sender_thread = TimeAnnouncementThread(self)
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

instance: TimeAnnouncementModule = None

def _on_server_startup(server: PluginServerInterface):
    instance.sender_thread.exec_capable = True

def _on_server_stop(server: PluginServerInterface, exit_code: int):
    instance.sender_thread.exec_capable = False

class TimeAnnouncementThread(threading.Thread):
    def __init__(self, module: TimeAnnouncementModule):
        super().__init__(name="{} TimeAnnouncementThread".format(constants.PLUGIN_ID))
        self.module = module
        self.running = True
        self.exec_capable = False
        self.loop_sleep_period = 1
        self.time_passed = 0

    def run(self):
        while self.running:
            if self.exec_capable:
                cur_time = time.localtime()
                if cur_time.tm_min == 0 and cur_time.tm_sec == 0:
                    msg = format.color_code[format.Color.YELLOW]
                    msg += "呆梨娘为您报时，现在是 {0}{1}{2} 时整".format(format.color_code[format.Color.GOLD], cur_time.tm_hour, format.color_code[format.Color.YELLOW])
                    msg += format.reset_code
                    self.module.broadcast_module_message(msg)

            time.sleep(self.loop_sleep_period)
