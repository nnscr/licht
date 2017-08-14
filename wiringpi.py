"""
WiringPi python wrapper.
"""
from ctypes import cdll

try:
    lib = cdll.LoadLibrary("libwiringPi.so")
except OSError:
    import dummy as dummy_wiring_pi
    lib = dummy_wiring_pi


# change names to conform to PEP 8
setup = lib.wiringPiSetup
soft_pwm_create = lib.softPwmCreate
soft_pwm_write = lib.softPwmWrite


class SoftPWM(object):
    """
    Class wrapper for a GPIO pin with software defined pwm.
    Translates a percentage value to the defined pwm_range.
    """

    def __init__(self, pin, pwm_range, int_value=0, inverted=True):
        soft_pwm_create(pin, int_value, pwm_range)
        self.pwm_range = pwm_range
        self.pin = pin
        self.inverted = inverted
        self.value = int_value

    def write(self, value):
        """
        Calculate the pwm value for a value in the range of 0 to 100, inclusive.
        If value is outside those bounds set it to the maximum or minimum value.
        Write the calculated value to the software pwm.
        """
        self.value = value

        if self.inverted:
            value = 100 - value

        value = max(0, min(100, value))
        raw_value = value / 100 * self.pwm_range

        soft_pwm_write(self.pin, int(raw_value))

