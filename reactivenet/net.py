import struct
import ipaddress
import asyncio
import contextlib

from .enums import *

class Error(Exception):
    pass

class Message():
    def __init__(self, size, payload=bytearray()):
        self.size = size
        self.payload = payload

    def pack(self):
        size = struct.pack('!H', self.size)

        return size + self.payload


    @staticmethod
    def new(payload=None):
        if not payload:
            return Message(0)
        else:
            return Message(len(payload), payload)


    @staticmethod
    async def read(reader):
        # read len
        size = await reader.read(2)
        size = struct.unpack('!H', size)[0]

        # payload
        payload = bytearray()
        if size > 0:
            payload = await reader.read(size)

        return Message(size, payload)


class ResultMessage():
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def pack(self):
        code = struct.pack('!B', self.code)

        return code + self.message.pack()

    def ok(self):
        return code == ReactiveResult.Ok


    @staticmethod
    async def read(reader):
        # read result code
        code = await reader.read(1)
        code = struct.unpack('!B', code)[0]

        try:
            code = ReactiveResult(code)
        except ValueError:
            raise Error("Result code not valid")

        message = await Message.read(reader)

        return ResultMessage(code, message)


class CommandMessage():
    def __init__(self, code, message, ip=None, port=None):
        self.code = code
        self.message = message
        self.__ip = ip
        self.__port = port

    @property
    def ip(self):
        if self.__ip is None:
            raise Error("IP address not specified")

        return self.__ip

    @property
    def port(self):
        if self.__port is None:
            raise Error("TCP port not specified")

        return self.__port


    def pack(self):
        code = struct.pack('!H', self.code)

        return code + self.message.pack()


    def set_dest(self, ip, port):
        self.__ip = ip
        self.__port = port


    def has_response(self):
        return self.code.has_response()


    async def send(self):
        reader, writer = await asyncio.open_connection(str(self.ip), self.port)

        with contextlib.closing(writer):
            writer.write(self.pack())
            await writer.drain()


    async def send_wait(self):
        if not self.has_response():
            raise Error("This command has not response: call send() instead")

        reader, writer = await asyncio.open_connection(str(self.ip), self.port)

        with contextlib.closing(writer):
            writer.write(self.pack())
            await writer.drain()
            return await ResultMessage.read(reader)


    @staticmethod
    async def read(reader):
        # read command code
        code = await reader.read(2)
        code = struct.unpack('!H', code)[0]

        try:
            code = ReactiveCommand(code)
        except ValueError:
            raise Error("Command code not valid")

        message = await Message.read(reader)

        return CommandMessage(code, message)


    @staticmethod
    async def read_with_ip(reader):
        ip = await reader.read(4)
        ip = struct.unpack('!i', ip)[0]
        ip = ipaddress.ip_address(ip)

        port = await reader.read(2)
        port = struct.unpack('!H', port)[0]

        cmd = await CommandMessage.read(reader)
        cmd.set_dest(ip, port)

        return cmd
