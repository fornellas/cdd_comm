from dataclasses import dataclass
from typing import List, Type, Iterable, ClassVar, Dict, Optional, Tuple
from abc import ABC, abstractmethod


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


class Color(Frame):
    DESCRIPTION: str = "Color"
    _NAMES: Dict[int, str] = {
        0x1: "Blue",
        0x2: "Orange",
        0x4: "Green",
    }

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
        return f"{self.DESCRIPTION}: {self._NAMES[self.data[0]]}"


class TextDataFrame(Frame, ABC):
    @classmethod
    @abstractmethod
    def match(cls, length: int, frame_type: int, address: int, data: List[int]) -> bool:
        return False

    @property
    def _data_str(self) -> str:
        # FIXME map data to Unicode chars
        return "".join(
            chr(d) if chr(d).isprintable() else f"({hex(d)})" for d in self.data
        )

    def __str__(self):
        return f"{self.DESCRIPTION}: {self._data_str}"


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
