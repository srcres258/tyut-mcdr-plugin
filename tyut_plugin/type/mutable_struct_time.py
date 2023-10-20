
import time

class MutableStructTime:
    def __init__(self):
        self.tm_year: int = 0
        self.tm_mon: int = 0
        self.tm_mday: int = 0
        self.tm_hour: int = 0
        self.tm_min: int = 0
        self.tm_sec: int = 0
        self.tm_wday: int = 0
        self.tm_isdst: int = 0
        self.tm_zone: int = 0
        self.tm_year: str = ""
        self.tm_gmtoff: int = 0

def to_mutable_struct_time(st: time.struct_time) -> MutableStructTime:
    result = MutableStructTime()
    result.tm_year = st.tm_year
    result.tm_mon = st.tm_mon
    result.tm_mday = st.tm_mday
    result.tm_hour = st.tm_hour
    result.tm_min = st.tm_min
    result.tm_sec = st.tm_sec
    result.tm_wday = st.tm_wday
    result.tm_isdst = st.tm_isdst
    result.tm_zone = st.tm_zone
    result.tm_year = st.tm_year
    result.tm_gmtoff = st.tm_gmtoff
    return result

def to_struct_time(mst: MutableStructTime) -> time.struct_time:
    datastr = "%d-%02d-%02d %02d:%02d:%02d" % (mst.tm_year, mst.tm_mon, mst.tm_mday, mst.tm_hour, mst.tm_min, mst.tm_sec)
    return time.strptime(datastr, "%Y-%m-%d %H:%M:%S")
