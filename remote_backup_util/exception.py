
class IllegalVersionException(Exception):
    def __init__(self, wrong_ver: str, right_ver: str):
        super().__init__("Wrong version {0}, the right one is {1}".format(wrong_ver, right_ver))
