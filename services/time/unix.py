import datetime
import time

import dateutil


def unix_now() -> int:
    return int(time.mktime(datetime.datetime.now(datetime.UTC).timetuple()))


def unix_last() -> int:
    dt = datetime.datetime.now(datetime.UTC) + dateutil.relativedelta.relativedelta(years=100)

    return int(time.mktime(dt.timetuple()))


def unix_zero() -> int:
    return 0
