from dataclasses import dataclass
from typing import List, Type, Iterable, ClassVar, Dict, Optional, Tuple
from abc import ABC, abstractmethod

##
## Frame
##


@dataclass
class Frame:
    length: int
    type: int
    address: int
    data: List[int]
    checksum: int

    DESCRIPTION: ClassVar[str] = "Frame"

    SUBCLASSES: ClassVar[List[Type["Frame"]]] = []

    @classmethod
    def get_kebab_case_description(cls):
        return cls.DESCRIPTION.lower().replace(" ", "-")

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls.SUBCLASSES.append(cls)

    def __str__(self):
        return f"Frame: " + "".join(
            chr(d) if chr(d).isprintable() else f"[{hex(d)}]" for d in self.data
        )

    def is_checksum_valid(self) -> bool:
        checksum = (
            self.length
            + self.type
            + ((self.address >> 8) & 0xFF)
            + (self.address & 0xFF)
            + sum(self.data)
        )
        checksum &= 0xFF
        checksum = 0xFF - checksum
        checksum += 1
        if self.checksum == checksum:
            return True
        else:
            return False

    @classmethod
    def from_data(
        cls, length: int, frame_type: int, address: int, data: List[int], checksum: int
    ) -> "Frame":
        for subclass in reversed(cls.SUBCLASSES):
            if subclass.match(length, frame_type, address, data):
                return subclass(length, frame_type, address, data, checksum)
        return cls(length, frame_type, address, data, checksum)

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        return False


# Directory


class Directory(Frame):

    DESCRIPTION: str = "Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x2 and frame_type == 0x0 and address == 0x200:
            return True
        else:
            return False

    def __str__(self):
        return f"{self.DESCRIPTION} Start"


class TelephoneDirectory(Directory):
    DESCRIPTION: str = "Telephone Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if super().match(length, frame_type, address, data) and data == [0x90, 0x0]:
            return True
        return False


class BusinessCardDirectory(Directory):
    DESCRIPTION: str = "Business Card Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if super().match(length, frame_type, address, data) and data == [0xC0, 0x0]:
            return True
        return False


class MemoDirectory(Directory):
    DESCRIPTION: str = "Memo Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if super().match(length, frame_type, address, data) and data == [0xA0, 0x0]:
            return True
        return False


class CalendarDirectory(Directory):
    DESCRIPTION: str = "Calendar Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if super().match(length, frame_type, address, data) and data == [0x80, 0x0]:
            return True
        return False


class ScheduleKeeperDirectory(Directory):
    DESCRIPTION: str = "Schedule Keeper Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if super().match(length, frame_type, address, data) and data == [0xB0, 0x0]:
            return True
        return False


class ReminderDirectory(Directory):
    DESCRIPTION: str = "Reminder Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if super().match(length, frame_type, address, data) and data == [0x91, 0x0]:
            return True
        return False


class ToDoDirectory(Directory):
    DESCRIPTION: str = "To Do Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if super().match(length, frame_type, address, data) and data == [0xC1, 0x0]:
            return True
        return False


class ExpenseManagerDirectory(Directory):
    DESCRIPTION: str = "Expense Manager Directory"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if super().match(length, frame_type, address, data) and data == [0x92, 0x0]:
            return True
        return False


# Others


class Color(Frame):
    DESCRIPTION: str = "Color"
    _NAMES: Dict[int, str] = {
        0x1: "Blue",
        0x2: "Orange",
        0x4: "Green",
    }

    @property
    def name(self):
        return self._NAMES[self.data[0]]

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if (
            length == 0x1
            and frame_type == 0x71
            and address == 0x0
            and data[0] in cls._NAMES.keys()
        ):
            return True
        return False

    def __str__(self):
        return f"{self.DESCRIPTION}: {self.name}"


