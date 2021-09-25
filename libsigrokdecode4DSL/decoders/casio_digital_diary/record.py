from abc import ABC, abstractmethod
from typing import List, Optional, Dict, ClassVar, Set, Type
from . import frame
from dataclasses import dataclass
import datetime


class Record(ABC):

    DESCRIPTION: str = "Record"

    DIRECTORY: ClassVar[Type[frame.Directory]]

    DIRECTORY_TO_RECORD: Dict[Type[frame.Directory], "Record"] = {}

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
    free1: Optional[str]
    free2: Optional[str]
    free3: Optional[str]
    free4: Optional[str]
    free5: Optional[str]
    free6: Optional[str]

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.TelephoneDirectory

    DESCRIPTION: str = "Telephone"

    @property
    def memo(self) -> Optional[str]:
        """
        CCS-8950's free1
        """
        return self.free1

    def __str__(self) -> str:
        info_str = f"Telephone: {self.name}"
        if self.number is not None:
            info_str += f", {self.number}"
        if self.address is not None:
            info_str += f", {self.address}"
        if self.free1 is not None:
            info_str += f", {self.free1}"
        if self.free2 is not None:
            info_str += f", {self.free2}"
        if self.free3 is not None:
            info_str += f", {self.free3}"
        if self.free4 is not None:
            info_str += f", {self.free4}"
        if self.free5 is not None:
            info_str += f", {self.free5}"
        if self.free6 is not None:
            info_str += f", {self.free6}"
        info_str += f" ({self.color})"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Telephone":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += f.text
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")
        fields: List[Optional[str]] = [
            None if v == "" else v for v in text.split(chr(0x1F))
        ]
        if not len(fields):
            raise ValueError("Missing name text frame")
        name = fields[0]
        if name is None:
            raise ValueError("Missing name text field")
        number = None
        if len(fields) > 1:
            number = fields[1]
        address = None
        if len(fields) > 2:
            address = fields[2]
        free1 = None
        if len(fields) > 3:
            free1 = fields[3]
        free2 = None
        if len(fields) > 4:
            free2 = fields[4]
        free3 = None
        if len(fields) > 5:
            free3 = fields[5]
        free4 = None
        if len(fields) > 6:
            free4 = fields[6]
        free5 = None
        if len(fields) > 7:
            free5 = fields[7]
        free6 = None
        if len(fields) > 8:
            free6 = fields[8]
        return cls(
            color, name, number, address, free1, free2, free3, free4, free5, free6
        )

    def to_frames(self) -> List[frame.Frame]:
        text_list: List[str] = [self.name]
        if self.number is not None:
            text_list.append(self.number)
        if self.address is not None:
            text_list.append(self.address)
        if self.free1 is not None:
            text_list.append(self.free1)
        if self.free2 is not None:
            text_list.append(self.free2)
        if self.free3 is not None:
            text_list.append(self.free3)
        if self.free4 is not None:
            text_list.append(self.free4)
        if self.free5 is not None:
            text_list.append(self.free5)
        if self.free6 is not None:
            text_list.append(self.free6)
        return [frame.Color.get(self.color), *frame.Text.from_text_list(text_list)]


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

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.BusinessCardDirectory

    DESCRIPTION: str = "Business Card"

    def __str__(self) -> str:
        return f"Business Card: {repr(self.employer)}, {repr(self.name)}, {repr(self.telephone_number)}, {repr(self.telex_number)}, {repr(self.fax_number)}, {repr(self.position)}, {repr(self.department)}, {repr(self.po_box)}, {repr(self.address)}, {repr(self.memo)} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "BusinessCard":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += f.text
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")
        fields: List[Optional[str]] = [
            None if v == "" else v for v in text.split(chr(0x1F))
        ]
        if len(fields) < 2:
            raise ValueError("Missing name and / or employer text frame")
        employer = fields[0]
        if employer is None:
            raise ValueError("Missing employer")
        name = fields[1]
        if name is None:
            raise ValueError("Missing name")
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

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.MemoDirectory

    DESCRIPTION: str = "Memo"

    def __str__(self) -> str:
        return f"Memo: {repr(self.text)}"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Memo":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += f.text
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
    date_colors: Optional[List[str]]

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.CalendarDirectory

    DESCRIPTION: str = "Calendar"

    def __str__(self) -> str:
        info_list = []
        for date in range(1, 32):
            color = ""
            if self.date_colors is not None:
                color = self.date_colors[date - 1][0].lower()
            highlight = "*" if date in self.highlighted_dates else ""
            info_list.append(f"{date}{color}{highlight}")
        return f"{self.DESCRIPTION}: " + " ".join(info_list)

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Calendar":
        year: int = 0
        month: int = 0
        highlighted_dates: Set[int] = set()
        date_colors: Optional[List[str]] = None
        for f in frames:
            if isinstance(f, frame.Date):
                if f.year is None:
                    raise ValueError("Missing year")
                year = f.year
                if f.month is None:
                    raise ValueError("Missing month")
                month = f.month
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

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.ScheduleKeeperDirectory

    DESCRIPTION: str = "Schedule Keeper"

    def __str__(self) -> str:
        return f"Schedule Keeper: {self.date}, {self.start_time}, {self.end_time}, {self.alarm_time}, {self.illustration}, {self.description} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "ScheduleKeeper":
        color: str = "Blue"
        date: Optional[datetime.date] = None
        start_time: Optional[datetime.time] = None
        end_time: Optional[datetime.time] = None
        alarm_time: Optional[datetime.time] = None
        illustration: Optional[int] = None
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


