
import threading
import time
import os

from mcdreforged.api.all import *
from mcdreforged.api.all import Literal

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

class MaintenanceNoticeModule(ModuleBase):
    def __init__(self):
        super().__init__("maintenance_notice", name="服务器维护公告", msg_tag="服务器维护", msg_tag_color=format.Color.DARK_RED)

    def on_init(self):
        super().on_init()
        global instance
        instance = self

    def on_load(self, server: PluginServerInterface):
        super().on_load(server)
        self.sender_thread = MaintenanceTimerThread(self)
        self.sender_thread.daemon = True
        self.sender_thread.start()

    def on_register_command(self, prefix_cmd: Literal):
        super().on_register_command(prefix_cmd)
        cmd = Literal('scdmnt')\
            .requires(lambda src: src.has_permission_higher_than(3))\
            .runs(_on_schedule_stop)
        prefix_cmd.then(cmd)

    def on_unload(self, server: PluginServerInterface):
        super().on_unload(server)
        self.sender_thread.running = False

    def on_stop(self):
        super().on_stop()
        global instance
        instance = None

instance: MaintenanceNoticeModule = None

def __get_maintenance_time(psi: PluginServerInterface) -> time.struct_time:
    time_str = ""
    with open(os.path.join(psi.get_data_folder(), "mt_time.txt"), 'r', encoding='utf-8') as f:
        time_str = f.read()
    st = time.strptime(time_str, "%H:%M:%S")
    result = to_mutable_struct_time(time.localtime())
    result.tm_hour = st.tm_hour
    result.tm_min = st.tm_min
    result.tm_sec = st.tm_sec
    result = to_struct_time(result)
    return result

def __get_maintenance_reason(psi: PluginServerInterface) -> str:
    reason_str = ""
    with open(os.path.join(psi.get_data_folder(), "mt_reason.txt"), 'r', encoding='utf-8') as f:
        reason_str = f.read()
    return reason_str

def _on_schedule_stop(src: CommandSource):
    # Ensure the permission again
    if src.has_permission_higher_than(3):
        time = __get_maintenance_time(src.get_server().as_plugin_server_interface())
        reason = __get_maintenance_reason(src.get_server().as_plugin_server_interface())
        instance.sender_thread.schedule_stop(time, reason)

class MaintenanceTimerThread(threading.Thread):
    def __init__(self, module: MaintenanceNoticeModule):
        super().__init__(name="{} RestartTimerThread".format(constants.PLUGIN_ID))
        self.module = module
        self.running = True
        self.loop_sleep_period = 1
        self.time_passed = 0
        self.stop_time: time.struct_time = None
        self.stop_reason: str = "未指定"
        self.__notice_status = [False, False, False, False, False, False,
                                False, False, False, False, False, False]

    def __announce_schedule_stop_message(self, stop_time: time.struct_time):
        msg = format.color_code[format.Color.YELLOW]
        msg += "已设置维护计划：服务器将于"
        msg += format.color_code[format.Color.RED]
        msg += "{}:{}:{}".format("%02d" % stop_time.tm_hour, "%02d" % stop_time.tm_min, "%02d" % stop_time.tm_sec)
        msg += format.color_code[format.Color.YELLOW]
        msg += "关闭以进行维护，原因："
        msg += format.reset_code
        msg += self.stop_reason
        msg += format.reset_code
        self.module.broadcast_module_message(msg)
        self.module.broadcast_module_message("请合理安排时间，及时下线。")

    def __broadcast_stop_message(self, info: str):
        msg = format.color_code[format.Color.YELLOW]
        msg += "服务器将在{4}{0}:{1}:{2}{5}关闭，距离关闭还有{4}{3}{5}，原因：{6}{7}".format(
            "%02d" % self.stop_time.tm_hour, "%02d" % self.stop_time.tm_min, "%02d" % self.stop_time.tm_sec, info,
            format.color_code[format.Color.RED], format.color_code[format.Color.YELLOW], format.reset_code,
            self.stop_reason
        )
        msg += format.reset_code
        self.module.broadcast_module_message(msg)

    def __do_stop(self):
        log.i("服务器维护：即将停止服务器和MCDR")
        self.module.server.stop_exit()

    def schedule_stop(self, stop_time: time.struct_time, reason: str):
        if len(reason) == 0:
            reason = "未指定"
        self.stop_reason = reason
        self.stop_time = stop_time
        self.__announce_schedule_stop_message(stop_time)

    def run(self):
        while self.running:
            if self.module.server.is_server_startup() and not self.stop_time is None:
                cur_time = time.localtime()
                delta = time.mktime(self.stop_time) - time.mktime(cur_time)

                if delta <= 0:
                    log.i("服务器维护：已发送服务器停止命令")
                    self.__do_stop()
                    self.stop_time = None
                    self.stop_reason = "未指定"
                    for i in range(len(self.__notice_status)):
                        self.__notice_status[i] = False
                elif delta <= 1.0:
                    if not self.__notice_status[0]:
                        self.__broadcast_stop_message("1秒")
                        self.__notice_status[0] = True
                elif delta <= 2.0:
                    if not self.__notice_status[1]:
                        self.__broadcast_stop_message("2秒")
                        self.__notice_status[1] = True
                elif delta <= 3.0:
                    if not self.__notice_status[2]:
                        self.__broadcast_stop_message("3秒")
                        self.__notice_status[2] = True
                elif delta <= 5.0:
                    if not self.__notice_status[3]:
                        self.__broadcast_stop_message("5秒")
                        self.__notice_status[3] = True
                elif delta <= 10.0:
                    if not self.__notice_status[4]:
                        self.__broadcast_stop_message("10秒")
                        self.__notice_status[4] = True
                elif delta <= 30.0:
                    if not self.__notice_status[5]:
                        self.__broadcast_stop_message("30秒")
                        self.__notice_status[5] = True
                elif delta <= 60.0:
                    if not self.__notice_status[6]:
                        self.__broadcast_stop_message("1分钟")
                        self.__notice_status[6] = True
                elif delta <= 60.0 * 2:
                    if not self.__notice_status[7]:
                        self.__broadcast_stop_message("2分钟")
                        self.__notice_status[7] = True
                elif delta <= 60.0 * 5:
                    if not self.__notice_status[8]:
                        self.__broadcast_stop_message("5分钟")
                        self.__notice_status[8] = True
                elif delta <= 60.0 * 10:
                    if not self.__notice_status[9]:
                        self.__broadcast_stop_message("10分钟")
                        self.__notice_status[9] = True
                elif delta <= 60.0 * 30:
                    if not self.__notice_status[10]:
                        self.__broadcast_stop_message("30分钟")
                        self.__notice_status[10] = True
                elif delta <= 60.0 * 60:
                    if not self.__notice_status[11]:
                        self.__broadcast_stop_message("1小时")
                        self.__notice_status[11] = True

            time.sleep(self.loop_sleep_period)
