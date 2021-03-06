import datetime
import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, Type, Union

##
## Frame
##


@dataclass
class Frame:
    length: int
    frame_type: int
    address: int
    data: List[int]
    checksum: int

    DESCRIPTION: ClassVar[str] = "Frame"

    SUBCLASSES: ClassVar[List[Type["Frame"]]] = []

    _FRAME_START: int = 0x3A

    @classmethod
    def get_kebab_case_description(cls) -> str:
        return cls.DESCRIPTION.lower().replace(" ", "-")

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.SUBCLASSES.append(cls)

    def __str__(self) -> str:
        return "Frame: " + "".join(
            chr(d) if chr(d).isprintable() else f"[{hex(d)}]" for d in self.data
        )

    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: Union[Any, "Frame"]) -> bool:
        if type(other) != type(self):
            return False
        return (
            self.length == other.length
            and self.frame_type == other.frame_type
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
            self.length, self.frame_type, self.address, self.data
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
            *self._encode(self.frame_type),
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


class ScheduleDirectory(Directory):
    DESCRIPTION: ClassVar[str] = "Schedule Directory"
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


class Colors(Enum):
    BLUE: int = 0x1
    ORANGE: int = 0x2
    GREEN: int = 0x4


class Color(Frame):
    DESCRIPTION: ClassVar[str] = "Color"
    LENGTH: ClassVar[int] = 0x1
    TYPE: ClassVar[int] = 0x71
    ADDRESS: ClassVar[int] = 0x0
    _CODE_TO_COLOR: Dict[int, Colors] = {color.value: color for color in list(Colors)}
    _COLOR_TO_CODE: Dict[Colors, int] = {
        color: code for code, color in _CODE_TO_COLOR.items()
    }

    @property
    def color(self) -> Colors:
        return self._CODE_TO_COLOR[self.data[0]]

    @property
    def name(self) -> str:
        return self.color.name

    @classmethod
    def from_color(cls, color: Colors) -> "Color":
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


class TextDataFrame(ABC, Frame):
    CASIO_TO_UNICODE: Dict[int, str] = {
        10: chr(0x1F),  # Unit separator
        13: "\n",
        21: "??",
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
        124: "??",
        125: "}",
        126: "~",
        181: "??",
        144: "??",
        182: "??",
        183: "??",
        184: "??",
        185: "??",
        186: "??",
        187: "??",
        188: "??",
        189: "??",
        198: "??",
        199: "??",
        200: "??",
        201: "??",
        202: "??",
        173: "??",
        160: "??",
        130: "??",
        161: "??",
        162: "??",
        163: "??",
        133: "??",
        138: "??",
        141: "??",
        149: "??",
        151: "??",
        131: "??",
        136: "??",
        140: "??",
        147: "??",
        150: "??",
        168: "??",
        142: "??",
        203: "??",
        204: "??",
        153: "??",
        154: "??",
        205: "??",
        207: "??",
        165: "??",
        209: "??",
        146: "??",
        128: "??",
        143: "??",
        232: "??",
        225: "??",
        190: "??",
        155: "??",
        132: "??",
        137: "??",
        139: "??",
        148: "??",
        129: "??",
        206: "??",
        208: "??",
        164: "??",
        210: "??",
        145: "??",
        135: "??",
        134: "??",
        237: "??",
        156: "??",
        157: "??",
        234: "??",
        166: "??",
        167: "??",
        245: "??",
        246: "??",
        241: "??",
        248: "??",
        253: "??",
        211: "??",
        230: "??",
        171: "??",
        172: "??",
        212: "??",
        159: "??",
        179: "|",
        216: "???",
        174: "???",
        175: "???",
        251: "???",
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
        return "".join(self.CASIO_TO_UNICODE[d] for d in self.data)

    def __str__(self) -> str:
        return f"{self.DESCRIPTION}: {self.text}"


class Date(TextDataFrame):
    DESCRIPTION: ClassVar[str] = "Date"
    LENGTH: ClassVar[int] = 0xA
    TYPE: ClassVar[int] = 0xF0
    ADDRESS: ClassVar[int] = 0x0

    @classmethod
    def from_values(
        cls, year: Optional[int], month: Optional[int], day: Optional[int]
    ) -> "Date":
        year_str = "----"
        if year is not None:
            year_str = "%.4d" % (year)
        month_str = "--"
        if month is not None:
            month_str = "%.2d" % (month)
        day_str = "--"
        if day is not None:
            day_str = "%.2d" % day
        data: List[int] = [
            cls.UNICODE_TO_CASIO[c] for c in f"{year_str}-{month_str}-{day_str}"
        ]
        return cls(
            length=cls.LENGTH,
            frame_type=cls.TYPE,
            address=cls.ADDRESS,
            data=data,
            checksum=cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

    @classmethod
    def from_date(cls, date: datetime.date) -> "Date":
        data: List[int] = [
            cls.UNICODE_TO_CASIO[c]
            for c in "%.4d-%.2d-%.2d" % (date.year, date.month, date.day)
        ]
        return cls(
            length=cls.LENGTH,
            frame_type=cls.TYPE,
            address=cls.ADDRESS,
            data=data,
            checksum=cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

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

    @classmethod
    def from_time(cls, time: datetime.time) -> "Time":
        data: List[int] = [
            cls.UNICODE_TO_CASIO[c] for c in "%.2d:%.2d" % (time.hour, time.minute)
        ]
        return cls(
            length=cls.LENGTH,
            frame_type=cls.TYPE,
            address=cls.ADDRESS,
            data=data,
            checksum=cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

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


class Priorities(Enum):
    A: int = 0x10
    B: int = 0x20
    C: int = 0x30


class Priority(Frame):
    DESCRIPTION: ClassVar[str] = "Priority"
    LENGTH: ClassVar[int] = 0x1
    TYPE: ClassVar[int] = 0x72
    ADDRESS: ClassVar[int] = 0x0
    _CODE_TO_PRIORITY: Dict[int, Priorities] = {
        priority.value: priority for priority in list(Priorities)
    }
    _PRIORITY_TO_CODE: Dict[Priorities, int] = {
        priority: code for code, priority in _CODE_TO_PRIORITY.items()
    }
    _PRIORITY_TO_COLOR: Dict[Priorities, Colors] = {
        Priorities.A: Colors.ORANGE,
        Priorities.B: Colors.BLUE,
        Priorities.C: Colors.GREEN,
    }

    @property
    def color(self) -> Colors:
        return self._PRIORITY_TO_COLOR[self.priority]

    @property
    def priority(self) -> Priorities:
        return self._CODE_TO_PRIORITY[self.data[0]]

    @classmethod
    def from_priority(cls, priority: Priorities) -> "Priority":
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
        return f"{self.DESCRIPTION}: {self.priority.name}"


class DayHighlight(Frame):
    DESCRIPTION: ClassVar[str] = "Day Highlight"
    LENGTH: ClassVar[int] = 0x4
    TYPE: ClassVar[int] = 0xD0
    ADDRESS: ClassVar[int] = 0x0

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == cls.LENGTH and frame_type == cls.TYPE and address == cls.ADDRESS:
            return True
        return False

    @classmethod
    def from_days(cls, days: Set[int]) -> "DayHighlight":
        if len(days) > cls.LENGTH * 8:
            raise ValueError("Invalid number of days")

        data: List[int] = [0] * cls.LENGTH

        for day in days:
            byte: int = int((day - 1) / 8)
            bit: int = (day - 1) % 8
            data[byte] |= 1 << bit

        data = list(reversed(data))

        return cls(
            length=cls.LENGTH,
            frame_type=cls.TYPE,
            address=cls.ADDRESS,
            data=data,
            checksum=cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

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
    LENGTH: ClassVar[int] = 0x20
    TYPE: ClassVar[int] = 0x78
    ADDRESS: ClassVar[int] = 0x0

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == cls.LENGTH and frame_type == cls.TYPE and address == cls.ADDRESS:
            return True
        return False

    @classmethod
    def from_days_and_colors(
        cls, days: Set[int], colors: List[Colors]
    ) -> "DayColorHighlight":
        data: List[int] = [0] * cls.LENGTH

        if len(days) > cls.LENGTH:
            raise ValueError("invalid days lengths")
        if len(colors) >= cls.LENGTH:
            raise ValueError(f"invalid colors length: {len(colors)}")

        for day in days:
            if day < 0 or day > 31:
                raise ValueError("invalid day")
            idx = day - 1
            data[idx] |= 0x80

        for idx, color in enumerate(colors):
            data[idx] |= color.value

        data = list(reversed(data))

        return cls(
            length=cls.LENGTH,
            frame_type=cls.TYPE,
            address=cls.ADDRESS,
            data=data,
            checksum=cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

    def _get_day_color_highlight(self) -> List[Tuple[Colors, bool]]:
        color_highlight: List[Tuple[Colors, bool]] = []
        for info in reversed(self.data):
            color: Colors
            for color_candidate in list(Colors):
                if info & color_candidate.value:
                    color = color_candidate
                    break
            highlight: bool = False
            if info & 0x80:
                highlight = True
            color_highlight.append((color, highlight))
        return color_highlight

    @property
    def days(self) -> Set[int]:
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
    def colors(self) -> List[Colors]:
        day_colors: List[Colors] = []
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

    @classmethod
    def from_start_end_times(
        cls, start_time: datetime.time, end_time: datetime.time
    ) -> "StartEndTime":
        data: List[int] = [
            cls.UNICODE_TO_CASIO[c]
            for c in "%.2d:%.2d~%.2d:%.2d"
            % (start_time.hour, start_time.minute, end_time.hour, end_time.minute)
        ]
        return cls(
            length=cls.LENGTH,
            frame_type=cls.TYPE,
            address=cls.ADDRESS,
            data=data,
            checksum=cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

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
    LENGTH: ClassVar[int] = 0x1
    TYPE: ClassVar[int] = 0x21
    ADDRESS: ClassVar[int] = 0x0

    @classmethod
    def from_number(cls, number: int) -> "Illustration":
        data: List[int] = [number]
        return cls(
            cls.LENGTH,
            cls.TYPE,
            cls.ADDRESS,
            data,
            cls.calculate_checksum(cls.LENGTH, cls.TYPE, cls.ADDRESS, data),
        )

    @property
    def number(self) -> int:
        return self.data[0]

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if length == cls.LENGTH and frame_type == cls.TYPE and address == cls.ADDRESS:
            return True
        return False

    def __str__(self) -> str:
        return f"Illustration: {self.number}"


class Text(TextDataFrame):
    DESCRIPTION: ClassVar[str] = "Text"
    TYPE_LOW: ClassVar[int] = 0x80
    TYPE_HIGH: ClassVar[int] = 0x81
    _MAX_CHUNK_SIZE: int = 0x80
    MAX_LENGTH: ClassVar[int] = 376

    @classmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        if (
            frame_type == cls.TYPE_LOW  # Text with address < 0x100
            or frame_type == cls.TYPE_HIGH  # Text with address >= 0x100
        ):
            return True
        return False

    @classmethod
    def _from_text(
        cls, text: str, last: bool, address: int
    ) -> Tuple[List["Text"], int]:
        if not last:
            text += chr(0x1F)

        if len(text) > cls.MAX_LENGTH:
            raise ValueError("Text too long")

        frame_list: List["Text"] = []

        lines = text.split("\n")

        for idx, line in enumerate(lines):
            last = idx + 1 == len(lines)

            for chunk in textwrap.wrap(
                line,
                width=cls._MAX_CHUNK_SIZE,
                expand_tabs=False,
                replace_whitespace=False,
                break_on_hyphens=False,
                drop_whitespace=False,
            )[:3]:
                if address >= (cls._MAX_CHUNK_SIZE * 2):
                    frame_type = cls.TYPE_HIGH
                    frame_address = address % (cls._MAX_CHUNK_SIZE * 2)
                else:
                    frame_type = cls.TYPE_LOW
                    frame_address = address

                data: List[int] = []
                for c in chunk:
                    if c not in cls.UNICODE_TO_CASIO:
                        raise ValueError(f"Invalid character: {repr(c)}")
                    data.append(cls.UNICODE_TO_CASIO[c])
                if not last:
                    data.append(cls.UNICODE_TO_CASIO["\n"])
                length = len(data)
                frame_list.append(
                    cls(
                        length=length,
                        frame_type=frame_type,
                        address=frame_address,
                        data=data,
                        checksum=cls.calculate_checksum(
                            length, frame_type, frame_address, data
                        ),
                    )
                )
                address += len(data)

        return frame_list, address

    @classmethod
    def from_text_list(cls, text_list: List[str]) -> List["Text"]:
        if sum(map(len, text_list)) > cls.MAX_LENGTH:
            raise ValueError("Text too long")

        frames: List[Text] = []
        address: int = 0

        for idx, text in enumerate(text_list):
            last: bool = idx + 1 == len(text_list)
            new_frames, address = cls._from_text(text=text, last=last, address=address)
            frames.extend(new_frames)

        return frames

    @classmethod
    def from_text(cls, text: str) -> List["Text"]:
        return cls.from_text_list([text])


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

    def __init__(self) -> None:
        self.length: Optional[int] = None
        self.frame_type: Optional[int] = None
        self._address_low: Optional[int] = None
        self._address_high: Optional[int] = None
        self.address: Optional[int] = None
        self._data_count: Optional[int] = None
        self.data = []
        self.checksum: Optional[int] = None

    def add_data(self, data: int) -> Tuple[str, Optional[Frame]]:
        if self.length is None:
            self.length = data
            self._data_count = self.length
            return ("Length", None)
        if self.frame_type is None:
            self.frame_type = data
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
                self.frame_type,
                self.address,
                self.data,
                self.checksum,
            ),
        )
