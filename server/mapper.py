import json
import os
import inspect

full_path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

# eight power sockets on this board
_min_socket = 1
_max_socket = 8

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
        ##if device_name not in cls._pinmap["pins"][cls._devicemap["devices"]].keys():
        ##    return None
        return int(cls._pinmap["pins"][cls._devicemap["devices"][device_name]])

    @classmethod
    def pin_for_socket(cls, socket_num):
        assert type(socket_num) is int and _min_socket <= socket_num <= _max_socket, "Invalid socket_num {0}".format(socket_num)
        return int(cls._pinmap["pins"][str(socket_num)])
