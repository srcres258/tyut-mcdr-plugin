
from remote_backup_util.app import server, client

def bootstrap(launch_server: bool = True):
    if launch_server:
        server.main()
    else:
        client.main()

def main():
    char = input("To launch the client enter '0', otherwise the server will be launched:")
    bootstrap(char != '0')

if __name__ == "__main__":
    main()
