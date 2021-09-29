import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, List, Optional, Set, Type, cast

from . import frame


class Record(ABC):

    DESCRIPTION: str = "Record"

    DIRECTORY: ClassVar[Type[frame.Directory]]

    DIRECTORY_TO_RECORD: Dict[Type[frame.Directory], Type["Record"]] = {}

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
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
    color: Optional[frame.ColorEnum]
    name: str
    number: Optional[str]
    address: Optional[str]
    field1: Optional[str]
    field2: Optional[str]
    field3: Optional[str]
    field4: Optional[str]
    field5: Optional[str]
    field6: Optional[str]

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.TelephoneDirectory

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
    def from_frames(cls, frames: List[frame.Frame]) -> "Telephone":
        text = ""
        color: Optional[frame.ColorEnum] = None
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.enum
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
            color, name, number, address, field1, field2, field3, field4, field5, field6
        )

    def to_frames(self) -> List[frame.Frame]:
        text_list: List[str] = [self.name]
        if self.number is not None:
            text_list.append(self.number)
        if self.address is not None:
            text_list.append(self.address)
        if self.field1 is not None:
            text_list.append(self.field1)
        if self.field2 is not None:
            text_list.append(self.field2)
        if self.field3 is not None:
            text_list.append(self.field3)
        if self.field4 is not None:
            text_list.append(self.field4)
        if self.field5 is not None:
            text_list.append(self.field5)
        if self.field6 is not None:
            text_list.append(self.field6)
        if self.color:
            return [
                frame.Color.from_color_enum(self.color),
                *frame.Text.from_text_list(text_list),
            ]
        else:
            return cast(List[frame.Frame], frame.Text.from_text_list(text_list))


@dataclass
class BusinessCard(Record):
    color: Optional[frame.ColorEnum]
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
        color: Optional[frame.ColorEnum] = None
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.enum
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
    color: Optional[frame.ColorEnum]
    text: str

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.MemoDirectory

    DESCRIPTION: str = "Memo"

    def __str__(self) -> str:
        return f"Memo: {repr(self.text)}"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Memo":
        text = ""
        color: Optional[frame.ColorEnum] = None
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.enum
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
    highlighted_days: Set[int]
    date_colors: Optional[List[frame.ColorEnum]]

    DIRECTORY: ClassVar[Type[frame.Directory]] = frame.CalendarDirectory

    DESCRIPTION: str = "Calendar"

    def __str__(self) -> str:
        info_list = []
        for date in range(1, 32):
            color = ""
            if self.date_colors:
                color = self.date_colors[date - 1].name[0].lower()
            highlight = "*" if date in self.highlighted_days else ""
            info_list.append(f"{date}{color}{highlight}")
        return f"{self.DESCRIPTION}: " + " ".join(info_list)

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Calendar":
        year: int = 0
        month: int = 0
        highlighted_days: Set[int] = set()
        date_colors: Optional[List[frame.ColorEnum]] = None
        for f in frames:
            if isinstance(f, frame.Date):
                if f.year is None:
                    raise ValueError("Missing year")
                year = f.year
                if f.month is None:
                    raise ValueError("Missing month")
                month = f.month
            elif isinstance(f, frame.DayHighlight):
                for day in f.days:
                    highlighted_days.add(day)
            elif isinstance(f, frame.DayColorHighlight):
                for date in f.highlighted_days:
                    highlighted_days.add(date)
                date_colors = f.day_colors
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if year == 0 or month == 0:
            raise ValueError("Missing Date frame")

        return cls(year, month, highlighted_days, date_colors)

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
            elif isinstance(f, frame.StartEndTime):
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
    priority: frame.PriorityEnum

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
        info_str += f"Priority: {self.priority.name} "
        info_str += self.description + " "
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "ToDo":
        deadline_date: Optional[datetime.date] = None
        deadline_time: Optional[datetime.time] = None
        alarm: Optional[datetime.time] = None
        checked_date: Optional[datetime.date] = None
        checked_time: Optional[datetime.time] = None
        description: str = ""
        priority: Optional[frame.PriorityEnum] = None

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
