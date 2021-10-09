from typing import Dict, List, Optional, Tuple, Union, cast

import sigrokdecode

from . import frame as frame_mod
from . import record as record_mod


def _get_annotation_index(annotations: Tuple[Tuple[str, str], ...], name: str) -> int:
    for index, annotation in enumerate(annotations):
        if annotation[0] == name:
            return index
    raise RuntimeError(f"Unknown annotation {repr(name)}: {repr(annotations)}")


_FRAME_TYPE_DESC: Dict[str, str] = {
    frame_class.get_kebab_case_description(): frame_class.DESCRIPTION
    for frame_class in frame_mod.Frame.SUBCLASSES + [frame_mod.Frame]
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
        for record_class in record_mod.Record.DIRECTORY_TO_RECORD.values()
    ],
    ("sender-record-unknown", "Unknown Record"),
    ("sender-warning", "Sender Warning"),
    ("receiver-xon", "Receiver XON"),
    ("receiver-xoff", "Receiver XOFF"),
    ("receiver-ack", "Receiver ACK"),
    ("receiver-nack", "Receiver NACK"),
    ("receiver-warning", "Receiver Warning"),
)


class Decoder(sigrokdecode.Decoder):
    api_version = 3
    id = "casio_digital_diary"
    name = "Casio Digital Diary"
    longname = "Casio Digital Diary"
    desc = "Casio Digital Diary serial communication protocol"
    license = "gplv2+"
    inputs = ["uart"]
    outputs: List[str] = []
    channels: Tuple[Dict[str, str], ...] = tuple()
    optional_channels: Tuple[Dict[str, str], ...] = tuple()
    # Typing here is messed up: The class variable is a Tuple, but when decode()
    # is called, the value changes to a Dict Oo
    options: Union[
        Tuple[Dict[str, Union[str, Tuple[str, ...]]], ...], Dict[str, str]
    ] = (
        {
            "id": "sender",
            "desc": "Sender of data",
            "default": "TX",
            "values": ("TX", "RX"),
        },
    )
    annotations: Tuple[Tuple[str, str], ...] = _ANNOTATIONS
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
                for record_class in record_mod.Record.DIRECTORY_TO_RECORD.values()
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
                _get_annotation_index(annotations, "receiver-xon"),
                _get_annotation_index(annotations, "receiver-xoff"),
                _get_annotation_index(annotations, "receiver-ack"),
                _get_annotation_index(annotations, "receiver-nack"),
            ),
        ),
        (
            "receiver-warning",
            "Receiver Warning",
            (_get_annotation_index(annotations, "receiver-warning"),),
        ),
    )
    binary: Tuple[Tuple[str, str], ...] = tuple()
    tags = ["PC"]

    _record_state: str
    _frame_builder: frame_mod.FrameBuilder
    _chunk_startsample: int

    ##
    ## Private
    ##

    # Receiver

    def _decode_receiver(self, startsample: int, endsample: int, data: int) -> None:
        if data == 0x11:
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "receiver-xon"),
                    ["XON"],
                ],
            )
            return

        if data == 0x13:
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "receiver-xoff"),
                    ["XOFF"],
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

        if data == 0x3F:
            self.put(
                startsample,
                endsample,
                self.out_ann,
                [
                    _get_annotation_index(self.annotations, "receiver-nack"),
                    ["NACK"],
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

    def _decode_sender_sync_or_frame(
        self, startsample: int, endsample: int, data: int
    ) -> bool:
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
        return False

    def _decode_sender_sync(self, startsample: int, endsample: int, data: int) -> bool:
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
        return False

    def _decode_hex(self, data: int) -> Optional[int]:
        if not hasattr(self, "_hex_high_value"):
            self._hex_high_value = chr(data)
            return None
        else:
            hex_value = int(self._hex_high_value + chr(data), 16)
            delattr(self, "_hex_high_value")
            return hex_value

    def _decode_record(
        self, startsample: int, endsample: int, decoded_frame: frame_mod.Frame
    ) -> None:
        if self._record_state == "directory_or_record":
            if isinstance(decoded_frame, frame_mod.Directory):
                self._record_state = "start"
                self._record_directory_type = type(decoded_frame)
                return
            else:
                self._record_state = "start"
        if self._record_state == "start":
            self._record_startsample = startsample
            self._record_state = "frames"
            self._record_frames: List[frame_mod.Frame] = []
        if self._record_state == "frames":
            if isinstance(decoded_frame, frame_mod.EndOfRecord):
                if self._record_directory_type in record_mod.Record.DIRECTORY_TO_RECORD:
                    record_class = record_mod.Record.DIRECTORY_TO_RECORD[
                        self._record_directory_type
                    ]
                    decoded_record = record_class.from_frames(self._record_frames)
                    decoded_str = str(decoded_record)
                    annotation = (
                        f"sender-record-{type(decoded_record).__name__.lower()}"
                    )
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
                            _get_annotation_index(self.annotations, "sender-warning"),
                            [decoded_str],
                        ],
                    )
                self._record_state = "directory_or_record"
            else:
                self._record_frames.append(decoded_frame)

    def _decode_sender_frame(self, startsample: int, endsample: int, data: int) -> bool:
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
                if type(decoded_frame) is frame_mod.Frame:
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
                self._frame_builder = frame_mod.FrameBuilder()
                self._sender_decode_function = self._decode_sender_sync_or_frame
        else:
            self._chunk_startsample = startsample
        return True

    def _decode_sender(self, startsample: int, endsample: int, data: int) -> None:

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

    def __init__(self) -> None:
        self.reset()

    def start(self) -> None:
        """
        This function is called before the beginning of the decoding. This is the
        place to register() the output types, check the user-supplied PD options for
         validity, and so on.
        """
        self.out_ann = self.register(sigrokdecode.OUTPUT_ANN)

    def reset(self) -> None:
        """
        This function is called before the beginning of the decoding. This is the
        place to reset variables internal to your protocol decoder to their initial
        state, such as state machines and counters.
        """
        self._sender_decode_function = self._decode_sender_sync_or_frame
        self._frame_builder = frame_mod.FrameBuilder()
        self._record_state = "directory_or_record"

    def decode(
        self,
        startsample: int,
        endsample: int,
        data: Tuple[
            str,
            int,
            Union[int, Tuple[int, List[int]], Tuple[int, int], Tuple[int, bool]],
        ],
    ) -> None:
        """
        In stacked decoders, this is a function that is called by the
        libsigrokdecode backend whenever it has a chunk of data for the protocol
        decoder to handle.
        """

        self.options = cast(Dict[str, str], self.options)

        ptype, rxtx, pdata = data
        pdata = cast(Tuple[int, List[int]], pdata)

        if ptype != "DATA":
            return

        datavalue = pdata[0]

        if rxtx == 0:
            if self.options["sender"] == "RX":
                self._decode_sender(startsample, endsample, datavalue)
            else:
                self._decode_receiver(startsample, endsample, datavalue)
        elif rxtx == 1:
            if self.options["sender"] == "TX":
                self._decode_sender(startsample, endsample, datavalue)
            else:
                self._decode_receiver(startsample, endsample, datavalue)
