
import threading
import time
import os
import tqdm

from mcdreforged.api.all import *

from remote_backup_util.api import host, messenger, message, util

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

FILE_DIR = os.path.join(os.getcwd(), 'server', 'world')
BACKUP_TIME_LIST = [
    __time_of(14, 0, 0),
    __time_of(22, 0, 0)
]
BYTES_PER_TIME = 1024 * 1024 * 2 # 2 MB per time by default, can be adjusted on your own. Don't set it to a big number because it depends on Python's runtime memory.

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

def __get_next_backup_time_rough(cur_time: time.struct_time) -> time.struct_time:
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

def _get_next_backup_time(cur_time: time.struct_time) -> time.struct_time:
    result = __get_next_backup_time_rough(cur_time)
    if result is None:
        cur_time_n = time.mktime(cur_time)
        cur_time_n += 60.0 * 60 * 24
        cur_time_2 = time.localtime(cur_time_n)
        cur_time_2 = to_mutable_struct_time(cur_time_2)
        cur_time_2.tm_hour = cur_time_2.tm_min = cur_time_2.tm_sec = 0
        cur_time_2 = to_struct_time(cur_time_2)
        return __get_next_backup_time_rough(cur_time_2)
    else:
        return result

def send_and_recv_message(msgr: messenger.Messenger, msg: message.Message) -> message.Message:
    msgr.send_message(msg)
    return msgr.recv_message()

def send_file_push_data(host: host.Host, content: bytes):
    remaining = len(content)
    sent = 0
    pbar = tqdm.tqdm(total=len(content))
    while remaining > 0:
        send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "file_push_data", (content[sent : sent + BYTES_PER_TIME],)))
        pbar.update(BYTES_PER_TIME)
        sent += BYTES_PER_TIME
        remaining -= BYTES_PER_TIME
    pbar.close()

class BackupProgressNotifierThread(threading.Thread):
    def __init__(self, module: BackupModule):
        super().__init__(name="{} BackupProgressNotifierThread".format(constants.PLUGIN_ID), daemon=True)
        self.module = module
        self.time_elapsed = 1
        self.running = True
        self.backup_progress_value = 0
        self.backup_progress_maximum = 0

    def run(self):
        while self.running:
            if self.time_elapsed % 60 == 0:
                self.module.broadcast_module_message("备份进行中，已进行 {} 分钟，进度 {}/{} ...".format(self.time_elapsed / 60, self.backup_progress_value, self.backup_progress_maximum))
            self.time_elapsed += 1
            time.sleep(1)

# Due to conflicts with Tkinter, GUI is abandoned.

# class BackupGUIThread(threading.Thread):
#     def __init__(self):
#         super().__init__(name="{} BackupGUIThread".format(constants.PLUGIN_ID), daemon=True)
#         self.tk = tkinter.Tk()
#         self.tk.geometry('600x400')
#         self.tk.title("存档远程备份")
#         self.info_label = tkinter.Label(self.tk, text="正在连接到服务器...")
#         self.info_label.pack(side=tkinter.TOP)
#         self.progress_pbar_0 = ttk.Progressbar(self.tk)
#         self.progress_pbar_0.pack(side=tkinter.TOP, fill=tkinter.X)
#         self.progress_pbar_0['value'] = 0
#         self.progress_label_0 = tkinter.Label(self.tk, text="")
#         self.progress_label_0.pack(side=tkinter.TOP)
#         self.progress_pbar_1 = ttk.Progressbar(self.tk)
#         self.progress_pbar_1.pack(side=tkinter.TOP, fill=tkinter.X)
#         self.progress_pbar_1['value'] = 0
#         self.progress_label_1 = tkinter.Label(self.tk, text="")
#         self.progress_label_1.pack(side=tkinter.TOP)

#     def run(self):
#         self.tk.mainloop()

