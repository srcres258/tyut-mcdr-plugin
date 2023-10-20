
import threading
import time

from mcdreforged.api.all import *

from tyut_plugin.api.module import *
from tyut_plugin.api.util import *
from tyut_plugin.api.info import *

CLEAN_TIME: int = 60 * 10 # 10 min by default

class DustmanModule(ModuleBase):
    def __init__(self):
        super().__init__("dustman", name="服务器扫地大妈", msg_tag="扫地大妈", msg_tag_color=format.Color.DARK_PURPLE)

    def on_init(self):
        super().on_init()
        global instance
        instance = self

    def on_load(self, server: PluginServerInterface):
        super().on_load(server)
        self.sender_thread = DustmanTimerThread(self)
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

instance: DustmanModule = None

def _on_server_startup(server: PluginServerInterface):
    instance.sender_thread.exec_capable = True

def _on_server_stop(server: PluginServerInterface, exit_code: int):
    instance.sender_thread.exec_capable = False

class DustmanTimerThread(threading.Thread):
    def __init__(self, module: DustmanModule):
        super().__init__(name="{} DustmanTimerThread".format(constants.PLUGIN_ID))
        self.module = module
        self.running = True
        self.exec_capable = False
        self.time_left: int = CLEAN_TIME
        self.__notice_status = [False, False, False, False, False, False,
                                False, False, False, False, False, False]

    def __announce(self, time_info: str):
        msg = "{2}全服掉落物将在 {1}{0}{2} 后清除{3}".format(time_info, format.color_code[format.Color.RED], format.color_code[format.Color.WHITE], format.reset_code)
        self.module.broadcast_module_message(msg)

    def __do_clean(self):
        log.i("扫地大妈：正在清理全服掉落物")
        self.module.server.execute("kill @e[type=item]")
        self.module.broadcast_module_message("已清理全服掉落物")

    def run(self):
        while self.running:
            if self.exec_capable:
                if self.time_left <= 0:
                    self.__do_clean()
                    self.time_left = CLEAN_TIME
                    for i in range(len(self.__notice_status)):
                        self.__notice_status[i] = False
                elif self.time_left <= 1:
                    if not self.__notice_status[0]:
                        self.__announce("1秒")
                        self.__notice_status[0] = True
                elif self.time_left <= 2:
                    if not self.__notice_status[1]:
                        self.__announce("2秒")
                        self.__notice_status[1] = True
                elif self.time_left <= 3:
                    if not self.__notice_status[2]:
                        self.__announce("3秒")
                        self.__notice_status[2] = True
                elif self.time_left <= 4:
                    if not self.__notice_status[3]:
                        self.__announce("4秒")
                        self.__notice_status[3] = True
                elif self.time_left <= 5:
                    if not self.__notice_status[4]:
                        self.__announce("5秒")
                        self.__notice_status[4] = True
                elif self.time_left <= 10:
                    if not self.__notice_status[5]:
                        self.__announce("10秒")
                        self.__notice_status[5] = True
                elif self.time_left <= 20:
                    if not self.__notice_status[6]:
                        self.__announce("20秒")
                        self.__notice_status[6] = True
                elif self.time_left <= 30:
                    if not self.__notice_status[7]:
                        self.__announce("30秒")
                        self.__notice_status[7] = True
                elif self.time_left <= 60:
                    if not self.__notice_status[8]:
                        self.__announce("1分钟")
                        self.__notice_status[8] = True
                elif self.time_left <= 60 * 2:
                    if not self.__notice_status[9]:
                        self.__announce("2分钟")
                        self.__notice_status[9] = True
                elif self.time_left <= 60 * 5:
                    if not self.__notice_status[10]:
                        self.__announce("5分钟")
                        self.__notice_status[10] = True
                elif self.time_left <= 60 * 10:
                    if not self.__notice_status[11]:
                        self.__announce("10分钟")
                        self.__notice_status[11] = True


            time.sleep(1)
            self.time_left -= 1
