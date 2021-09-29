import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Dict, List, Optional, Set, Tuple, Type

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

    _FRAME_START: int = 0x3A

    @classmethod
    def get_kebab_case_description(cls) -> str:
        return cls.DESCRIPTION.lower().replace(" ", "-")

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls.SUBCLASSES.append(cls)

    def __str__(self) -> str:
        return "Frame: " + "".join(
            chr(d) if chr(d).isprintable() else f"[{hex(d)}]" for d in self.data
        )

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other) -> bool:
        if type(other) != type(self):
            return False
        return (
            self.length == other.length
            and self.type == other.type
            and self.address == other.address
            and self.data == other.data
            and self.checksum == other.checksum
        )

    @staticmethod
    def calculate_checksum(
        length: int, frame_type: int, address: int, data: List[int]
    ) -> int:
        checksum = (
            length + frame_type + ((address >> 8) & 0xFF) + (address & 0xFF) + sum(data)
        )
        checksum &= 0xFF
        checksum = 0xFF - checksum
        checksum += 1
        return checksum & 0xFF

    def is_checksum_valid(self) -> bool:
        if self.checksum == self.calculate_checksum(
            self.length, self.type, self.address, self.data
        ):
            return True
        else:
            return False

    @staticmethod
    def _encode(value: int) -> List[int]:
        assert value <= 255
        assert value >= 0
        return list(ord(v) for v in "%02X" % value)

    def bytes(self) -> bytes:
        bytes_list: List[int] = [
            self._FRAME_START,
            *self._encode(self.length),
            *self._encode(self.type),
            *self._encode(self.address & 0xFF),
            *self._encode((self.address & 0xFF00) >> 8),
        ]
        for d in self.data:
            bytes_list.extend(self._encode(d))
        bytes_list.extend(self._encode(self.checksum))
        return bytes(bytes_list)

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

    DESCRIPTION: ClassVar[str] = "Directory"

    LENGTH: ClassVar[int] = 0x2
    TYPE: ClassVar[int] = 0x0
    ADDRESS: ClassVar[int] = 0x200
    DATA: ClassVar[List[int]] = [0, 0]

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if (
            length == cls.LENGTH
            and frame_type == cls.TYPE
            and address == cls.ADDRESS
            and data == cls.DATA
        ):
            return True
        else:
            return False

    @classmethod
    def get(cls) -> "Directory":
        return cls(
            cls.LENGTH,
            cls.TYPE,
            cls.ADDRESS,
            cls.DATA,
            cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, cls.DATA),
        )

    def __str__(self) -> str:
        return f"{self.DESCRIPTION}"


class TelephoneDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "Telephone Directory"
    DATA: ClassVar[List[int]] = [0x90, 0x0]


class BusinessCardDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "Business Card Directory"
    DATA: ClassVar[List[int]] = [0xC0, 0x0]


class MemoDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "Memo Directory"
    DATA: ClassVar[List[int]] = [0xA0, 0x0]


class CalendarDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "Calendar Directory"
    DATA: ClassVar[List[int]] = [0x80, 0x0]


class ScheduleKeeperDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "Schedule Keeper Directory"
    DATA: ClassVar[List[int]] = [0xB0, 0x0]


class ReminderDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "Reminder Directory"
    DATA: ClassVar[List[int]] = [0x91, 0x0]


class ToDoDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "To Do Directory"
    DATA: ClassVar[List[int]] = [0xC1, 0x0]


class ExpenseManagerDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "Expense Manager Directory"
    DATA: ClassVar[List[int]] = [0x92, 0x0]


# Others


class ColorEnum(Enum):
    BLUE: int = 0x1
    ORANGE: int = 0x2
    GREEN: int = 0x4


