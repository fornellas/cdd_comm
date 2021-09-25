from . import frame as frame_mod
from . import record as record_mod
from typing import Dict, List, Optional
import serial
import time


class Sender:
    SYNC_1: int = 0x0D
    SYNC_2: int = 0x0A
    XON: int = 0x11
    XOFF: int = 0x13
    ACK: int = 0x23
    NACK: int = 0x3F

    def __init__(
        self,
        directory_data: Dict[frame_mod.Directory, List[record_mod.Record]],
        port: str,
        baudrate: int,
        bytesize: int,
        parity: str,
    ):
        self.directory_data = directory_data
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity

    def _get_serial(self) -> serial.Serial:
        print("Opening serial port")
        return serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=self.bytesize,
            parity=self.parity,
        )

    def _wait_xon(self, ser: serial.Serial) -> None:
        while True:
            read = ser.read(size=1)[0]
            if read == self.XOFF:
                print("< XOFF")
            elif read == self.XON:
                print("< XON")
                return

    def _check_wait_xoff(self, ser: serial.Serial) -> Optional[int]:
        if ser.in_waiting:
            read = ser.read(size=1)[0]
            if read == self.XOFF:
                print("< XOFF")
                self._wait_xon(ser)
                return None
            return read
        return None

    def _receive_byte(self, ser: serial.Serial) -> int:
        while True:
            read = ser.read(size=1)[0]
            if read == self.XOFF:
                self._wait_xon(ser)
            return read

    def _send_bytes(self, ser: serial.Serial, data: bytes) -> None:
        for d in data:
            read = self._check_wait_xoff(ser)
            if read != None:
                if read == self.NACK:
                    raise RuntimeError("NACK")
                else:
                    raise RuntimeError(f"Unexpected: {repr(read)}")
            if ser.write(bytes([d])) != 1:
                raise RuntimeError("Short write!")
            # print(f"    > {hex(d)}")
            # This seem to be required otherwise we get constant XOFF
            time.sleep(0.0011)

    def _sync(self, ser: serial.Serial) -> None:
        while True:
            print("> Sync 1")
            ser.write(bytes([self.SYNC_1]))
            time.sleep(0.01)
            print("> Sync 2")
            ser.write(bytes([self.SYNC_2]))
            original_timeout = ser.timeout
            ser.timeout = 0.2  # FIXME
            xon = ser.read(size=1)
            ser.timeout = original_timeout
            if len(xon):
                print("< XON")
                if xon[0] == self.XON:
                    break
                else:
                    print(f"< Unexpected: {hex(xon)[0]}")
            print("! Timeout")

    def _send_frame(self, ser: serial.Serial, frame: frame_mod.Frame) -> None:
        # print(f"  > Frame: {frame}")
        self._send_bytes(ser, frame.bytes())

    def _wait_for_ack(self, ser: serial.Serial) -> None:
        read = self._receive_byte(ser)
        if read == self.ACK:
            print("< ACK")
            return
        elif read == self.NACK:
            print("< NACK")
            raise (RuntimeError("NACK received"))
        else:
            raise RuntimeError(f"Unexpected data: {hex(read)}")

    def _send_directory(
        self, ser: serial.Serial, directory: frame_mod.Directory
    ) -> None:
        print(f"> {directory}")
        self._send_frame(ser, directory)
        self._wait_for_ack(ser)

    def _send_record(self, ser: serial.Serial, record: record_mod.Record) -> None:
        print(f"> {record}")
        for frame in record.to_frames():
            self._send_frame(ser, frame)
        self._send_frame(ser, frame_mod.EndOfRecord.get())
        self._wait_for_ack(ser)

    def send_directory_data(self) -> None:
        with self._get_serial() as ser:
            self._sync(ser)
            for directory, records in self.directory_data.items():
                self._send_directory(ser, directory)
                for record in records:
                    self._send_record(ser, record)
            self._send_frame(ser, frame_mod.EndOfTransmission.get())


if __name__ == "__main__":
    Sender(
        directory_data={
            frame_mod.TelephoneDirectory.get(): [
                record_mod.Telephone(
                    color="Blue",
                    name="John Doe Blue",
                    number="123-456",
                    address="Nowhere St",
                    memo="Average guy",
                ),
                record_mod.Telephone(
                    color="Orange",
                    name="John Doe Orange",
                    number="123-456",
                    address="Nowhere St",
                    memo="Average guy",
                ),
                record_mod.Telephone(
                    color="Green",
                    name="John Doe Green",
                    number="123-456",
                    address="Nowhere St",
                    memo="Average guy",
                ),
            ],
        },
        port="/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A50285BI-if00-port0",
        baudrate=9600,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_NONE,
    ).send_directory_data()
