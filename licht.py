from sys import argv, stderr
from config import port, ip
import asyncio

if __name__ == '__main__':
    if len(argv) < 2:
        print("Missing argument.", file=stderr)
        exit(1)

    @asyncio.coroutine
    def send(data, loop):
        payload = " ".join(data).encode()
        payload_length = len(payload)
        assert len(payload) <= 255

        reader, writer = yield from asyncio.open_connection(ip, port, loop=loop)
        writer.write(bytes([payload_length]))
        writer.write(payload)

        data = yield from reader.read(100)
        print("Received: %r" % data)
        writer.close()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send(argv[1:], loop))
    loop.close()
