"""
Dummy for wiringPi library. Used if run on a machine that doesn't have wiringPi installed. Useful for testing on desktop
computer.
"""


def wiringPiSetup():
    print("WiringPi: Setup")


def softPwmCreate(*args):
    print("WiringPi: softPwmCreate: %r" % (args, ))


def softPwmWrite(*args):
    print("WiringPi: softPwmWrite: %r" % (args, ))

