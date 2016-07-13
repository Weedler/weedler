#!/usr/bin/python3

import os
import inspect
import sys
import logging
import json
import re
import copy
import time
import RPi.GPIO as GPIO

from mapper import Mapper
from state import BoardState

full_path = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))

logging.info('Program started')
lt = time.localtime()

print("\n\n----------------------------------------------------")
print(time.asctime(lt))
print("----------------------------------------------------")

class DeviceState:

    f = open(full_path+"/data/schedule.json")
    _schedule = json.load(f)
    f.close()
    _schedule['schedule'].sort(key=lambda s: s['time'])

    def dumps(self):

        s = self._schedule
        print('Name: {0}\nVersion: {1}'.format(s['name'], s['version']))

        # get a unique list of devices mentioned in the schedule
        devices = list(set([j for t in s['schedule'] for j in list(t.keys()) if j != 'time']))
        print('Devices: ', devices)

        # for each device, collect the state changes in order
        device_states = dict((d, []) for d in devices)

        for t in s['schedule']:
            m = re.match(r'^\s*(\d\d):(\d\d)\s*$', t['time'])
            if not m:
                print('Malformed time {0} encountered, skipping.'.format(t['time']))
            else:
                mins = int(m.group(1)) * 60 + int(m.group(2))
                for d in t.keys():
                    if d in devices:
                        # introduces a tuple: state, 24hr time (string), minutes into day (int)
                        device_states[d].append((t[d], t['time'], mins))

        # Figure out what the state of each device will be at the end of the day
        # and remove consecutive ONs and OFFs

        start_state = {}

        for d, s in device_states.items():
            new = []
            prev = ''
            for n in s:
                if n[0] != prev:
                    new.append(n)
                    prev = n[0]

            # if there are no values, warn
            if len(new) == 0:
                print('Warning, nothing to do for device {0}'.format(d))
            # if there's only one value left, warn
            elif len(new) == 1:
                print('Warning, device {0} is {1} all day'.format(d, new[0][0]))

            device_states[d] = new
            start_state[d] = (new[-1][0], '00:00', 0)

        print(device_states)
        print(start_state)

        # Figure out how many minutes each device is on each day
        for d, s in device_states.items():
            last = start_state[d]
            total = 0
            for t in s:
                if last[0] == 'ON':
                    total += t[2] - last[2]
                    # assert false, 'Unexpected state in ' + self.__class__.__name__
                last = t
            if last[0] == 'ON':
                total += 1440 - last[2]

            print('Device {0} is on for {1} minutes a day'.format(d, total))

        # Given a time, determine if each device should be on or off

        curr_mins = lt.tm_hour * 60 + lt.tm_min
        curr_state = copy.deepcopy(start_state)

        assert 0 <= curr_mins < 1440, 'Minutes per day invalid in {0}'.format(self.__class__.__name__)

        for d, s in device_states.items():
            for t in s:
                if t[2] <= curr_mins:
                    curr_state[d] = {"ON":1,"OFF":0}[t[0]]

        print('At {0} device states should be {1}'.format(curr_mins, curr_state))

        true_state = {}
        for d in curr_state.keys():
            p = Mapper.pin_for_device(d)
            BoardState.set_pin_mode(p, GPIO.OUT)
            s = BoardState.get_pin_state(p)
            true_state[d] = s

        print("Right now device state is {0}".format(true_state))

        for d in curr_state.keys():
            if curr_state[d] != true_state[d]:
                print("Switching device {0} from {1} to {2}".format(d, true_state[d], curr_state[d]))
                print("{0}: Switching device {1} from {2} to {3}".format(time.asctime(lt), d, true_state[d], curr_state[d]), file=sys.stderr)
                p = Mapper.pin_for_device(d)
                BoardState.set_pin_state(p, curr_state[d])

ds = DeviceState()
ds.dumps()
