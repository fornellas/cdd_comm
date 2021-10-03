import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional, Set, Type

from . import frame as frame_mod


def _raw_list_to_text_list(raw_list: List[Optional[str]]) -> List[str]:
    text_list: List[str] = []
    data: bool = False
    for e in reversed(raw_list):
        if e is None:
            if data:
                text_list.insert(0, "")
            else:
                continue
        else:
            data = True
            text_list.insert(0, e)
    return text_list


class Record(ABC):
    DESCRIPTION: str = "Record"
    DIRECTORY: ClassVar[Type[frame_mod.Directory]]
    DIRECTORY_TO_RECORD: Dict[Type[frame_mod.Directory], Type["Record"]] = {}

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        cls.DIRECTORY_TO_RECORD[cls.DIRECTORY] = cls

    @classmethod
    @abstractmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Record":
        pass

    @abstractmethod
    def to_frames(self) -> List[frame_mod.Frame]:
        pass


@dataclass
class Telephone(Record):
    name: str
    number: Optional[str]
    address: Optional[str]
    field1: Optional[str]
    field2: Optional[str]
    field3: Optional[str]
    field4: Optional[str]
    field5: Optional[str]
    field6: Optional[str]
    color: Optional[frame_mod.ColorEnum]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.TelephoneDirectory

    DESCRIPTION: str = "Telephone"

    @property
    def memo(self) -> Optional[str]:
        """
        CCS-8950 amalgamates various fields at a single "memo" field.
        """
        field_str: List[str] = []

        if self.field1:
            field_str.append(self.field1)
        if self.field2:
            field_str.append(self.field2)
        if self.field3:
            field_str.append(self.field3)
        if self.field4:
            field_str.append(self.field4)
        if self.field5:
            field_str.append(self.field5)
        if self.field6:
            field_str.append(self.field6)

        return "\n".join(field_str)

    def __str__(self) -> str:
        info_str = f"Telephone: {self.name}"
        if self.number is not None:
            info_str += f", {self.number}"
        if self.address is not None:
            info_str += f", {self.address}"
        if self.field1 is not None:
            info_str += f", {self.field1}"
        if self.field2 is not None:
            info_str += f", {self.field2}"
        if self.field3 is not None:
            info_str += f", {self.field3}"
        if self.field4 is not None:
            info_str += f", {self.field4}"
        if self.field5 is not None:
            info_str += f", {self.field5}"
        if self.field6 is not None:
            info_str += f", {self.field6}"
        info_str += f" ({self.color})"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Telephone":
        text = ""
        color: Optional[frame_mod.ColorEnum] = None
        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.enum
            elif isinstance(f, frame_mod.Text):
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
        field1 = None
        if len(fields) > 3:
            field1 = fields[3]
        field2 = None
        if len(fields) > 4:
            field2 = fields[4]
        field3 = None
        if len(fields) > 5:
            field3 = fields[5]
        field4 = None
        if len(fields) > 6:
            field4 = fields[6]
        field5 = None
        if len(fields) > 7:
            field5 = fields[7]
        field6 = None
        if len(fields) > 8:
            field6 = fields[8]
        return cls(
            name, number, address, field1, field2, field3, field4, field5, field6, color
        )

    def to_frames(self) -> List[frame_mod.Frame]:
        text_list: List[str] = _raw_list_to_text_list(
            [
                self.name,
                self.number,
                self.address,
                self.field1,
                self.field2,
                self.field3,
                self.field4,
                self.field5,
                self.field6,
            ]
        )

        frames: List[frame_mod.Frame] = []
        if self.color is not None:
            frames.append(frame_mod.Color.from_color_enum(self.color))
        frames.extend(frame_mod.Text.from_text_list(text_list))

        return frames


