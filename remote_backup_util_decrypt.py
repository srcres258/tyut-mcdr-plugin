
import pickledb
import os
import tqdm

BASE_DIR = os.getcwd()
FILE_DIR = os.path.join(BASE_DIR, 'server_data')
DECRYPT_DIR = os.path.join(BASE_DIR, 'decrypt_data')

file_content_hash_db = None
file_path_name_hash_db = None

try:
    file_content_hash_db = pickledb.load(os.path.join(FILE_DIR, 'file_content_hash.db'), False)
    file_path_name_hash_db = pickledb.load(os.path.join(FILE_DIR, 'file_path_name_hash_db.db'), False)
except:
    pass

def main():
    if not os.path.exists(FILE_DIR):
        os.makedirs(FILE_DIR)
    if not os.path.exists(DECRYPT_DIR):
        os.makedirs(DECRYPT_DIR)
    pbar = tqdm.tqdm(total=len(file_path_name_hash_db.db))
    try:
        for key in file_path_name_hash_db.db.keys():
            print("Decrypting:", key)
            key_hash = file_path_name_hash_db.db[key]
            print("Hash:", key_hash)
            source_path = key_hash[:2]
            source_path += os.path.sep
            source_path += key_hash
            source_path_full = os.path.join(FILE_DIR, source_path)
            dest_path = key[1:]
            dest_path_full = os.path.join(DECRYPT_DIR, dest_path)
            content = b''
            with open(source_path_full, 'rb') as f:
                content = f.read()
            dest_path_full_pdir = os.path.split(dest_path_full)[0]
            if not os.path.exists(dest_path_full_pdir):
                os.makedirs(dest_path_full_pdir)
            with open(dest_path_full, 'wb') as f:
                f.write(content)
            print("Done.")
            pbar.update(1)
    finally:
        pbar.close()

if __name__ == "__main__":
    main()