class TextDataFrame(Frame, ABC):
    # TODO All other characters from manual
    CASIO_TO_UNICODE: Dict[int, str] = {
        10: chr(0x1F),  # Unit separator
        13: "\n",
        21: "§",
        32: " ",
        33: "!",
        34: '"',
        35: "#",
        36: "$",
        37: "%",
        38: "&",
        39: "'",
        40: "(",
        41: ")",
        42: "*",
        43: "+",
        44: ",",
        45: "-",
        46: ".",
        47: "/",
        48: "0",
        49: "1",
        50: "2",
        51: "3",
        52: "4",
        53: "5",
        54: "6",
        55: "7",
        56: "8",
        57: "9",
        58: ":",
        59: ";",
        60: "<",
        61: "=",
        62: ">",
        63: "?",
        64: "@",
        65: "A",
        66: "B",
        67: "C",
        68: "D",
        69: "E",
        70: "F",
        71: "G",
        72: "H",
        73: "I",
        74: "J",
        75: "K",
        76: "L",
        77: "M",
        78: "N",
        79: "O",
        80: "P",
        81: "Q",
        82: "R",
        83: "S",
        84: "T",
        85: "U",
        86: "V",
        87: "W",
        88: "X",
        89: "Y",
        90: "Z",
        91: "[",
        92: "\\",
        93: "]",
        94: "^",
        97: "a",
        98: "b",
        99: "c",
        100: "d",
        101: "e",
        102: "f",
        103: "g",
        104: "h",
        105: "i",
        106: "j",
        107: "k",
        108: "l",
        109: "m",
        110: "n",
        111: "o",
        112: "p",
        113: "q",
        114: "r",
        115: "s",
        116: "t",
        117: "u",
        118: "v",
        119: "w",
        120: "x",
        121: "y",
        122: "z",
        123: "{",
        124: "¦",
        125: "}",
        126: "~",
        181: "Á",
        144: "É",
        182: "Í",
        183: "Ó",
        184: "Ú",
        185: "À",
        186: "È",
        187: "Ì",
        188: "Ò",
        189: "Ù",
        198: "Â",
        199: "Ê",
        200: "Î",
        201: "Ô",
        202: "Û",
        173: "¡",
        160: "á",
        130: "é",
        161: "í",
        162: "ó",
        163: "ú",
        133: "à",
        138: "è",
        141: "ì",
        149: "ò",
        151: "ù",
        131: "â",
        136: "ê",
        140: "î",
        147: "ô",
        150: "û",
        168: "¿",
        142: "Ä",
        203: "Ë",
        204: "Ï",
        153: "Ö",
        154: "Ü",
        205: "Ã",
        207: "Õ",
        165: "Ñ",
        209: "Ĳ",
        146: "Æ",
        128: "Ç",
        143: "Å",
        232: "Ø",
        225: "β",
        190: "¶",
        155: "¢",
        132: "ä",
        137: "ë",
        139: "ï",
        148: "ö",
        129: "ü",
        206: "ã",
        208: "õ",
        164: "ñ",
        210: "ĳ",
        145: "æ",
        135: "ç",
        134: "å",
        237: "ø",
        156: "£",
        157: "¥",
        234: "Ω",
        166: "ª",
        167: "º",
        245: "×",
        246: "÷",
        241: "±",
        248: "°",
        253: "²",
        211: "³",
        230: "µ",
        171: "½",
        172: "¼",
        212: "¾",
        159: "f",
        179: "|",
        216: "₣",
        174: "←",
        175: "→",
        251: "√",
    }

    UNICODE_TO_CASIO: Dict[str, int] = {
        u: c for c, u in CASIO_TO_UNICODE.items() if u != ""
    }

    @classmethod
    @abstractmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        return False

    @property
    def text(self) -> str:
        return "".join(
            self.CASIO_TO_UNICODE[d] if d in self.CASIO_TO_UNICODE else f"[{d}]"
            for d in self.data
        )

    def __str__(self):
        return f"{self.DESCRIPTION}: {self.text}"


class Date(TextDataFrame):
    DESCRIPTION: str = "Date"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0xA and frame_type == 0xF0 and address == 0x0:
            return True
        return False


class ToDoDate(TextDataFrame):
    DESCRIPTION: str = "To Do Date"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0xA and frame_type == 0xF4 and address == 0x0:
            return True
        return False


class DoDoPriority(Frame):
    DESCRIPTION: str = "To Do Priority"
    _NAME: Dict[int, str] = {
        0x10: "A: Orange",
        0x20: "B: Blue",
        0x30: "C: Green",
    }

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x1 and frame_type == 0x72 and address == 0x0:
            return True
        return False

    def __str__(self):
        return f"{self.DESCRIPTION}: {self._NAME[self.data[0]]}"


class ToDoTime(TextDataFrame):
    DESCRIPTION: str = "To Do Time"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x5 and frame_type == 0xE4 and address == 0x0:
            return True
        return False


class ToDoAlarm(TextDataFrame):
    DESCRIPTION: str = "To Do Alarm"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x5 and frame_type == 0xC4 and address == 0x0:
            return True
        return False


class CalendarHighlight(Frame):
    DESCRIPTION: str = "Calendar Highlight"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x20 and frame_type == 0x78 and address == 0x0:
            return True
        return False

    def __str__(self):
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
        return f"{self.DESCRIPTION}: " + " ".join(info_list)


class Time(TextDataFrame):
    DESCRIPTION: str = "Time"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length in [0xB, 0x5] and frame_type == 0xE0 and address == 0x0:
            return True
        return False


class Alarm(TextDataFrame):
    DESCRIPTION: str = "Alarm"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x5 and frame_type == 0xC0 and address == 0x0:
            return True
        return False


class Illustration(Frame):
    DESCRIPTION: str = "Illustration"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x1 and frame_type == 0x21 and address == 0x0:
            return True
        return False

    def __str__(self):
        return f"Illustration: {self.data[0]}"


class Text(TextDataFrame):
    DESCRIPTION: str = "Text"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if (
            frame_type == 0x80  # Text with address < 0x100
            or frame_type == 0x81  # Text with address >= 0x100
        ):
            return True
        return False


# End


class EndOfRecord(Frame):
    DESCRIPTION: str = "End Of Record"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x0 and frame_type == 0x0 and address == 0x100:
            return True
        return False

    def __str__(self):
        return "End"


class EndOfTransmission(Frame):
    DESCRIPTION: str = "End Of Transmission"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x0 and frame_type == 0x0 and address == 0xFF00:
            return True
        return False

    def __str__(self):
        return "End Of Transmission"


##
## Frame Builder
##


class FrameBuilder:
    length: Optional[int]
    type: Optional[int]
    address: Optional[int]
    data: List[int]
    checksum: Optional[int]

    def __init__(self):
        self.length = None
        self.type = None
        self._address_low = None
        self._address_high = None
        self.address = None
        self._data_count = None
        self.data = []
        self.checksum = None

    def add_data(self, data: int) -> Tuple[str, Optional[Frame]]:
        if self.length is None:
            self.length = data
            self._data_count = self.length
            return ("Length", None)
        if self.type is None:
            self.type = data
            return ("Type", None)
        if self._address_low is None:
            self._address_low = data
            return ("Address Low", None)
        if self._address_high is None:
            self._address_high = data
            self.address = (self._address_high << 8) | (self._address_low & 0xFF)
            return ("Address High", None)
        if self._data_count:
            self.data.append(data)
            self._data_count -= 1
            return ("Data", None)
        self.checksum = data
        return (
            "Checksum",
            Frame.from_data(
                self.length,
                self.type,
                self.address,
                self.data,
                self.checksum,
            ),
        )