class Color(Frame):
    DESCRIPTION: ClassVar[str] = "Color"
    LENGTH: ClassVar[int] = 0x1
    TYPE: ClassVar[int] = 0x71
    ADDRESS: ClassVar[int] = 0x0
    _CODE_TO_COLOR: Dict[int, ColorEnum] = {
        color.value: color for color in list(ColorEnum)
    }
    _COLOR_TO_CODE: Dict[ColorEnum, int] = {
        color: code for code, color in _CODE_TO_COLOR.items()
    }

    @property
    def enum(self) -> ColorEnum:
        return self._CODE_TO_COLOR[self.data[0]]

    @property
    def name(self) -> str:
        return self.enum.name

    @classmethod
    def from_color_enum(cls, color: ColorEnum) -> "Color":
        data = [cls._COLOR_TO_CODE[color]]
        return cls(
            cls.LENGTH,
            cls.TYPE,
            cls.ADDRESS,
            data,
            cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if (
            length == cls.LENGTH
            and frame_type == cls.TYPE
            and address == cls.ADDRESS
            and data[0] in cls._CODE_TO_COLOR.keys()
        ):
            return True
        return False

    def __str__(self) -> str:
        return f"{self.DESCRIPTION}: {self.name}"


class TextDataFrame(Frame, ABC):
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

    def __str__(self) -> str:
        return f"{self.DESCRIPTION}: {self.text}"


class Date(TextDataFrame):
    DESCRIPTION: ClassVar[str] = "Date"
    LENGTH: ClassVar[int] = 0xA
    TYPE: ClassVar[int] = 0xF0
    ADDRESS: ClassVar[int] = 0x0

    def _get_date(self) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        year: Optional[int]
        month: Optional[int]
        day: Optional[int]
        if self.text[0] != "-":
            year_str = self.text[0:4]
            year = int(year_str)
        else:
            year = None
        if self.text[5] != "-":
            month_str = self.text[5:7]
            month = int(month_str)
        else:
            month = None
        if self.text[8] != "-":
            day_str = self.text[8:10]
            day = int(day_str)
        else:
            day = None
        return (year, month, day)

    @property
    def year(self) -> Optional[int]:
        year, month, day = self._get_date()
        return year

    @property
    def month(self) -> Optional[int]:
        year, month, day = self._get_date()
        return month

    @property
    def day(self) -> Optional[int]:
        year, month, day = self._get_date()
        return day

    @property
    def date(self) -> datetime.date:
        year, month, day = self._get_date()
        if year is None:
            raise RuntimeError("Missing year")
        if month is None:
            raise RuntimeError("Missing month")
        if day is None:
            raise RuntimeError("Missing day")
        return datetime.date(year, month, day)

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == cls.LENGTH and frame_type == cls.TYPE and address == cls.ADDRESS:
            return True
        return False


class DeadlineDate(Date):
    DESCRIPTION: ClassVar[str] = "Deadline Date"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0xA and frame_type == 0xF4 and address == 0x0:
            return True
        return False


class Time(TextDataFrame):
    DESCRIPTION: ClassVar[str] = "Time"
    LENGTH: ClassVar[int] = 0x5
    TYPE: ClassVar[int] = 0xE0
    ADDRESS: ClassVar[int] = 0x0

    @property
    def time(self) -> datetime.time:
        hour_str, minute_str = self.text.split(":")
        return datetime.time(int(hour_str), int(minute_str))

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == cls.LENGTH and frame_type == cls.TYPE and address == cls.ADDRESS:
            return True
        return False


class DeadlineTime(Time):
    DESCRIPTION: ClassVar[str] = "Deadline Time"
    TYPE: ClassVar[int] = 0xE4


class ToDoAlarm(Time):
    DESCRIPTION: ClassVar[str] = "To Do Alarm"
    TYPE: ClassVar[int] = 0xC4


class Alarm(Time):
    DESCRIPTION: ClassVar[str] = "Alarm"
    TYPE: ClassVar[int] = 0xC0


class PriorityEnum(Enum):
    A: int = 0x10
    B: int = 0x20
    C: int = 0x30


class Priority(Frame):
    DESCRIPTION: ClassVar[str] = "Priority"
    LENGTH: ClassVar[int] = 0x1
    TYPE: ClassVar[int] = 0x72
    ADDRESS: ClassVar[int] = 0x0
    _CODE_TO_PRIORITY: Dict[int, PriorityEnum] = {
        priority.value: priority for priority in list(PriorityEnum)
    }
    _PRIORITY_TO_CODE: Dict[PriorityEnum, int] = {
        priority: code for code, priority in _CODE_TO_PRIORITY.items()
    }
    _PRIORITY_TO_COLOR: Dict[PriorityEnum, ColorEnum] = {
        PriorityEnum.A: ColorEnum.ORANGE,
        PriorityEnum.B: ColorEnum.BLUE,
        PriorityEnum.C: ColorEnum.GREEN,
    }

    @property
    def color(self) -> ColorEnum:
        return self._PRIORITY_TO_COLOR[self.enum]

    @property
    def enum(self) -> PriorityEnum:
        return self._CODE_TO_PRIORITY[self.data[0]]

    @classmethod
    def from_priority_enum(cls, priority: PriorityEnum) -> "Priority":
        data = [cls._PRIORITY_TO_CODE[priority]]
        return cls(
            cls.LENGTH,
            cls.TYPE,
            cls.ADDRESS,
            data,
            cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if (
            length == cls.LENGTH
            and frame_type == cls.TYPE
            and address == cls.ADDRESS
            and data[0] in cls._CODE_TO_PRIORITY.keys()
        ):
            return True
        return False

    def __str__(self) -> str:
        return f"{self.DESCRIPTION}: {self.enum.name}"


class DayHighlight(Frame):
    DESCRIPTION: ClassVar[str] = "Day Highlight"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x4 and frame_type == 0xD0 and address == 0x0:
            return True
        return False

    @property
    def days(self) -> Set[int]:
        days: List[int] = []
        for idx, data in enumerate(self.data):
            for bit in range(8):
                if data & (1 << bit):
                    days.append((3 - idx) * 8 + bit + 1)
        return set(days)

    def __str__(self) -> str:
        return f"{self.DESCRIPTION}: " + " ".join(str(day) for day in sorted(self.days))


class DayColorHighlight(Frame):
    DESCRIPTION: ClassVar[str] = "Day Color & Highlight"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x20 and frame_type == 0x78 and address == 0x0:
            return True
        return False

    def _get_day_color_highlight(self) -> List[Tuple[ColorEnum, bool]]:
        color_highlight: List[Tuple[ColorEnum, bool]] = []
        for info in reversed(self.data):
            color_enum: ColorEnum
            for color_enum_candidate in list(ColorEnum):
                if info & color_enum_candidate.value:
                    color_enum = color_enum_candidate
                    break
            highlight: bool = False
            if info & 0x80:
                highlight = True
            color_highlight.append((color_enum, highlight))
        return color_highlight

    @property
    def highlighted_days(self) -> Set[int]:
        highlighted_dates: Set[int] = set()
        for idx, value in enumerate(self._get_day_color_highlight()):
            _color, highlight = value
            date = idx + 1
            if date > 31:
                continue
            if highlight:
                highlighted_dates.add(date)
        return highlighted_dates

    @property
    def day_colors(self) -> List[ColorEnum]:
        day_colors: List[ColorEnum] = []
        for idx, value in enumerate(self._get_day_color_highlight()):
            color, _highlight = value
            date = idx + 1
            if date > 31:
                continue
            day_colors.append(color)
        return day_colors

    def __str__(self) -> str:
        info_list = []
        for idx, value in enumerate(self._get_day_color_highlight()):
            color, highlight = value
            date = idx + 1
            if date > 31:
                continue
            info_list.append(f"{date}{color.name[0].lower()}{'*' if highlight else ''}")
        return f"{self.DESCRIPTION}: " + " ".join(info_list)


class StartEndTime(TextDataFrame):
    DESCRIPTION: ClassVar[str] = "StartEndTime"
    LENGTH: ClassVar[int] = 0xB
    TYPE: ClassVar[int] = 0xE0
    ADDRESS: ClassVar[int] = 0x0

    def _get_start_end_times(self) -> Tuple[datetime.time, Optional[datetime.time]]:
        time_str_list = self.text.split("~")

        hour, minute = [int(v) for v in time_str_list[0].split(":")]
        start_time = datetime.time(hour, minute)

        end_time: Optional[datetime.time]
        hour, minute = [int(v) for v in time_str_list[1].split(":")]
        end_time = datetime.time(hour, minute)

        return (start_time, end_time)

    @property
    def start_time(self) -> datetime.time:
        return self._get_start_end_times()[0]

    @property
    def end_time(self) -> Optional[datetime.time]:
        return self._get_start_end_times()[1]

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == cls.LENGTH and frame_type == cls.TYPE and address == cls.ADDRESS:
            return True
        return False


class Illustration(Frame):
    DESCRIPTION: ClassVar[str] = "Illustration"

    @property
    def number(self) -> int:
        return self.data[0]

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == 0x1 and frame_type == 0x21 and address == 0x0:
            return True
        return False

    def __str__(self) -> str:
        return f"Illustration: {self.number}"


class Text(TextDataFrame):
    DESCRIPTION: ClassVar[str] = "Text"

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if (
            frame_type == 0x80  # Text with address < 0x100
            or frame_type == 0x81  # Text with address >= 0x100
        ):
            return True
        return False

    @classmethod
    def from_text_list(cls, text_list: List[str]) -> List["Text"]:
        frames: List[Text] = []
        address: int = 0

        for idx, text in enumerate(text_list):
            if idx + 1 < len(text_list):
                text = text + chr(0x1F)
            if len(text) < 0x100:
                frame_type: int = 0x80
                data = [
                    cls.UNICODE_TO_CASIO.get(c, cls.UNICODE_TO_CASIO["?"]) for c in text
                ]
                length: int = len(data)
                frames.append(
                    cls(
                        length=length,
                        type=frame_type,
                        address=address,
                        data=data,
                        checksum=cls.calculate_checksum(
                            length, frame_type, address, data
                        ),
                    )
                )
            else:
                raise NotImplementedError
            address += len(text)

        return frames


# End


class EndOfRecord(Frame):
    DESCRIPTION: ClassVar[str] = "End Of Record"
    LENGTH: ClassVar[int] = 0x0
    TYPE: ClassVar[int] = 0x0
    ADDRESS: ClassVar[int] = 0x100
    DATA: List[int] = []

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == cls.LENGTH and frame_type == cls.TYPE and address == cls.ADDRESS:
            return True
        return False

    @classmethod
    def get(cls) -> "EndOfRecord":
        return cls(
            cls.LENGTH,
            cls.TYPE,
            cls.ADDRESS,
            cls.DATA,
            cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, cls.DATA),
        )

    def __str__(self) -> str:
        return "End"


class EndOfTransmission(Frame):
    DESCRIPTION: ClassVar[str] = "End Of Transmission"
    LENGTH: ClassVar[int] = 0x0
    TYPE: ClassVar[int] = 0x0
    ADDRESS: ClassVar[int] = 0xFF00
    DATA: List[int] = []

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == cls.LENGTH and frame_type == cls.TYPE and address == cls.ADDRESS:
            return True
        return False

    @classmethod
    def get(cls) -> "EndOfTransmission":
        return cls(
            cls.LENGTH,
            cls.TYPE,
            cls.ADDRESS,
            cls.DATA,
            cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, cls.DATA),
        )

    def __str__(self) -> str:
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
        if self.address is None:
            raise ValueError("Missing address")
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
