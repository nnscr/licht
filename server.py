import asyncio
import wiringpi
import config
import time
import traceback
import morse
from copy import copy

# setup GPIO
wiringpi.setup()
pwm_r = wiringpi.SoftPWM(config.pin_r, config.pwm_range)
pwm_g = wiringpi.SoftPWM(config.pin_g, config.pwm_range)
pwm_b = wiringpi.SoftPWM(config.pin_b, config.pwm_range)


def list_get(l, idx, default=None):
    try:
        return l[idx]
    except IndexError:
        return default


class Color(object):
    """ A mutable color object. """
    __slots__ = ["r", "g", "b"]

    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def __dict__(self):
        return {"r": self.r, "g": self.g, "b": self.b}

    def __str__(self):
        return "\033[31m{r:8.3f} \033[32m{g:8.3f} \033[34m{b:8.3f}\033[m".format(**self.__dict__())


class Light(object):
    def __init__(self, loop):
        # The current main color
        self.current = Color(100, 100, 100)
        # The event loop to use
        self.loop = loop
        # Modes that we want to run
        self.mode_queue = list()
        # The currently running mode asyncio.Task
        self.mode_running = None

    def _write(self, color):
        """ Write the given color to outputs """
        # print("\033[30mSetting color to {0}".format(color))
        pwm_r.write(color.r)
        pwm_g.write(color.g)
        pwm_b.write(color.b)

    def _run_coroutine(self, coroutine):
        """
        Run the given coroutine as soon as possible using the event loop.
        Extra function for easier exchange when upgrading asyncio version
        """
        return asyncio.async(coroutine)

    def set(self, color):
        """ Immediately set the given color, without transition. """
        self._write(color)
        self.current = color

    def restore(self, transition=True):
        """ After a mode, restore the main color. """
        if not transition:
            self._write(self.current)
        else:
            self.transition(self.current, current=Color(pwm_r.value, pwm_g.value, pwm_b.value))

    def transition(self, final_color, current=None, duration=500.):
        """ Make a transition from the current color to the given target color. """

        @asyncio.coroutine
        def _coro():
            nonlocal current
            if not current:
                current = copy(self.current)

            resolution = 20
            steps = int(duration / resolution)

            step_r = (final_color.r - current.r) / steps
            step_g = (final_color.g - current.g) / steps
            step_b = (final_color.b - current.b) / steps

            sleep = resolution / 1000

            for step in range(0, steps):
                current.r += step_r
                current.g += step_g
                current.b += step_b

                self._write(current)
                yield from asyncio.sleep(sleep)

            self.set(final_color)

        return self._run_coroutine(_coro())

    def append_mode(self, mode):
        """ Append a new mode to the queue. Start the queue if it is not running. """
        assert asyncio.iscoroutinefunction(mode)
        print("Appending queue")
        self.mode_queue.append(mode)

        self.run_modes()

        return mode

    def run_modes(self):
        """ Run all waiting modes, stopping when the queue is empty. """
        if self.mode_running:
            print("\033[33mModes are already running.\033[m")
            return
        else:
            print("\033[32;1mRunning modes, queue length: {0}\033[m".format(len(self.mode_queue)))

        @asyncio.coroutine
        def _coro():
            while len(self.mode_queue) > 0:
                # Get the next mode to run
                mode = self.mode_queue.pop(0)

                print("Run mode {0}".format(mode))

                # Add to main loop
                self.mode_running = self._run_coroutine(mode())

                # Wait for mode finish
                yield from asyncio.wait([self.mode_running])

                print("Finished mode {0}".format(mode))

            self.mode_running = None
            print("\033[32;1mAll modes finished, restoring.\033[m")
            self.restore()

        return self._run_coroutine(_coro())

    def cancel_mode(self):
        if not self.mode_running:
            print("Nothing to cancel.")
            return False

        print("\033[33mCancelling {0}\033[m".format(self.mode_running))
        self.mode_running.cancel()

    def alarm(self, color, duration, speed, step):
        @asyncio.coroutine
        def mode_alarm():
            intensity = 0
            direction = 0
            end = time.time() + duration

            while duration == 0 or time.time() <= end:
                if intensity >= 100:
                    direction = 0

                if intensity <= 20:
                    direction = 1

                intensity = intensity + step if direction == 1 else intensity - step

                self._write(Color(**{color: intensity}))
                yield from asyncio.sleep(speed)

        return self.append_mode(mode_alarm)

    def alert(self, times, speed):
        @asyncio.coroutine
        def mode_alert():
            duration = speed / 2
            original = self.current

            for i in range(0, times):
                yield from self.transition(Color(100, 0, 0), duration=duration)
                yield from self.transition(Color(30, 0, 0), duration=duration)

            self.current = original

        return self.append_mode(mode_alert)

    def morse(self, text):
        @asyncio.coroutine
        def mode_morse():
            code = morse.text_to_morse(text)

            color_off = Color(0, 0, 0)
            color_on = Color(100, 100, 100)

            for symbol in code:
                is_pause = symbol in [" ", "/"]

                self._write(color_on if not is_pause else color_off)
                yield from asyncio.sleep(morse.durations[symbol])

                if not is_pause:
                    self._write(color_off)
                    yield from asyncio.sleep(morse.duration_pause)

        return self.append_mode(mode_morse)


def run():
    def handle_message(message: str):
        message = message.split(" ")

        if message[0] == "on":
            r = list_get(message, 1, config.default_r)
            g = list_get(message, 2, config.default_g)
            b = list_get(message, 3, config.default_b)

            if len(message) == 5:
                brightness = max(0, min(100, int(message[4])))

                r = r / 100 * brightness
                g = g / 100 * brightness
                b = b / 100 * brightness

            duration = list_get(message, 6, 500)

            # When changing default color, use a soft transition
            return light.transition(Color(r, g, b), duration=duration)

        elif message[0] == "off":
            return light.transition(Color(0, 0, 0))

        elif message[0] == "alarm":
            duration = int(message[1])
            color = list_get(message, 2, "r")
            speed = int(list_get(message, 3, 2))
            speed = speed / 1000
            step = int(list_get(message, 4, 1))

            light.alarm(color, duration, speed, step)

        elif message[0] == "alert":
            times = int(list_get(message, 1, 3))
            speed = int(list_get(message, 2, 300))

            light.alert(times, speed)

        elif message[0] == "cancel":
            # Cancel the currently executing mode
            light.cancel_mode()
            pass

        elif message[0] == "morse":
            light.morse(" ".join(message[1:]))

        else:
            raise NotImplementedError("Unknown mode")

    @asyncio.coroutine
    def handle_client(reader, writer):
        payload_length = yield from reader.read(1)
        payload_length = int.from_bytes(payload_length, byteorder="little")
        payload = yield from reader.read(payload_length)
        message = payload.decode()
        addr = writer.get_extra_info("peername")
        print("Received %r from %r" % (message, addr))

        try:
            task = handle_message(message)

            if task:
                # if a task is scheduled (like a transition), wait for it's completion
                yield from asyncio.wait([task])

            writer.write("OK".encode())
        except Exception as e:
            writer.write("ERR".encode())
            traceback.print_exc()

        yield from writer.drain()
        writer.close()

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_client, "0.0.0.0", config.port)
    server = loop.run_until_complete(coro)

    print("Running server on {}".format(server.sockets[0].getsockname()))

    light = Light(loop)
    light.set(Color(config.default_r, config.default_g, config.default_b))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()

    # Turn on white light
    light.set(Color(100, 100, 100))

if __name__ == '__main__':
    run()
