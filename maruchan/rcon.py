import struct
import socket


class RCON():

    SERVERDATA_AUTH = 3
    SERVERDATA_AUTH_RESPONSE = 2
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_RESPONSE_VALUE = 0

    def __init__(self, host, port, password):
        self._conn = socket.socket()
        self._conn.settimeout(3)
        self._host = host
        self._port = port
        self._password = password

    @staticmethod
    def pack_rcon_msg(type: int, msg: str, msg_id: int=0):
        bmsg = bytes(msg, "UTF-8")

        bmsg = struct.pack(
            "ii%dsbb" % len(bmsg),
            msg_id,
            type,
            bmsg,
            0, 0)
        return struct.pack("i%ds" % len(bmsg), len(bmsg), bmsg)

    @staticmethod
    def unpack_rcon_msg(bmsg: bytes):
        msg = struct.unpack("iii%dsbb" % (len(bmsg)-14), bmsg)
        return msg[1:4]

    def connect(self):
        self._conn.connect((self._host, self._port))

    def auth(self):
        self._conn.send(
            RCON.pack_rcon_msg(
                RCON.SERVERDATA_AUTH,
                self._password))
        return(RCON.unpack_rcon_msg(self._conn.recv(20000)))

    def send_msg(self, msg):
        self._conn.send(
            RCON.pack_rcon_msg(
                RCON.SERVERDATA_EXECCOMMAND,
                msg))
        return(RCON.unpack_rcon_msg(self._conn.recv(20000)))

    def disconnect(self):
        self._conn.close()
