import struct
import ipaddress
import asyncio
import contextlib

from .enums import *

class Error(Exception):
    pass


# Message: format <size u16><payload>
class Message():
    def __init__(self, payload=bytearray()):
        self.payload = payload


    # form the byte array according to the format
    def pack(self):
        size = struct.pack('!H', len(self.payload))

        return size + self.payload


    # read from an asyncio StreamReader
    @staticmethod
    async def read(reader):
        # read len
        size = await reader.readexactly(2)
        size = struct.unpack('!H', size)[0]

        # payload
        payload = bytearray()
        if size > 0:
            payload = await reader.readexactly(size)

        return Message(payload)


# ResultMessage: format <code u8><size u16><payload>
class ResultMessage():
    def __init__(self, code, message):
        self.code = code
        self.message = message


    # form the byte array according to the format
    def pack(self):
        code = struct.pack('!B', self.code)

        return code + self.message.pack()


    # check if the command succeeded
    def ok(self):
        return self.code == ReactiveResult.Ok


    # read from an asyncio StreamReader
    @staticmethod
    async def read(reader):
        # read result code
        code = await reader.readexactly(1)
        code = struct.unpack('!B', code)[0]

        try:
            code = ReactiveResult(code)
        except ValueError:
            raise Error("Result code not valid")

        message = await Message.read(reader)

        return ResultMessage(code, message)


# CommandMessage: format <code u8><size u16><payload>
class CommandMessage():
    def __init__(self, code, message, ip=None, port=None):
        self.code = code
        self.message = message
        self.__ip = ip
        self.__port = port


    # get destination IP
    # raises exception if the IP is not specified
    @property
    def ip(self):
        if self.__ip is None:
            raise Error("IP address not specified")

        return self.__ip


    # get destination port
    # raises exception if the port is not specified
    @property
    def port(self):
        if self.__port is None:
            raise Error("TCP port not specified")

        return self.__port


    # form the byte array according to the format
    def pack(self):
        code = struct.pack('!B', self.code)

        return code + self.message.pack()


    # set destination ip and port
    def set_dest(self, ip, port):
        self.__ip = ip
        self.__port = port


    # check if the command will have a response
    def has_response(self):
        return self.code.has_response()


    # send the command to the destination IP and port
    async def send(self):
        reader, writer = await asyncio.open_connection(str(self.ip), self.port)

        with contextlib.closing(writer):
            writer.write(self.pack())
            await writer.drain()


    # send the command to the destination IP and port
    # also wait for the response
    # raises exception if the command does not have a response
    async def send_wait(self):
        if not self.has_response():
            raise Error("This command has not response: call send() instead")

        reader, writer = await asyncio.open_connection(str(self.ip), self.port)

        with contextlib.closing(writer):
            writer.write(self.pack())
            await writer.drain()
            return await ResultMessage.read(reader)


    # read from an asyncio StreamReader
    @staticmethod
    async def read(reader):
        # read command code
        code = await reader.readexactly(1)
        code = struct.unpack('!B', code)[0]

        try:
            code = ReactiveCommand(code)
        except ValueError:
            raise Error("Command code not valid")

        message = await Message.read(reader)

        return CommandMessage(code, message)


    # read from an asyncio StreamReader
    # also read ip and port from reader, that are sent before the command
    @staticmethod
    async def read_with_ip(reader):
        ip = await reader.readexactly(4)
        ip = struct.unpack('!I', ip)[0]
        ip = ipaddress.ip_address(ip)

        port = await reader.readexactly(2)
        port = struct.unpack('!H', port)[0]

        cmd = await CommandMessage.read(reader)
        cmd.set_dest(ip, port)

        return cmd


# CommandMessageLoad: since the loading process is different for each
#                     architecture, this class receives the payload already
#                     formed by the caller. The code is fixed: ReactiveCommand.Load
# Inherited: has_response(), send() and send_wait() from CommandMessage
class CommandMessageLoad(CommandMessage):
    def __init__(self, payload, ip, port):
        super().__init__(ReactiveCommand.Load, None, ip, port)
        self.payload = payload


    # form the byte array according to the format
    def pack(self):
        code = struct.pack('!B', self.code)

        return code + self.payload
