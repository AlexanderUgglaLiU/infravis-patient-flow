
from datetime import datetime

def str2datetime(string: str) -> datetime:
    date, time = string.split(" ")
    year, month, day = date.split("-")
    hh, mm, ss = time.split(":")
    dt = datetime(int(year), int(month), int(day), int(hh), int(mm), int(ss))
    return dt


def timediff(s1: str, s2: str) -> float:
    return (str2datetime(s2) - str2datetime(s1)).total_seconds()