@dataclass
class BusinessCard(Record):
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
    color: Optional[frame_mod.ColorEnum]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.BusinessCardDirectory

    DESCRIPTION: str = "Business Card"

    def __str__(self) -> str:
        return f"Business Card: {repr(self.employer)}, {repr(self.name)}, {repr(self.telephone_number)}, {repr(self.telex_number)}, {repr(self.fax_number)}, {repr(self.position)}, {repr(self.department)}, {repr(self.po_box)}, {repr(self.address)}, {repr(self.memo)} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "BusinessCard":
        text = ""
        color: Optional[frame_mod.ColorEnum] = None
        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.enum
            elif isinstance(f, frame_mod.Text):
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
            color,
        )

    def to_frames(self) -> List[frame_mod.Frame]:
        text_list: List[str] = _raw_list_to_text_list(
            [
                self.employer,
                self.name,
                self.telephone_number,
                self.telex_number,
                self.fax_number,
                self.position,
                self.department,
                self.po_box,
                self.address,
                self.memo,
            ]
        )

        frames: List[frame_mod.Frame] = []
        if self.color is not None:
            frames.append(frame_mod.Color.from_color_enum(self.color))
        frames.extend(frame_mod.Text.from_text_list(text_list))

        return frames


@dataclass
class Memo(Record):
    text: str
    color: Optional[frame_mod.ColorEnum]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.MemoDirectory

    DESCRIPTION: str = "Memo"

    def __str__(self) -> str:
        return f"Memo: {repr(self.text)}"

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Memo":
        text = ""
        color: Optional[frame_mod.ColorEnum] = None
        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.enum
            elif isinstance(f, frame_mod.Text):
                text += f.text
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        return cls(text, color)

    def to_frames(self) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []

        if self.color is not None:
            frames.append(frame_mod.Color.from_color_enum(self.color))
        frames.extend(frame_mod.Text.from_text_list([self.text]))

        return frames


@dataclass
class Calendar(Record):
    year: int
    month: int
    days: Set[int]
    colors: Optional[List[frame_mod.ColorEnum]]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.CalendarDirectory

    DESCRIPTION: str = "Calendar"

    def __str__(self) -> str:
        info_list = []
        for date in range(1, 32):
            color = ""
            if self.colors:
                color = self.colors[date - 1].name[0].lower()
            highlight = "*" if date in self.days else ""
            info_list.append(f"{date}{color}{highlight}")
        return f"{self.DESCRIPTION}: " + " ".join(info_list)

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Calendar":
        year: int = 0
        month: int = 0
        days: Set[int] = set()
        colors: Optional[List[frame_mod.ColorEnum]] = None
        for f in frames:
            if isinstance(f, frame_mod.Date):
                if f.year is None:
                    raise ValueError("Missing year")
                year = f.year
                if f.month is None:
                    raise ValueError("Missing month")
                month = f.month
            elif isinstance(f, frame_mod.DayHighlight):
                for day in f.days:
                    days.add(day)
            elif isinstance(f, frame_mod.DayColorHighlight):
                for date in f.days:
                    days.add(date)
                colors = f.colors
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if year == 0 or month == 0:
            raise ValueError("Missing Date frame")

        return cls(year, month, days, colors)

    def to_frames(self) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []

        frames.append(frame_mod.Date.from_date(datetime.date(self.year, self.month, 1)))
        frames.append(frame_mod.DayHighlight.from_days(self.days))
        if self.colors is not None:
            frames.append(
                frame_mod.DayColorHighlight.from_days_and_colors(
                    self.days,
                    self.colors,
                )
            )
        return frames


