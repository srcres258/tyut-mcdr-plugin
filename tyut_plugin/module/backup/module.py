
import threading
import time

from mcdreforged.api.all import *

from tyut_plugin.api.module import *
from tyut_plugin.api.util import *
from tyut_plugin.api.info import *
from tyut_plugin.api.type import *

def __time_of(hour: int, min: int, sec: int) -> time.struct_time:
    result = to_mutable_struct_time(time.localtime())
    result.tm_hour = hour
    result.tm_min = min
    result.tm_sec = sec
    result = to_struct_time(result)
    return result

BACKUP_TIME_LIST = [
    __time_of(14, 0, 0),
    __time_of(22, 0, 0)
]

class BackupModule(ModuleBase):
    def __init__(self):
        super().__init__("backup", name="服务器备份", msg_tag="备份", msg_tag_color=format.Color.DARK_RED)

    def on_init(self):
        super().on_init()
        global instance
        instance = self

    def on_load(self, server: PluginServerInterface):
        super().on_load(server)
        self.sender_thread = BackupTimerThread(self)
        self.sender_thread.daemon = True
        self.sender_thread.start()

    def on_unload(self, server: PluginServerInterface):
        super().on_unload(server)
        self.sender_thread.running = False

    def on_stop(self):
        super().on_stop()
        global instance
        instance = None

instance: BackupModule = None

def __get_next_restart_time_rough(cur_time: time.struct_time) -> time.struct_time:
    for t in BACKUP_TIME_LIST:
        t2 = to_mutable_struct_time(cur_time)
        t2.tm_hour = t.tm_hour
        t2.tm_min = t.tm_min
        t2.tm_sec = t.tm_sec
        t2 = to_struct_time(t2)
        cur_time_n = time.mktime(cur_time)
        t2_n = time.mktime(t2)
        if cur_time_n < t2_n:
            return t2
    return None

def _get_next_restart_time(cur_time: time.struct_time) -> time.struct_time:
    result = __get_next_restart_time_rough(cur_time)
    if result is None:
        cur_time_n = time.mktime(cur_time)
        cur_time_n += 60.0 * 60 * 24
        cur_time_2 = time.localtime(cur_time_n)
        cur_time_2 = to_mutable_struct_time(cur_time_2)
        cur_time_2.tm_hour = cur_time_2.tm_min = cur_time_2.tm_sec = 0
        cur_time_2 = to_struct_time(cur_time_2)
        return __get_next_restart_time_rough(cur_time_2)
    else:
        return result

class BackupTimerThread(threading.Thread):
    def __init__(self, module: BackupModule):
        super().__init__(name="{} BackupTimerThread".format(constants.PLUGIN_ID))
        self.module = module
        self.running = True
        self.loop_sleep_period = 1
        self.time_passed = 0
        self.backup_time = _get_next_restart_time(time.localtime())
        self.__notice_status = [False, False, False, False, False, False,
                                False, False, False, False, False, False]

    def __broadcast_backup_message(self, backup_time: time.struct_time, info: str):
        msg = format.color_code[format.Color.YELLOW]
        msg += "服务器将在{4}{0}:{1}:{2}{5}进行备份，距离备份开始还有{4}{3}{5}。".format(
            "%02d" % backup_time.tm_hour, "%02d" % backup_time.tm_min, "%02d" % backup_time.tm_sec, info, format.color_code[format.Color.RED], format.color_code[format.Color.YELLOW]
        )
        msg += format.reset_code
        self.module.broadcast_module_message(msg)

    def __do_restart(self):
        self.module.server.restart()

    def run(self):
        while self.running:
            cur_time = time.localtime()
            delta = time.mktime(self.backup_time) - time.mktime(cur_time)

            if self.module.server.is_server_startup():
                if delta <= 0:
                    log.i("定时备份：开始备份")
                    self.__do_restart()
                    self.backup_time = _get_next_restart_time(time.localtime())
                    for i in range(len(self.__notice_status)):
                        self.__notice_status[i] = False
                elif delta <= 1.0:
                    if not self.__notice_status[0]:
                        self.__broadcast_backup_message(self.backup_time, "1秒")
                        self.__notice_status[0] = True
                elif delta <= 2.0:
                    if not self.__notice_status[1]:
                        self.__broadcast_backup_message(self.backup_time, "2秒")
                        self.__notice_status[1] = True
                elif delta <= 3.0:
                    if not self.__notice_status[2]:
                        self.__broadcast_backup_message(self.backup_time, "3秒")
                        self.__notice_status[2] = True
                elif delta <= 5.0:
                    if not self.__notice_status[3]:
                        self.__broadcast_backup_message(self.backup_time, "5秒")
                        self.__notice_status[3] = True
                elif delta <= 10.0:
                    if not self.__notice_status[4]:
                        self.__broadcast_backup_message(self.backup_time, "10秒")
                        self.__notice_status[4] = True
                elif delta <= 30.0:
                    if not self.__notice_status[5]:
                        self.__broadcast_backup_message(self.backup_time, "30秒")
                        self.__notice_status[5] = True
                elif delta <= 60.0:
                    if not self.__notice_status[6]:
                        self.__broadcast_backup_message(self.backup_time, "1分钟")
                        self.__notice_status[6] = True
                elif delta <= 60.0 * 2:
                    if not self.__notice_status[7]:
                        self.__broadcast_backup_message(self.backup_time, "2分钟")
                        self.__notice_status[7] = True
                elif delta <= 60.0 * 5:
                    if not self.__notice_status[8]:
                        self.__broadcast_backup_message(self.backup_time, "5分钟")
                        self.__notice_status[8] = True
                elif delta <= 60.0 * 10:
                    if not self.__notice_status[9]:
                        self.__broadcast_backup_message(self.backup_time, "10分钟")
                        self.__notice_status[9] = True
                elif delta <= 60.0 * 30:
                    if not self.__notice_status[10]:
                        self.__broadcast_backup_message(self.backup_time, "30分钟")
                        self.__notice_status[10] = True
                elif delta <= 60.0 * 60:
                    if not self.__notice_status[11]:
                        self.__broadcast_backup_message(self.backup_time, "1小时")
                        self.__notice_status[11] = True

            time.sleep(self.loop_sleep_period)
