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

    def get_type_str(self) -> str:
        if self.length == 0x2 and self.frame_type == 0x0 and self.address == 0x2:
            return "segment-start"
        if (
            self.length == 0x1
            and self.frame_type == 0x71
            and self.address == 0x0
            and self.data[0] in [0x1, 0x2, 0x4]
        ):
            return "color"
        if self.length == 0xA and self.frame_type == 0xF0 and self.address == 0x0:
            return "date"
        if self.length == 0xA and self.frame_type == 0xF4 and self.address == 0x0:
            return "todo-date"
        if self.length == 0x1 and self.frame_type == 0x72 and self.address == 0x0:
            return "todo-priority"
        if self.length == 0x5 and self.frame_type == 0xE4 and self.address == 0x0:
            return "todo-time"
        if self.length == 0x5 and self.frame_type == 0xC4 and self.address == 0x0:
            return "todo-alarm"
        if self.length == 0x20 and self.frame_type == 0x78 and self.address == 0x0:
            return "calendar-date-color-highlight"
        if (
            self.length in [0xB, 0x5]
            and self.frame_type == 0xE0
            and self.address == 0x0
        ):
            return "time"
        if self.length == 0x5 and self.frame_type == 0xC0 and self.address == 0x0:
            return "alarm"
        if self.length == 0x1 and self.frame_type == 0x21 and self.address == 0x00:
            return "illustration"
        if self.frame_type == 0x80:
            return "text"
        if self.frame_type == 0x0 and self.address == 0x1 and self.length == 0x0:
            return "record-end"
        if self.length == 0 and self.frame_type == 0x0 and self.address == 0xFF:
            return "finish"
        return "unknown"

    def __str__(self) -> str:
        type_str = self.get_type_str()

        if type_str == "segment-start":
            if self.data == [0x90, 0x0]:
                return "Telephone Segment Start"
            if self.data == [0xC0, 0x0]:
                return "Business Card Segment Start"
            if self.data == [0xA0, 0x0]:
                return "Memo Segment Start"
            if self.data == [0x80, 0x0]:
                return "Calendar Segment Start"
            if self.data == [0xB0, 0x0]:
                return "Schedule Keeper Segment Start"
            if self.data == [0x91, 0x0]:
                return "Reminder Segment Start"
            if self.data == [0xC1, 0x0]:
                return "To Do Segment Start"
            if self.data == [0x92, 0x0]:
                return "Expense Manager Segment Start"
            return "Unknown Data Segment Start"

        if type_str == "color":
            color_map = {
                0x1: "Blue",
                0x2: "Orange",
                0x4: "Green",
            }
            return f"Color: {color_map[self.data[0]]}"

        if type_str == "date":
            return "Date: " + "".join(chr(d) for d in self.data)

        if type_str == "todo-date":
            return "To Do Date: " + "".join(chr(d) for d in self.data)

        if type_str == "todo-priority":
            priority_map = {
                0x10: "A: Orange",
                0x20: "B: Blue",
                0x30: "C: Green",
            }
            return f"To Do Priority: {priority_map[self.data[0]]}"

        if type_str == "todo-time":
            return "To Do Time: " + "".join(chr(d) for d in self.data)

        if type_str == "todo-alarm":
            return "To Do Alarm: " + "".join(chr(d) for d in self.data)

        if type_str == "calendar-date-color-highlight":
            info_list = []
            for day, color_highlight in enumerate(reversed(self.data)):
                if color_highlight & 0x1:
                    color = "b"
                if color_highlight & 0x4:
                    color = "g"
                if color_highlight & 0x2:
                    color = "o"
                highlight = ""
                if color_highlight & 0x80:
                    highlight = "*"
                info_list.append(f"{day+1}{color}{highlight}")
            return " ".join(info_list)

        if type_str == "time":
            return "Time: " + "".join(chr(d) for d in self.data)

        if type_str == "alarm":
            return "Alarm: " + "".join(chr(d) for d in self.data)

        if type_str == "illustration":
            return f"Illustration: {self.data[0]}"

        if type_str == "text":
            return "Text: " + "".join(
                chr(d) if chr(d).isprintable() else f"({hex(d)})" for d in self.data
            )

        if type_str == "record-end":
            return "Record End"

        if type_str == "finish":
            return "Finish"

        return "Unknown: " + "".join(
            chr(d) if chr(d).isprintable() else f"({hex(d)})" for d in self.data
        )


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
        ("sync", "Sync"),
        ("frame-start", "Frame Start"),
        ("frame-header", "Frame Header"),
        ("frame-data", "Frame Data"),
        ("frame-checksum", "Frame Checksum"),
        ("frame-type-segment-start", "Segment Start"),
        ("frame-type-color", "Color"),
        ("frame-type-date", "Date"),
        ("frame-type-todo-date", "To Do Date"),
        ("frame-type-todo-priority", "To Do Priority"),
        ("frame-type-todo-time", "To Do Time"),
        ("frame-type-todo-alarm", "To Do Alarm"),
        ("frame-type-calendar-date-color-highlight", "Calendar Date Color / Highlight"),
        ("frame-type-time", "Time"),
        ("frame-type-alarm", "Alarm"),
        ("frame-type-illustration", "Illustration"),
        ("frame-type-text", "Text"),
        ("frame-type-record-end", "Record End"),
        ("frame-type-finish", "Finish"),
        ("frame-type-unknown", "Unknown"),
        ("sender-warning", "Sender Warning"),
        ("receiver-ready", "Receiver Ready"),
        ("receiver-ack", "Receiver Ack"),
        ("receiver-warning", "Receiver Warning"),
    )
    annotation_rows = (
        (
            "sender",
            "Sender",
            (
                _get_annotation_index(annotations, "sync"),
                _get_annotation_index(annotations, "frame-start"),
                _get_annotation_index(annotations, "frame-header"),
                _get_annotation_index(annotations, "frame-data"),
                _get_annotation_index(annotations, "frame-checksum"),
            ),
        ),
        (
            "frame",
            "Frame",
            (
                _get_annotation_index(annotations, "frame-type-segment-start"),
                _get_annotation_index(annotations, "frame-type-color"),
                _get_annotation_index(annotations, "frame-type-date"),
                _get_annotation_index(annotations, "frame-type-todo-date"),
                _get_annotation_index(annotations, "frame-type-todo-priority"),
                _get_annotation_index(annotations, "frame-type-todo-time"),
                _get_annotation_index(annotations, "frame-type-todo-alarm"),
                _get_annotation_index(
                    annotations, "frame-type-calendar-date-color-highlight"
                ),
                _get_annotation_index(annotations, "frame-type-time"),
                _get_annotation_index(annotations, "frame-type-alarm"),
                _get_annotation_index(annotations, "frame-type-illustration"),
                _get_annotation_index(annotations, "frame-type-text"),
                _get_annotation_index(annotations, "frame-type-record-end"),
                _get_annotation_index(annotations, "frame-type-finish"),
                _get_annotation_index(annotations, "frame-type-unknown"),
            ),
        ),
        (
            "sender-warning",
            "Sender Warning",
            (_get_annotation_index(annotations, "sender-warning"),),
        ),
        (
            "receiver",
            "Receiver",
            (
                _get_annotation_index(annotations, "receiver-ready"),
                _get_annotation_index(annotations, "receiver-ack"),
            ),
        ),
        (
            "receiver-warning",
            "Receiver Warning",
            (_get_annotation_index(annotations, "receiver-warning"),),
        ),
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
        if data == 0x11:
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "receiver-ready"),
                    ["Ready"],
                ],
            )
            return

        if data == 0x23:
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "receiver-ack"),
                    ["Ack"],
                ],
            )
            return

        self.put(
            startsample,
            endsample,
            self.out_ann,
            [
                _get_annotation_index(self.annotations, "receiver-warning"),
                ["?"],
            ],
        )

    # Sender

    def _decode_sender_sync_or_frame(self, startsample, endsample, data):
        # Sync 1/2
        if data == ord("\r"):
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sync"),
                    ["Sync 1/2"],
                ],
            )
            self._sender_decode_function = self._decode_sender_sync
            return True
        # Frame start
        if data == ord(":"):
            self._frame.startsample = startsample
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "frame-start"),
                    ["Start"],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_header_length
            return True

    def _decode_sender_sync(self, startsample, endsample, data):
        if data is ord("\n"):
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "sync"),
                    ["Sync 2/2"],
                ],
            )
            self._sender_decode_function = self._decode_sender_sync_or_frame
            return True

    def _decode_sender_frame_header_length(self, startsample, endsample, data):
        value = self._decode_hex(data)
        if value is not None:
            self._frame.length = value
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "frame-header"),
                    ["Length: " + hex(value)],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_header_type
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender_frame_header_type(self, startsample, endsample, data):
        value = self._decode_hex(data)
        if value is not None:
            self._frame.frame_type = value
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "frame-header"),
                    ["Type: " + hex(value)],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_header_address_high
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender_frame_header_address_high(self, startsample, endsample, data):
        value = self._decode_hex(data)
        if value is not None:
            self._frame_address_high = value
            self._sender_decode_function = self._decode_sender_frame_header_address_low
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender_frame_header_address_low(self, startsample, endsample, data):
        value = self._decode_hex(data)
        if value is not None:
            frame_address_low = value
            self._frame.address = (self._frame_address_high << 8) | (
                frame_address_low & 0xFF
            )
            delattr(self, "_frame_address_high")
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "frame-header"),
                    ["Address: " + hex(self._frame.address)],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame_data
            self._data_count = self._frame.length
        return True

    def _decode_sender_frame_data(self, startsample, endsample, data):
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
                        _get_annotation_index(self.annotations, "frame-data"),
                        [" ".join(hex(d) for d in self._frame.data)],
                    ],
                )
            self._sender_decode_function = self._decode_sender_frame_checksum
            if self._sender_decode_function(startsample, endsample, data):
                return True

    def _decode_sender_frame_checksum(self, startsample, endsample, data):
        value = self._decode_hex(data)
        if value is not None:
            self._frame.checksum = value
            self._frame.endsample = endsample
            self.put(
                self._chunk_startsample,
                self._frame.endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "frame-checksum"),
                    ["Checksum: " + hex(value)],
                ],
            )
            self.put(
                self._frame.startsample,
                self._frame.endsample,
                self.out_ann,
                [
                    _get_annotation_index(
                        self.annotations, f"frame-type-{self._frame.get_type_str()}"
                    ),
                    [str(self._frame)],
                ],
            )
            self._frame = Frame.new_empty()
            self._sender_decode_function = self._decode_sender_sync_or_frame
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender(self, startsample, endsample, data):

        if self._sender_decode_function(startsample, endsample, data):
            return

        # Warning
        self.put(
            startsample,
            endsample,
            self.out_ann,
            [
                _get_annotation_index(self.annotations, "sender-warning"),
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
