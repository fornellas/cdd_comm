from abc import ABC, abstractmethod
from typing import List, Optional, Dict, ClassVar, Set
from . import frame
from dataclasses import dataclass
import datetime


class Record(ABC):

    DESCRIPTION: str = "Record"

    DIRECTORY: ClassVar[Optional[frame.Directory]] = None

    DIRECTORY_TO_RECORD: Dict[frame.Directory, "Record"] = {}

    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        cls.DIRECTORY_TO_RECORD[cls.DIRECTORY] = cls

    @classmethod
    @abstractmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Record":
        pass

    @abstractmethod
    def to_frames(self) -> List[frame.Frame]:
        pass


@dataclass
class Telephone(Record):
    color: str
    name: str
    number: Optional[str]
    address: Optional[str]
    memo: Optional[str]

    DIRECTORY: ClassVar[Optional[frame.Directory]] = frame.TelephoneDirectory

    DESCRIPTION: str = "Telephone"

    def __str__(self):
        return f"Telephone: {repr(self.name)}, {repr(self.number)}, {repr(self.address)}, {repr(self.memo)} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Telephone":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += str(f.text)
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")
        fields: List[str] = [None if v == "" else v for v in text.split(chr(0x1F))]
        if not len(fields):
            raise ValueError("Missing name text frame")
        name = fields[0]
        number = None
        if len(fields) > 1:
            number = fields[1]
        address = None
        if len(fields) > 2:
            address = fields[2]
        memo = None
        if len(fields) > 3:
            memo = fields[3]
        return cls(color, name, number, address, memo)

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError


@dataclass
class BusinessCard(Record):
    color: str
    employer: str
    name: str
    telephone_number: Optional[str]
    telex_number: Optional[str]
    fax_number: Optional[str]
    position: Optional[str]
    department: Optional[str]
    po_box: Optional[str]
    address: Optional[str]
    memo: Optional[str]

    DIRECTORY: ClassVar[Optional[frame.Directory]] = frame.BusinessCardDirectory

    DESCRIPTION: str = "Business Card"

    def __str__(self):
        return f"Business Card: {repr(self.employer)}, {repr(self.name)}, {repr(self.telephone_number)}, {repr(self.telex_number)}, {repr(self.fax_number)}, {repr(self.position)}, {repr(self.department)}, {repr(self.po_box)}, {repr(self.address)}, {repr(self.memo)} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "BusinessCard":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += str(f.text)
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")
        fields: List[str] = [None if v == "" else v for v in text.split(chr(0x1F))]
        if len(fields) < 2:
            raise ValueError("Missing name and / or employer text frame")
        employer = fields[0]
        name = fields[1]
        telephone_number = None
        if len(fields) > 2:
            telephone_number = fields[2]
        telex_number = None
        if len(fields) > 3:
            telex_number = fields[3]
        fax_number = None
        if len(fields) > 4:
            fax_number = fields[4]
        position = None
        if len(fields) > 5:
            position = fields[5]
        department = None
        if len(fields) > 6:
            department = fields[6]
        po_box = None
        if len(fields) > 7:
            po_box = fields[7]
        address = None
        if len(fields) > 8:
            address = fields[8]
        memo = None
        if len(fields) > 9:
            memo = fields[9]

        return cls(
            color,
            employer,
            name,
            telephone_number,
            telex_number,
            fax_number,
            position,
            department,
            po_box,
            address,
            memo,
        )

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError


@dataclass
class Memo(Record):
    color: str
    text: str

    DIRECTORY: ClassVar[Optional[frame.Directory]] = frame.MemoDirectory

    DESCRIPTION: str = "Memo"

    def __str__(self):
        return f"Memo: {repr(self.text)}"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Memo":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += str(f.text)
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        return cls(color, text)

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError


@dataclass
class Calendar(Record):
    year: int
    month: int
    highlighted_dates: Set[int]
    date_colors: List[str]

    DIRECTORY: ClassVar[Optional[frame.Directory]] = frame.CalendarDirectory

    DESCRIPTION: str = "Calendar"

    def __str__(self):
        info_list = []
        for date in range(1, 32):
            color = self.date_colors[date - 1][0].lower()
            highlight = "*" if date in self.highlighted_dates else ""
            info_list.append(f"{date}{color}{highlight}")
        return f"{self.DESCRIPTION}: " + " ".join(info_list)

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Calendar":
        year: int = 0
        month: int = 0
        highlighted_dates: Set[int] = set()
        date_colors: List[str] = []
        for f in frames:
            if isinstance(f, frame.Date):
                year = f.date.year
                month = f.date.month
            elif isinstance(f, frame.DatesHighlight):
                for date in f.dates:
                    highlighted_dates.add(date)
            elif isinstance(f, frame.DateColorHighlight):
                for date in f.highlighted_dates:
                    highlighted_dates.add(date)
                date_colors = f.date_colors
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if year == 0 or month == 0:
            raise ValueError("Missing Date frame")

        return cls(year, month, highlighted_dates, date_colors)

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError


@dataclass
class ScheduleKeeper(Record):
    color: str
    date: datetime.date
    start_time: Optional[datetime.time]
    end_time: Optional[datetime.time]
    alarm_time: Optional[datetime.time]
    illustration: Optional[int]
    description: Optional[str]

    DIRECTORY: ClassVar[Optional[frame.Directory]] = frame.ScheduleKeeperDirectory

    DESCRIPTION: str = "Schedule Keeper"

    def __str__(self):
        return f"Schedule Keeper: {self.date}, {self.start_time}, {self.end_time}, {self.alarm_time}, {self.illustration}, {self.description} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "ScheduleKeeper":
        color: str = "Blue"
        date: datetime.date = None
        start_time: datetime.time = None
        end_time: datetime.time = None
        alarm_time: datetime.time = None
        illustration: int = None
        description: Optional[str] = None

        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Date):
                date = f.date
            elif isinstance(f, frame.Time):
                start_time = f.start_time
                end_time = f.end_time
            elif isinstance(f, frame.Alarm):
                alarm_time = f.time
            elif isinstance(f, frame.Illustration):
                illustration = f.number
            elif isinstance(f, frame.Text):
                if description is None:
                    description = ""
                description += str(f.text)
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if not date:
            raise ValueError("Missing date")
        if not start_time and not description:
            raise ValueError("Missing either start_time or description")

        return cls(
            color,
            date,
            start_time,
            end_time,
            alarm_time,
            illustration,
            description,
        )

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError
