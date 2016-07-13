import os
import sys
import RPi.GPIO as GPIO

# Use RPi board numbering throughout
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

class BoardState:
    # Pi1 Model B+, Pi 2B, Pi Zero and Pi 3B
    # http://www.raspberrypi-spy.co.uk/wp-content/uploads/2012/06/Raspberry-Pi-GPIO-Layout-Model-B-Plus-rotated-2700x900-1024x341.png

    _board_gpio_pins = [11, 12, 13, 15, 16, 18, 22, 7, 29, 31, 33, 35, 37, 32, 36, 38, 40]

    _board_to_bcm = [None, None, None, 2, None, 3, None, 4, 14, None, 15, 17, 18, 27, None,
                     22, 23, None, 24, 10, None, 9, 25, 11, 8, None, 7, 0, 1, 5, None,
                     6, 12, 13, None, 19, 16, 26, 20, None, 21]

    _bcm_to_board = [27, 28, 3, 5, 7, 29, 31, 26, 24, 21, 19, 23, 32, 33, 8, 10,
                     36, 11, 12, 35, 38, 40, 15, 16, 18, 22, 37, 13]

    _wpi_to_bcm = [17, 18, 27, 22, 23, 24, 25, 4, 2, 3, 8, 7, 10, 9, 11, 14,
                   15, None, None, None, None, 5, 6, 13, 19, 26, 12, 16, 20, 21, 0, 1]

    _bcm_to_wpi = [30, 31, 8, 9, 7, 21, 22, 11, 10, 13, 12, 14, 26, 23, 15, 16,
                   27, 0, 1, 24, 28, 29, 3, 4, 5, 6, 25, 2]

    # The kernel export uses BCM pin numbering. Make sure pins are exported.
    for p in _board_gpio_pins:
        bcm = _board_to_bcm[p]
        path = "/sys/class/gpio/gpio{0}".format(bcm)
        if not os.path.isdir(path):
            f = open("/sys/class/gpio/export", "w")
            print("Creating " + path, file=sys.stderr)
            f.write("{0}\n".format(bcm))
            f.flush()
            f.close()

    @classmethod
    def set_pin_mode(cls, pin, mode):
        assert (type(pin) is int) and (pin in cls._board_gpio_pins), "Invalid pin value {0} in {1}".format(pin,cls.__name__)
        assert mode in [GPIO.IN, GPIO.OUT], "Invalid pin mode {0} in {1}".format(mode, cls.__name__)
        GPIO.setup(pin, mode)

    @classmethod
    def get_pin_state(cls, pin):
        assert (type(pin) is int) and (pin in cls._board_gpio_pins), "Invalid pin value {0} in {1}".format(pin,
                                                                                                           cls.__name__)
        bcm_pin = cls._board_to_bcm[pin]
        path = "/sys/class/gpio/gpio{0}/value".format(bcm_pin)
        assert os.path.isfile(path), "GPIO pin {0} (BCM) {1} (Board) is not exported in {2}.".format(bcm_pin, pin,
                                                                                                     cls.__name__)
        f = open(path)
        val = f.readline()
        f.close()
        ret = int(val)
        assert ret in [0, 1], "Unexpected pin state {0} in {1}.".format(ret, cls.__name__)
        return ret

    @classmethod
    def set_pin_state(cls, pin, state):
        assert (type(pin) is int) and (pin in cls._board_gpio_pins), "Invalid pin value {0} in {1}".format(pin,
                                                                                                           cls.__name__)
        assert state in [0, 1], "Unexpected pin state {0} in {1}.".format(state, cls.__name__)
        GPIO.setup(pin, GPIO.OUT, initial=state)
        GPIO.output(pin, state)

    @classmethod
    def dump_state(cls):
        print("Board/BCM/WPi")
        for pino in cls._board_gpio_pins:
            print("Pin {0}/{1}/{2} state is {3}".format(pino,
                                                        cls._board_to_bcm[pino],
                                                        cls._bcm_to_wpi[cls._board_to_bcm[pino]],
                                                        cls.get_pin_state(pino)))