@dataclass
class Schedule(Record):
    date: datetime.date
    start_time: Optional[datetime.time]
    end_time: Optional[datetime.time]
    alarm_time: Optional[datetime.time]
    illustration: Optional[int]
    description: Optional[str]
    color: Optional[frame_mod.ColorEnum]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.ScheduleKeeperDirectory

    DESCRIPTION: str = "Schedule"

    def __str__(self) -> str:
        return f"Schedule Keeper: {self.date}, {self.start_time}, {self.end_time}, {self.alarm_time}, {self.illustration}, {self.description} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Schedule":
        color: Optional[frame_mod.ColorEnum] = None
        date: Optional[datetime.date] = None
        start_time: Optional[datetime.time] = None
        end_time: Optional[datetime.time] = None
        alarm_time: Optional[datetime.time] = None
        illustration: Optional[int] = None
        description: Optional[str] = None

        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.enum
            elif isinstance(f, frame_mod.Date):
                date = f.date
            elif isinstance(f, frame_mod.StartEndTime):
                start_time = f.start_time
                end_time = f.end_time
            elif isinstance(f, frame_mod.Alarm):
                alarm_time = f.time
            elif isinstance(f, frame_mod.Illustration):
                illustration = f.number
            elif isinstance(f, frame_mod.Text):
                if description is None:
                    description = ""
                description += str(f.text)
            elif isinstance(f, frame_mod.Time):
                start_time = f.time
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if not date:
            raise ValueError("Missing date")
        if not start_time and not description:
            raise ValueError("Missing either start_time or description")

        return cls(
            date,
            start_time,
            end_time,
            alarm_time,
            illustration,
            description,
            color,
        )

    def to_frames(self) -> List[frame_mod.Frame]:
        raise NotImplementedError


@dataclass
class Reminder(Record):
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]
    alarm_time: Optional[datetime.time]
    description: str
    color: Optional[frame_mod.ColorEnum]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.ReminderDirectory

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
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Reminder":
        color: Optional[frame_mod.ColorEnum] = None
        year: Optional[int] = None
        month: Optional[int] = None
        day: Optional[int] = None
        alarm_time: Optional[datetime.time] = None
        description: str = ""

        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.enum
            elif isinstance(f, frame_mod.Date):
                year = f.year
                month = f.month
                day = f.day
            elif isinstance(f, frame_mod.Alarm):
                alarm_time = f.time
            elif isinstance(f, frame_mod.Text):
                description = f.text
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if description == "":
            raise ValueError("Missing description")

        return cls(year, month, day, alarm_time, description, color)

    def to_frames(self) -> List[frame_mod.Frame]:
        raise NotImplementedError


@dataclass
class ToDo(Record):
    deadline_date: Optional[datetime.date]
    deadline_time: Optional[datetime.time]
    alarm: Optional[datetime.time]
    checked_date: Optional[datetime.date]
    checked_time: Optional[datetime.time]
    description: str
    priority: frame_mod.PriorityEnum

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.ToDoDirectory

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
        info_str += f"Priority: {self.priority.name} "
        info_str += self.description + " "
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "ToDo":
        deadline_date: Optional[datetime.date] = None
        deadline_time: Optional[datetime.time] = None
        alarm: Optional[datetime.time] = None
        checked_date: Optional[datetime.date] = None
        checked_time: Optional[datetime.time] = None
        description: str = ""
        priority: Optional[frame_mod.PriorityEnum] = None

        for f in frames:
            if isinstance(f, frame_mod.DeadlineDate):
                deadline_date = f.date
            elif isinstance(f, frame_mod.DeadlineTime):
                deadline_time = f.time
            elif isinstance(f, frame_mod.ToDoAlarm):
                alarm = f.time
            elif isinstance(f, frame_mod.Date):
                checked_date = f.date
            elif isinstance(f, frame_mod.Time):
                checked_time = f.time
            elif isinstance(f, frame_mod.Text):
                description = f.text
            elif isinstance(f, frame_mod.Priority):
                priority = f.enum
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if description == "":
            raise ValueError("Missing description")

        if priority is None:
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

    def to_frames(self) -> List[frame_mod.Frame]:
        raise NotImplementedError


@dataclass
class Expense(Record):
    date: datetime.date
    amount: float
    payment_type: Optional[str]
    expense_type: Optional[str]
    rcpt: Optional[str]  # Empty for CSF-8950
    bus: Optional[str]  # Empty for CSF-8950
    description: Optional[str]
    color: Optional[frame_mod.ColorEnum]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.ExpenseManagerDirectory

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
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Expense":
        text = ""
        color: Optional[frame_mod.ColorEnum] = None
        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.enum
            elif isinstance(f, frame_mod.Text):
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
            date, amount, payment_type, expense_type, rcpt, bus, description, color
        )

    def to_frames(self) -> List[frame_mod.Frame]:
        raise NotImplementedError
