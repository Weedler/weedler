import json
import os
import inspect

full_path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

class Mapper:

    f = open(full_path + "/data/pinmap.json")
    _pinmap = json.load(f)
    f.close()
    f = open(full_path + "/data/devicemap.json")
    _devicemap = json.load(f)
    f.close()
    del f

    @classmethod
    def pin_for_device(cls, device_name):
        return int(Mapper._pinmap["pins"][Mapper._devicemap["devices"][device_name]])

