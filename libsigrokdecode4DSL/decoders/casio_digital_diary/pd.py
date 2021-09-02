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

    @classmethod
    def new_empty(cls):
        return cls(0, 0, 0, [], 0)


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
        ("sender-data", "Sender Data"),
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
            "sender-data",
            "Sender Data",
            (_get_annotation_index(annotations, "sender-data"),),
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
        print("_decode_sender_sync_or_frame")
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
            self._frame_startsample = startsample
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
        print("_decode_sender_sync")
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
        print("_decode_sender_frame_header_length")
        value = self._decode_hex(data)
        if value is not None:
            self._frame_header["length"] = value
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
        print("_decode_sender_frame_header_type")
        value = self._decode_hex(data)
        if value is not None:
            self._frame_header["type"] = value
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
        print("_decode_sender_frame_header_address_high")
        value = self._decode_hex(data)
        if value is not None:
            self._frame_header["address_high"] = value
            self._sender_decode_function = self._decode_sender_frame_header_address_low
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender_frame_header_address_low(self, startsample, endsample, data):
        print("_decode_sender_frame_header_address_low")
        value = self._decode_hex(data)
        if value is not None:
            self._frame_header["address_low"] = value
            self._frame_header["address"] = (
                self._frame_header["address_high"] << 8
            ) | (self._frame_header["address_low"] & 0xFF)
            print("  Address")
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-frame-header"),
                    ["Address: " + hex(self._frame_header["address"])],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_data
            self._frame_data = []
            self._data_count = self._frame_header["length"]
        return True

    def _decode_sender_frame_data(self, startsample, endsample, data):
        print("_decode_sender_frame_data")
        if self._data_count > 0:
            value = self._decode_hex(data)
            if value is not None:
                self._chunk_endsample = endsample
                self._frame_data.append(value)
                self._data_count = self._data_count - 1
            else:
                if self._data_count == self._frame_header["length"]:
                    self._chunk_startsample = startsample
            return True
        else:
            if self._frame_header["length"] > 0:
                self.put(
                    self._chunk_startsample,
                    self._chunk_endsample,
                    self.out_ann,
                    [
                        _get_annotation_index(
                            self.annotations, "sender-frame-data"
                        ),
                        ["".join(map(chr, self._frame_data))],
                    ],
                )
            self._sender_decode_function = self._decode_sender_frame_checksum
            if self._sender_decode_function(startsample, endsample, data):
                return True

    def _decode_sender_frame_checksum(self, startsample, endsample, data):
        print("_decode_sender_frame_checksum")
        value = self._decode_hex(data)
        if value is not None:
            self._frame_header["checksum"] = value
            print("  Checksum")
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(
                        self.annotations, "sender-frame-checksum"
                    ),
                    ["Checksum: " + hex(value)],
                ],
            )
            self.put(
                self._frame_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sender-frame"),
                    [
                        "Frame: type="
                        + hex(self._frame_header["type"])
                        + " address="
                        + hex(self._frame_header["address"])
                        + " "
                        + "".join(map(chr, self._frame_data))
                    ],
                ],
            )
            if self._frame_header["type"] == 0x80:
                self.put(
                    self._frame_startsample,
                    endsample,
                    self.out_ann,
                    [
                        _get_annotation_index(self.annotations, "sender-data"),
                        ["Data:" + "".join(map(chr, self._frame_data))],
                    ],
                )
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
        self._frame_header = {}

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