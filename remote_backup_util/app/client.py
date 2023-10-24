
import os
import tqdm

from remote_backup_util import messenger, message, host_impl, util, constants

FILE_DIR = os.path.join(os.getcwd(), 'client_data')
BYTES_PER_TIME = 1024 * 1024 * 2 # 2 MB per time by default, can be adjusted on your own. Don't set it to a big number because it depends on Python's runtime memory.

def get_file_content_hash(path: str) -> str:
    if os.access(path, os.R_OK):
        content = b''
        with open(path, 'rb') as f:
            content = f.read()
        return util.calc_sha1(content)
    else:
        return constants.ZERO_HASH

def get_push_file_target_path(push_file_name: str) -> str:
    push_file_name_sha1_str = util.calc_str_utf8_sha1(push_file_name)
    return os.path.join(FILE_DIR, push_file_name_sha1_str[:2], push_file_name_sha1_str)

def send_and_recv_message(msgr: messenger.Messenger, msg: message.Message) -> message.Message:
    msgr.send_message(msg)
    return msgr.recv_message()

def send_file_push_data(host: host_impl.SimpleServerHost, content: bytes):
    remaining = len(content)
    sent = 0
    pbar = tqdm.tqdm(total=len(content))
    while remaining > 0:
        send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "file_push_data", (content[sent : sent + BYTES_PER_TIME],)))
        pbar.update(BYTES_PER_TIME)
        sent += BYTES_PER_TIME
        remaining -= BYTES_PER_TIME
    pbar.close()

def __do_messenging(host: host_impl.SimpleServerHost):
    for root, dirs, files in os.walk(FILE_DIR):
        for (i, file) in enumerate(files):
            dirfile = os.path.join(root, file)
            dirfile_size = os.stat(dirfile).st_size
            print("Sending file: {} ({}/{})".format(dirfile, i, len(files)))
            content = b''
            with open(dirfile, 'rb') as f:
                content = f.read()
            content_hash = util.calc_sha1(content)
            print("Content hash:", content_hash)
            hash_msg = send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "get_file_content_sha1", (dirfile[len(FILE_DIR):],)))
            server_content_hash = hash_msg.command_arguments[0]
            print("Content hash from the server:", server_content_hash)
            if content_hash == server_content_hash:
                print("Hash are the same, skipping for this file.", content_hash)
            else:
                print("Hash are different, sending this file.")
                send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "file_push_begin", (dirfile[len(FILE_DIR):], dirfile_size, BYTES_PER_TIME)))
                send_file_push_data(host, content)
                send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "file_push_end", tuple()))
                print("Finished sending.")
    send_and_recv_message(host.messenger, message.Message("request", host.next_msg_id(), "bye", tuple()))

def main():
    if not os.path.exists(FILE_DIR):
        os.makedirs(FILE_DIR)
    host = host_impl.SimpleClientHost(__do_messenging, "localhost", 14285)
    host.init_messenger()
    host.start_messenger()

if __name__ == "__main__":
    main()
