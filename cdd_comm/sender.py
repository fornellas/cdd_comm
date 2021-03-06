import time
from types import TracebackType
from typing import Dict, List, Literal, Optional, Type

import serial

from . import frame as frame_mod
from . import record as record_mod


class FlowControlSerial:
    def __init__(
        self,
        port: str,
        baudrate: int,
        bytesize: int,
        parity: str,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self._serial = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
        )
        self._read_buff: List[int] = []

    def __enter__(self) -> "FlowControlSerial":
        if not self._serial.isOpen:
            self._serial.open()
        self._read_buff = []
        return self

    def __exit__(
        self,
        exctype: Optional[Type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> Literal[False]:
        self._serial.close()
        return False

    def write(self, data: bytes) -> None:
        for b in data:
            xoff: bool = False
            while True:
                if self._serial.in_waiting or xoff:
                    read = self._serial.read(size=1)[0]
                    if read == serial.XOFF[0]:
                        print("< XOFF")
                        xoff = True
                    elif read == serial.XON[0]:
                        print("< XON")
                        break
                    else:
                        self._read_buff.append(read)
                else:
                    break
            if self._serial.write([b]) != 1:
                raise RuntimeError("Short write!")
            time.sleep(9.0 / self.baudrate)

    def read(self) -> int:
        if self._read_buff:
            return self._read_buff.pop(0)
        else:
            return self._serial.read(size=1)[0]

    def wait_for_xon(self, timeout: float) -> bool:
        original_timeout = self._serial.timeout
        self._serial.timeout = timeout
        try:
            data = self._serial.read(size=1)
            if len(data):
                if data[0] == serial.XON[0]:
                    print("< XON")
                    return True
                else:
                    raise ValueError(f"Unexpected: {data[0]}")
            return False
        finally:
            self._serial.timeout = original_timeout


class Sender:
    ACK: int = 0x23
    NACK: int = 0x3F

    def __init__(
        self,
        port: str,
        baudrate: int,
        bytesize: int,
        parity: str,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity

    def _sync(self, ser: FlowControlSerial) -> None:
        while True:
            print("> CR")
            ser.write(serial.CR)
            time.sleep(0.01)
            print("> LF")
            ser.write(serial.LF)
            if ser.wait_for_xon(0.2):
                break

    def _send_frame(self, ser: FlowControlSerial, frame: frame_mod.Frame) -> None:
        # print(f"  > Frame: {frame}")
        ser.write(frame.bytes())
        time.sleep(0.040)

    def _wait_for_ack(self, ser: FlowControlSerial) -> None:
        read = ser.read()
        if read == self.ACK:
            print("< ACK")
            time.sleep(0.030)
            return
        elif read == self.NACK:
            print("< NACK")
            raise (RuntimeError("NACK received"))
        else:
            raise RuntimeError(f"Unexpected data: {hex(read)}")

    def _send_directory(
        self, ser: FlowControlSerial, directory: frame_mod.Directory
    ) -> None:
        print(f"> {directory}")
        self._send_frame(ser, directory)
        self._wait_for_ack(ser)

    def _send_record(self, ser: FlowControlSerial, record: record_mod.Record) -> None:
        print(f"> {record}")
        for frame in record.to_frames():
            self._send_frame(ser, frame)
        self._send_frame(ser, frame_mod.EndOfRecord.get())
        self._wait_for_ack(ser)

    def send_directory_data(
        self,
        data: Dict[frame_mod.Directory, List[record_mod.Record]],
    ) -> None:
        with FlowControlSerial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
        ) as ser:
            self._sync(ser)
            for directory, records in data.items():
                self._send_directory(ser, directory)
                for record in records:
                    self._send_record(ser, record)
            self._send_frame(ser, frame_mod.EndOfTransmission.get())