class BackupClientHost(host.ClientHost):
    def __init__(self, module: BackupModule, notifier_thread: BackupProgressNotifierThread):
        super().__init__("114.55.177.176", 14285)
        self.module = module
        self.notifier_thread = notifier_thread

    def do_messenging(self):
        backup_start_time = time.time()

        self.module.server.execute("save-off")
        self.module.server.execute("save-all flush")

        try:
            # for root, dirs, files in os.walk(FILE_DIR):
            #     for (i, file) in enumerate(files):
            #         dirfile = os.path.join(root, file)
            #         dirfile_size = os.stat(dirfile).st_size
            #         print("Sending file: {} ({}/{})".format(dirfile, i, len(files)))
            #         content = b''
            #         with open(dirfile, 'rb') as f:
            #             content = f.read()
            #         content_hash = util.calc_sha1(content)
            #         print("Content hash:", content_hash)
            #         hash_msg = send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "get_file_content_sha1", (dirfile[len(FILE_DIR):],)))
            #         server_content_hash = hash_msg.command_arguments[0]
            #         print("Content hash from the server:", server_content_hash)
            #         if content_hash == server_content_hash:
            #             print("Hash are the same, skipping for this file.", content_hash)
            #         else:
            #             print("Hash are different, sending this file.")
            #             send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "file_push_begin", (dirfile[len(FILE_DIR):], dirfile_size, BYTES_PER_TIME)))
            #             send_file_push_data(host, content)
            #             send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "file_push_end", tuple()))
            #             print("Finished sending.")
            # send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "bye", tuple()))

            dirfiles: list[str] = []
            for root, dirs, files in os.walk(FILE_DIR):
                for (i, file) in enumerate(files):
                    dirfiles.append(os.path.join(root, file))
            self.notifier_thread.backup_progress_maximum = len(dirfiles)
            for (i, dirfile) in enumerate(dirfiles):
                dirfile_size = os.stat(dirfile).st_size
                log.i("Sending file: {} ({}/{})".format(dirfile, i, len(dirfiles)))
                self.notifier_thread.backup_progress_value = i
                content = b''
                if ".lock" in dirfile or ".db" in dirfile:
                    log.i("Skipping for this file as it cannot be sent.")
                    continue
                with open(dirfile, 'rb') as f:
                    content = f.read()
                content_hash = util.calc_sha1(content)
                log.i("Content hash: " + content_hash)
                hash_msg = send_and_recv_message(self.messenger, message.Message("request", self.next_msg_id(), "get_file_content_sha1", (dirfile[len(FILE_DIR):],)))
                server_content_hash = hash_msg.command_arguments[0]
                log.i("Content hash from the server: " + server_content_hash)
                if content_hash == server_content_hash:
                    log.i("Hash are the same, skipping for this file.")
                else:
                    log.i("Hash are different, sending this file.")
                    send_and_recv_message(self.messenger, message.Message("request", self.next_msg_id(), "file_push_begin", (dirfile[len(FILE_DIR):], dirfile_size, BYTES_PER_TIME)))
                    send_file_push_data(self, content)
                    send_and_recv_message(self.messenger, message.Message("request", self.next_msg_id(), "file_push_end", tuple()))
                    log.i("Finished sending.")
            send_and_recv_message(self.messenger, message.Message("request", self.next_msg_id(), "bye", tuple()))
        except Exception as ex:
            msg = format.color_code[format.Color.RED]
            msg += "存档备份失败，请联系腐竹以寻求帮助: "
            msg += format.reset_code
            msg += str(ex)
            self.module.broadcast_module_message(msg)
        finally:
            self.clean_up_messenger()

        self.notifier_thread.running = False
        self.module.server.execute("save-on")

        backup_end_time = time.time()
        backup_delta_time = backup_end_time - backup_start_time
        backup_delta_time_mins = int(int(backup_delta_time) / 60)
        backup_delta_time_secs= int(int(backup_delta_time) - 60 * backup_delta_time_mins)
        self.module.broadcast_module_message("备份已完成，共用时 {} 分 {} 秒。".format(backup_delta_time_mins, backup_delta_time_secs))

class BackupTimerThread(threading.Thread):
    def __init__(self, module: BackupModule):
        super().__init__(name="{} BackupTimerThread".format(constants.PLUGIN_ID))
        self.module = module
        self.running = True
        self.loop_sleep_period = 1
        self.time_passed = 0
        self.backup_time = _get_next_backup_time(time.localtime())
        self.__notice_status = [False, False, False, False, False, False,
                                False, False, False, False, False, False]

    def __broadcast_backup_message(self, backup_time: time.struct_time, info: str):
        msg = format.color_code[format.Color.YELLOW]
        msg += "服务器将在{4}{0}:{1}:{2}{5}进行备份，距离备份开始还有{4}{3}{5}。".format(
            "%02d" % backup_time.tm_hour, "%02d" % backup_time.tm_min, "%02d" % backup_time.tm_sec, info, format.color_code[format.Color.RED], format.color_code[format.Color.YELLOW]
        )
        msg += format.reset_code
        self.module.broadcast_module_message(msg)

    def __do_backup(self):
        notifier_thread = BackupProgressNotifierThread(self.module)
        self.module.broadcast_module_message("正在连接到远程备份服务器...")
        host = BackupClientHost(self.module, notifier_thread)
        try:
            host.init_messenger()
            self.module.broadcast_module_message("已连接到备份服务器，即将开始备份，服务器可能产生些许卡顿，请耐心等待备份完成。")
            host.start_messenger()
            notifier_thread.start()
        except ConnectionRefusedError as error:
            self.module.broadcast_module_message("无法连接到远程服务器，备份失败: " + str(error))

    def run(self):
        while self.running:
            cur_time = time.localtime()
            delta = time.mktime(self.backup_time) - time.mktime(cur_time)

            if self.module.server.is_server_startup():
                if delta <= 0:
                    log.i("定时备份：开始备份")
                    self.__do_backup()
                    self.backup_time = _get_next_backup_time(time.localtime())
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
