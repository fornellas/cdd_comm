import sigrokdecode as srd
from dataclasses import dataclass
from typing import List


def _get_annotation_index(annotations, name):
    for index, annotation in enumerate(annotations):
        if annotation[0] == name:
            return index
    raise RuntimeError(f"Unknown annotation {repr(name)}: {repr(annotations)}")


@dataclass
class Frame:
    length: int
    frame_type: int
    address: int
    data: List[int]
    checksum: int
    startsample: int
    endsample: int

    @classmethod
    def new_empty(cls):
        return cls(0, 0, 0, [], 0, 0, 0)

    def get_data_str(self):
        return "".join(
            chr(d) if chr(d).isprintable() else f"({hex(d)})" for d in self.data
        )

    def get_frame_type_str(self):
        if self.frame_type == 0x0:
            if self.address == 0xFF and self.length == 0:
                return "End of Data"
            if self.address == 0x2:
                return "Start of data (TODO self.data)"
            if self.address == 0x1 and self.length == 0:
                return "Record End"
            return "Marker?"
        if self.frame_type == 0x71 and self.length == 1 and self.data == [0x01]:
            return "Record Start"

        if self.frame_type == 0x80:
            return "Data: " + self.get_data_str()
        return hex(self.frame_type)

    def __str__(self):
        return (
            "type="
            + hex(self.frame_type)
            + " address="
            + hex(self.address)
            + " length="
            + hex(self.length)
        )


class Packet:
    def __init__(self):
        self._frames = []

    def _is_last(self, frame):
        return True  # TODO

    def add_frame(self, frame) -> bool:
        if len(self._frames) == 0:
            self.startsample = frame.startsample
        self._frames.append(frame)
        if self._is_last(frame):
            self.endsample = frame.endsample
            return False
        return True

    def __str__(self):
        return self._frames[0].get_frame_type_str()


