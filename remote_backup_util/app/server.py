
import pickledb
import os
import tqdm
import json
import time

from remote_backup_util import host, constants, util, message, host_impl

FILE_DIR = os.path.join(os.getcwd(), 'server_data')

file_content_hash_db = None
file_path_name_hash_db = None

try:
    file_content_hash_db = pickledb.load(os.path.join(FILE_DIR, 'file_content_hash.db'), False)
    file_path_name_hash_db = pickledb.load(os.path.join(FILE_DIR, 'file_path_name_hash_db.db'), False)
except:
    pass

def get_file_content_hash_raw(path: str) -> str:
    if os.access(path, os.R_OK):
        content = b''
        with open(path, 'rb') as f:
            content = f.read()
        return util.calc_sha1(content)
    else:
        return constants.ZERO_HASH

def get_file_content_hash(path: str) -> str:
    result = file_content_hash_db.get(path)
    if result:
        return result
    elif os.access(path, os.R_OK):
        return get_file_content_hash_raw(path)
    else:
        return constants.ZERO_HASH

def get_push_file_target_path(push_file_name: str) -> str:
    push_file_name_sha1_str = util.calc_str_utf8_sha1(push_file_name)
    return os.path.join(FILE_DIR, push_file_name_sha1_str[:2], push_file_name_sha1_str)

# Synchonized implementation of pickledb.PickleDB.dump to avoid threading exceptions
def dump_db_sync(db: pickledb.PickleDB):
    json.dump(db.db, open(db.loco, 'wt'))

__doing_messenging = False

def __do_messenging(host: host.Host):
    global __doing_messenging
    try:
        __doing_messenging = True
        push_file_name = ""
        push_total_size = 0
        push_remaining_size = 0
        push_size_per_time = 0
        push_file_target_path = ""
        push_file = None
        push_pbar = None
        while True:
            msg = host.messenger.recv_message()
            match msg.command:
                # "get_version" has already been handled within Host itself, hence needn't handle it here.
                case "get_file_content_sha1":
                    host.messenger.send_message(message.Message("respond", host.next_msg_id(), msg.command, (get_file_content_hash(msg.command_arguments[0]),)))
                case "file_push_begin":
                    push_file_name = msg.command_arguments[0]
                    push_total_size = push_remaining_size = msg.command_arguments[1]
                    push_size_per_time = msg.command_arguments[2]
                    push_file_target_path = get_push_file_target_path(push_file_name)
                    push_file_target_path_parent = os.path.split(push_file_target_path)[0]
                    push_file_name_sha1_str = util.calc_str_utf8_sha1(push_file_name)
                    file_path_name_hash_db.set(push_file_name, push_file_name_sha1_str)
                    print("Attempting to receive a new file:", push_file_name)
                    print("SHA1 (file name):", push_file_name_sha1_str)
                    if not os.path.exists(push_file_target_path_parent):
                        os.makedirs(push_file_target_path_parent)
                    push_file = open(push_file_target_path, 'wb')
                    push_pbar = tqdm.tqdm(total=push_total_size)
                    host.messenger.send_message(message.Message("respond", host.next_msg_id(), msg.command, tuple()))
                case "file_push_data":
                    if push_remaining_size < push_size_per_time:
                        push_size_per_time = push_remaining_size
                    push_file.write(msg.command_arguments[0])
                    push_pbar.update(len(msg.command_arguments[0]))
                    push_remaining_size -= len(msg.command_arguments[0])
                    host.messenger.send_message(message.Message("respond", host.next_msg_id(), msg.command, tuple()))
                case "file_push_end":
                    push_file.close()
                    push_pbar.close()
                    file_content_hash = get_file_content_hash_raw(push_file_target_path)
                    file_content_hash_db.set(push_file_name, file_content_hash)
                    print("Finished receiving.")
                    print("SHA1 (file content):", file_content_hash)
                    push_file_name = ""
                    push_total_size = 0
                    push_remaining_size = 0
                    push_size_per_time = 0
                    push_file_target_path = ""
                    push_file = None
                    push_pbar = None
                    host.messenger.send_message(message.Message("respond", host.next_msg_id(), msg.command, tuple()))
                    dump_db_sync(file_content_hash_db)
                    dump_db_sync(file_path_name_hash_db)
                case "bye":
                    host.messenger.send_message(message.Message("respond", host.next_msg_id(), msg.command, tuple()))
                    dump_db_sync(file_content_hash_db)
                    dump_db_sync(file_path_name_hash_db)
                    break
    finally:
        __doing_messenging = False

def main():
    if __doing_messenging:
        time.sleep(1)
    else:
        if not os.path.exists(FILE_DIR):
            os.makedirs(FILE_DIR)
        host = host_impl.SimpleServerHost(__do_messenging, "localhost", 14285)
        host.init_messenger()
        print("Connected to client:", host.messenger.target_addr)
        host.start_messenger()

if __name__ == "__main__":
    main()
