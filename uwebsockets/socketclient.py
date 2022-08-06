"""
Websockets client for micropython

Based very heavily off
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""
import gc
import usocket as socket
import uasyncio as asyncio
import ubinascii as binascii
import urandom as random

gc.collect()

from .protocol import Websocket

class WebsocketClient(Websocket):
    is_client = True

async def connect(uri):
    """
    Connect a websocket.
    """

    if __debug__: print("open connection %s:%s",
                                "192.168.1.208", "8080")

    sock = socket.socket()
    addr = socket.getaddrinfo("192.168.1.208", 8080)
    sock.connect(addr[0][4])

    sreader = asyncio.StreamReader(sock)
    swriter = asyncio.StreamWriter(sock, {})

    async def send_header(header, *args):
        if __debug__: print(str(header), *args)
        await swriter.awrite(header % args + '\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                    for _ in range(16)))[:-1]
    path = "socket?slim=true&filter=MONITORING_SOURCE_ID_GPU_USAGE,MONITORING_SOURCE_ID_GPU_TEMPERATURE,MONITORING_SOURCE_ID_CPU_TEMPERATURE,MONITORING_SOURCE_ID_CPU_USAGE,MONITORING_SOURCE_ID_FRAMETIME,MONITORING_SOURCE_ID_FRAMERATE"

    await send_header(b'GET %s HTTP/1.1', path or '/')
    await send_header(b'Host: %s:%s', "192.168.1.208", "8080")
    await send_header(b'Connection: Upgrade')
    await send_header(b'Upgrade: websocket')
    await send_header(b'Authorization: Basic cm9vdDpwYXNz')
    await send_header(b'Sec-WebSocket-Key: %s', key)
    await send_header(b'Sec-WebSocket-Version: 13')
    await send_header(b'Origin: http://{hostname}:{port}'.format(
        hostname="192.168.1.208",
        port="8080")
    )
    await send_header(b'')

    response = await sreader.readline()
    header = response[:-2]
    assert header.startswith(b'HTTP/1.1 101 '), header

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        if __debug__: print(str(header))
        response = await sreader.readline()
        header = response[:-2]

    return WebsocketClient(sock, sreader, swriter)