class Decoder(srd.Decoder):
    api_version = 3
    id = "casio_digital_diary"
    name = "Casio Digital Diary"
    longname = "Casio Digital Diary"
    desc = "Casio Digital Diary serial communication protocol"
    license = "gplv2+"
    inputs = ["uart"]
    outputs = []
    channels = tuple()
    optional_channels = tuple()
    options = (
        {
            "id": "sender",
            "desc": "Sender of data",
            "default": "TX",
            "values": ("TX", "RX"),
        },
        {
            "id": "receiver",
            "desc": "Receiver of data",
            "default": "RX",
            "values": ("TX", "RX"),
        },
    )
    annotations = (
        ("receiver", "Receiver"),
        ("sender-sync", "Sender Frame Sync"),
        ("sender-frame-start", "Sender Frame Start"),
        ("sender-frame-header", "Sender Frame Header"),
        ("sender-frame-data", "Sender Frame Data"),
        ("sender-frame-checksum", "Sender Frame Checksum"),
        ("sender-frame", "Sender Frame"),
        ("sender-packet", "Sender Packet"),
        ("warning", "Warning"),
    )
    annotation_rows = (
        ("receiver", "Receiver", (_get_annotation_index(annotations, "receiver"),)),
        (
            "sender-decoded",
            "Sender Decoded",
            (
                _get_annotation_index(annotations, "sender-sync"),
                _get_annotation_index(annotations, "sender-frame-start"),
                _get_annotation_index(annotations, "sender-frame-header"),
                _get_annotation_index(annotations, "sender-frame-data"),
                _get_annotation_index(annotations, "sender-frame-checksum"),
            ),
        ),
        (
            "sender-frame",
            "Sender Frame",
            (_get_annotation_index(annotations, "sender-frame"),),
        ),
        (
            "sender-packet",
            "Sender Packet",
            (_get_annotation_index(annotations, "sender-packet"),),
        ),
        ("warning", "Warning", (_get_annotation_index(annotations, "warning"),)),
    )
    binary = tuple()
    tags = ["PC"]

    ##
    ## Private
    ##

    # Helpers

    def _decode_hex(self, data):
        if not hasattr(self, "_hex_high_value"):
            self._hex_high_value = chr(data)
            return
        else:
            hex_value = int(self._hex_high_value + chr(data), 16)
            delattr(self, "_hex_high_value")
            return hex_value

    # Receiver

    def _decode_receiver(self, startsample, endsample, data):
        print("<", hex(data))
        if data == 0x11:
            print("  XON", hex(data))
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "receiver"),
                    ["XON"],
                ],
            )
            return

        if data == 0x23:
            print("  ACK", hex(data))
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "receiver"),
                    ["ACK"],
                ],
            )
            return

        print("  ?")
        self.put(
            startsample,
            endsample,
            self.out_ann,
            [
                _get_annotation_index(self.annotations, "warning"),
                ["?"],
            ],
        )

    # Sender

    def _decode_sender_sync_or_frame(self, startsample, endsample, data):
        print("  _decode_sender_sync_or_frame")
        # Sync 1/2
        if data == ord("\r"):
            print("  Sync 1/2")
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-sync"),
                    ["Sync 1/2"],
                ],
            )
            self._sender_decode_function = self._decode_sender_sync
            return True
        # Frame start
        if data == ord(":"):
            print("  Frame start")
            self._frame.startsample = startsample
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-frame-start"),
                    ["Start"],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_header_length
            return True

    def _decode_sender_sync(self, startsample, endsample, data):
        print("  _decode_sender_sync")
        if data is ord("\n"):
            print("  Sync 2/2")
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-sync"),
                    ["Sync 2/2"],
                ],
            )
            self._sender_decode_function = self._decode_sender_sync_or_frame
            return True

    def _decode_sender_frame_header_length(self, startsample, endsample, data):
        print("  _decode_sender_frame_header_length")
        value = self._decode_hex(data)
        if value is not None:
            self._frame.length = value
            print("  Length")
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-frame-header"),
                    ["Length: " + hex(value)],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_header_type
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender_frame_header_type(self, startsample, endsample, data):
        print("  _decode_sender_frame_header_type")
        value = self._decode_hex(data)
        if value is not None:
            self._frame.frame_type = value
            print("  Type")
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-frame-header"),
                    ["Type: " + hex(value)],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_header_address_high
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender_frame_header_address_high(self, startsample, endsample, data):
        print("  _decode_sender_frame_header_address_high")
        value = self._decode_hex(data)
        if value is not None:
            self._frame_address_high = value
            self._sender_decode_function = self._decode_sender_frame_header_address_low
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender_frame_header_address_low(self, startsample, endsample, data):
        print("  _decode_sender_frame_header_address_low")
        value = self._decode_hex(data)
        if value is not None:
            frame_address_low = value
            self._frame.address = (self._frame_address_high << 8) | (
                frame_address_low & 0xFF
            )
            delattr(self, "_frame_address_high")
            print("  Address")
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-frame-header"),
                    ["Address: " + hex(self._frame.address)],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_data
            self._data_count = self._frame.length
        return True

    def _decode_sender_frame_data(self, startsample, endsample, data):
        print("  _decode_sender_frame_data")
        if self._data_count > 0:
            value = self._decode_hex(data)
            if value is not None:
                self._chunk_endsample = endsample
                self._frame.data.append(value)
                self._data_count = self._data_count - 1
            else:
                if self._data_count == self._frame.length:
                    self._chunk_startsample = startsample
            return True
        else:
            if self._frame.length > 0:
                self.put(
                    self._chunk_startsample,
                    self._chunk_endsample,
                    self.out_ann,
                    [
                        _get_annotation_index(self.annotations, "sender-frame-data"),
                        [" ".join(hex(d) for d in self._frame.data)],
                    ],
                )
            self._sender_decode_function = self._decode_sender_frame_checksum
            if self._sender_decode_function(startsample, endsample, data):
                return True

    def _decode_sender_frame_checksum(self, startsample, endsample, data):
        print("  _decode_sender_frame_checksum")
        value = self._decode_hex(data)
        if value is not None:
            self._frame.checksum = value
            self._frame.endsample = endsample
            print("  Checksum")
            self.put(
                self._chunk_startsample,
                self._frame.endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-frame-checksum"),
                    ["Checksum: " + hex(value)],
                ],
            )
            self.put(
                self._frame.startsample,
                self._frame.endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-frame"),
                    [str(self._frame)],
                ],
            )
            if not self._packet.add_frame(self._frame):
                self.put(
                    self._packet.startsample,
                    self._packet.endsample,
                    self.out_ann,
                    [
                        _get_annotation_index(self.annotations, "sender-packet"),
                        [str(self._packet)],
                    ],
                )
                self._packet = Packet()
            self._frame = Frame.new_empty()
            self._sender_decode_function = self._decode_sender_sync_or_frame
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender(self, startsample, endsample, data):
        print(">", hex(data))

        if self._sender_decode_function(startsample, endsample, data):
            return

        # Warning
        print("    ?")
        self.put(
            startsample,
            endsample,
            self.out_ann,
            [
                _get_annotation_index(self.annotations, "warning"),
                ["?"],
            ],
        )
        self._sender_decode_function = self._decode_sender_sync_or_frame

    ##
    ## Public
    ##

    def __init__(self):
        self.reset()

    def start(self):
        """
        This function is called before the beginning of the decoding. This is the
        place to register() the output types, check the user-supplied PD options for
         validity, and so on.
        """
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def reset(self):
        """
        This function is called before the beginning of the decoding. This is the
        place to reset variables internal to your protocol decoder to their initial
        state, such as state machines and counters.
        """
        self._sender_decode_function = self._decode_sender_sync_or_frame
        self._frame = Frame.new_empty()
        self._packet = Packet()
        if hasattr(self, "_frame_address_high"):
            delattr(self, "_frame_address_high")

    def decode(self, startsample, endsample, data):
        """
        In stacked decoders, this is a function that is called by the
        libsigrokdecode backend whenever it has a chunk of data for the protocol
        decoder to handle.
        """
        ptype, rxtx, pdata = data

        if ptype != "DATA":
            return

        datavalue = pdata[0]

        if rxtx == 0:
            if self.options["sender"] == "RX":
                self._decode_sender(startsample, endsample, datavalue)
            if self.options["receiver"] == "RX":
                self._decode_receiver(startsample, endsample, datavalue)
        elif rxtx == 1:
            if self.options["sender"] == "TX":
                self._decode_sender(startsample, endsample, datavalue)
            if self.options["receiver"] == "TX":
                self._decode_receiver(startsample, endsample, datavalue)
