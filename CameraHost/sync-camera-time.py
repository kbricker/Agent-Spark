#!/usr/bin/env python3
# Push the host's local time to the Sunba.
#
# Its firmware ignores its own DST rule - the clock runs an hour behind all
# summer no matter what TimeZone index or ONVIF TZ string it is given. So its
# NTP is turned off and this pushes real local time instead, from a host that
# does understand DST. Run daily from cron.

import datetime
import sys

sys.path.insert(0, "/home/kyle/frigate")
from xm_dvrip import DVRIP

CAM = "192.168.86.139"

d = DVRIP(CAM)
try:
    ntp = d.get("NetWork.NetNTP")
    if ntp.get("Enable"):
        ntp["Enable"] = False
        d.set("NetWork.NetNTP", ntp)

    before = d.get_time()
    now = datetime.datetime.now()
    d.set_time(now)
    after = d.get_time()
    print(f"{now:%Y-%m-%d %H:%M:%S} host | camera {before} -> {after}")
finally:
    d.close()
