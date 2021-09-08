import sigrokdecode as srd
from dataclasses import dataclass
from typing import List, Dict
from . import frame
from . import record
import re


def _get_annotation_index(annotations, name):
    for index, annotation in enumerate(annotations):
        if annotation[0] == name:
            return index
    raise RuntimeError(f"Unknown annotation {repr(name)}: {repr(annotations)}")


_FRAME_TYPE_DESC: Dict[str, str] = {
    frame_class.get_kebab_case_description(): frame_class.DESCRIPTION
    for frame_class in frame.Frame.SUBCLASSES + [frame.Frame]
}

_ANNOTATIONS = (
    ("sync", "Sync"),
    ("frame-start", "Frame Start"),
    ("frame-header", "Frame Header"),
    ("frame-data", "Frame Data"),
    ("frame-checksum", "Frame Checksum"),
    *[(f"frame-type-{id_str}", desc) for id_str, desc in _FRAME_TYPE_DESC.items()],
    *[
        (f"sender-record-{record_class.__name__.lower()}", record_class.DESCRIPTION)
        for record_class in record.Record.DIRECTORY_TO_RECORD.values()
    ],
    ("sender-record-unknown", "Unknown Record"),
    ("sender-warning", "Sender Warning"),
    ("receiver-ready", "Receiver Ready"),
    ("receiver-ack", "Receiver Ack"),
    ("receiver-warning", "Receiver Warning"),
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
    annotations = _ANNOTATIONS
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
            tuple(
                _get_annotation_index(_ANNOTATIONS, f"frame-type-{id_str}")
                for id_str in _FRAME_TYPE_DESC.keys()
            ),
        ),
        (
            "record",
            "Record",
            tuple(
                _get_annotation_index(
                    _ANNOTATIONS, f"sender-record-{record_class.__name__.lower()}"
                )
                for record_class in record.Record.DIRECTORY_TO_RECORD.values()
            )
            + (_get_annotation_index(_ANNOTATIONS, "sender-record-unknown"),),
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
            self._frame_startsample = startsample
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "frame-start"),
                    ["Frame Start"],
                ],
            )
            self._sender_decode_function = self._decode_sender_frame
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

    def _decode_hex(self, data):
        if not hasattr(self, "_hex_high_value"):
            self._hex_high_value = chr(data)
            return
        else:
            hex_value = int(self._hex_high_value + chr(data), 16)
            delattr(self, "_hex_high_value")
            return hex_value

    def _decode_record(self, startsample, endsample, decoded_frame):
        if self._record_state == "directory_or_record":
            if isinstance(decoded_frame, frame.Directory):
                self._record_state = "start"
                self._record_directory_type = type(decoded_frame)
                return
            else:
                self._record_state = "start"
        if self._record_state == "start":
            self._record_startsample = startsample
            self._record_state = "frames"
            self._record_frames: List[Frame] = []
        if self._record_state == "frames":
            if isinstance(decoded_frame, frame.EndOfRecord):
                if self._record_directory_type in record.Record.DIRECTORY_TO_RECORD:
                    record_class = record.Record.DIRECTORY_TO_RECORD[
                        self._record_directory_type
                    ]
                    decoded_record = record_class.from_frames(self._record_frames)
                    decoded_str = str(decoded_record)
                    annotation = (
                        f"sender-record-{type(decoded_record).__name__.lower()}"
                    )
                else:
                    decoded_str = "Unknown Record: " + ", ".join(
                        str(f) for f in self._record_frames
                    )
                    annotation = "sender-record-unknown"
                self.put(
                    self._record_startsample,
                    endsample,
                    self.out_ann,
                    [
                        _get_annotation_index(
                            self.annotations,
                            annotation,
                        ),
                        [decoded_str],
                    ],
                )
                self._record_state = "directory_or_record"
            else:
                self._record_frames.append(decoded_frame)

    def _decode_sender_frame(self, startsample, endsample, data):
        value = self._decode_hex(data)
        if value is not None:
            (chunk_desc, decoded_frame) = self._frame_builder.add_data(value)
            self.put(
                self._chunk_startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "frame-header"),
                    [f"{chunk_desc}: " + hex(value)],
                ],
            )
            if decoded_frame is not None:
                if not decoded_frame.is_checksum_valid():
                    self.put(
                        self._chunk_startsample,
                        endsample,
                        self.out_ann,
                        [
                            _get_annotation_index(self.annotations, "sender-warning"),
                            ["Bad Checksum"],
                        ],
                    )
                if type(decoded_frame) is frame.Frame:
                    self.put(
                        self._frame_startsample,
                        endsample,
                        self.out_ann,
                        [
                            _get_annotation_index(self.annotations, "sender-warning"),
                            [f"Unknown {decoded_frame}"],
                        ],
                    )
                else:
                    self.put(
                        self._frame_startsample,
                        endsample,
                        self.out_ann,
                        [
                            _get_annotation_index(
                                self.annotations,
                                f"frame-type-{decoded_frame.get_kebab_case_description()}",
                            ),
                            [repr(str(decoded_frame))[1:-1]],
                        ],
                    )
                self._decode_record(self._frame_startsample, endsample, decoded_frame)
                self._frame_builder = frame.FrameBuilder()
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
        self._frame_builder = frame.FrameBuilder()
        self._record_state = "directory_or_record"

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