@dataclass
class Reminder(Record):
    color: str
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]
    alarm_time: Optional[datetime.time]
    description: str

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.ReminderDirectory

    DESCRIPTION: str = "Reminder"

    def __str__(self) -> str:
        info_str = "Reminder: "
        if self.year:
            info_str += str(self.year) + "-"
        else:
            info_str += "-----"
        if self.month:
            info_str += str(self.month) + "-"
        else:
            info_str += "---"
        if self.day:
            info_str += str(self.day) + " "
        else:
            info_str += "-- "
        if self.alarm_time:
            info_str += f"{self.alarm_time.hour}:{self.alarm_time.minute}"
        else:
            info_str += "--:--"
        info_str += f" {self.description}"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Reminder":
        color: str = "Blue"
        year: Optional[int] = None
        month: Optional[int] = None
        day: Optional[int] = None
        alarm_time: Optional[datetime.time] = None
        description: str = ""

        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Date):
                year = f.year
                month = f.month
                day = f.day
            elif isinstance(f, frame.Alarm):
                alarm_time = f.time
            elif isinstance(f, frame.Text):
                description = f.text
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if description == "":
            raise ValueError("Missing description")

        return cls(color, year, month, day, alarm_time, description)

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError


@dataclass
class ToDo(Record):
    deadline_date: Optional[datetime.date]
    deadline_time: Optional[datetime.time]
    alarm: Optional[datetime.time]
    checked_date: Optional[datetime.date]
    checked_time: Optional[datetime.time]
    description: str
    priority: str

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.ToDoDirectory

    DESCRIPTION: str = "To Do"

    def __str__(self) -> str:
        info_str = "To Do: "
        if self.deadline_date:
            info_str += "Deadline: " + str(self.deadline_date) + " "
        if self.deadline_time:
            info_str += str(self.deadline_time) + " "
        if self.alarm:
            info_str += "Alarm: " + str(self.alarm) + " "
        if self.checked_date:
            info_str += "Checked: " + str(self.checked_date) + " "
        if self.checked_time:
            info_str += str(self.checked_time) + " "
        info_str += self.description + " "
        info_str += self.priority
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "ToDo":
        deadline_date: Optional[datetime.date] = None
        deadline_time: Optional[datetime.time] = None
        alarm: Optional[datetime.time] = None
        checked_date: Optional[datetime.date] = None
        checked_time: Optional[datetime.time] = None
        description: str = ""
        priority: str = ""

        for f in frames:
            if isinstance(f, frame.DeadlineDate):
                deadline_date = f.date
            elif isinstance(f, frame.DeadlineTime):
                deadline_time = f.time
            elif isinstance(f, frame.ToDoAlarm):
                alarm = f.time
            elif isinstance(f, frame.Date):
                checked_date = f.date
            elif isinstance(f, frame.Time):
                checked_time = f.time
            elif isinstance(f, frame.Text):
                description = f.text
            elif isinstance(f, frame.Priority):
                priority = f.value
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if description == "":
            raise ValueError("Missing description")

        if priority == "":
            raise ValueError("Missing priority")

        return cls(
            deadline_date,
            deadline_time,
            alarm,
            checked_date,
            checked_time,
            description,
            priority,
        )

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError


@dataclass
class Expense(Record):
    color: str
    date: datetime.date
    amount: float
    payment_type: Optional[str]
    expense_type: Optional[str]
    rcpt: Optional[str]  # Empty for CSF-8950
    bus: Optional[str]  # Empty for CSF-8950
    description: Optional[str]

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.ExpenseManagerDirectory

    DESCRIPTION: str = "Expense"

    def __str__(self) -> str:
        info_str = f"Expense: {self.date}, Amount: {self.amount}"
        if self.payment_type is not None:
            info_str += f", Payment Type: {self.payment_type}"
        if self.expense_type is not None:
            info_str += f", Expense Type: {self.expense_type}"
        if self.rcpt is not None:
            info_str += f", rcpt: {self.rcpt}"
        if self.bus is not None:
            info_str += f", bus: {self.bus}"
        if self.description is not None:
            info_str += f", Description: {self.description}"
        info_str += f" ({self.color})"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Expense":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += f.text
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")
        fields: List[Optional[str]] = [
            None if v == "" else v for v in text.split(chr(0x1F))
        ]

        if len(fields) < 2:
            raise ValueError("Missing date and/or amount.")

        date_str = fields[0]
        assert date_str is not None
        year_str = int(date_str[0:4])
        month_str = int(date_str[4:6])
        day_str = int(date_str[6:8])
        date = datetime.date(year_str, month_str, day_str)

        amount_str = fields[1]
        assert amount_str is not None
        amount = float(amount_str)

        payment_type: Optional[str] = None
        if len(fields) > 2:
            payment_type = fields[2]

        expense_type: Optional[str] = None
        if len(fields) > 3:
            expense_type = fields[3]

        rcpt: Optional[str] = None
        if len(fields) > 4:
            rcpt = fields[4]

        bus: Optional[str] = None
        if len(fields) > 5:
            bus = fields[5]

        description: Optional[str] = None
        if len(fields) > 6:
            description = fields[6]

        return cls(
            color, date, amount, payment_type, expense_type, rcpt, bus, description
        )

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError
