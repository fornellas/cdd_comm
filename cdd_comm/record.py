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
    free1: Optional[str]
    free2: Optional[str]
    free3: Optional[str]
    free4: Optional[str]
    free5: Optional[str]
    free6: Optional[str]
    color: Optional[frame_mod.Colors]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.TelephoneDirectory

    DESCRIPTION: str = "Telephone"

    def __str__(self) -> str:
        info_str = f"Telephone: {repr(self.name)}"
        if self.number is not None:
            info_str += f", {repr(self.number)}"
        if self.address is not None:
            info_str += f", {repr(self.address)}"
        if self.free1 is not None:
            info_str += f", {repr(self.free1)}"
        if self.free2 is not None:
            info_str += f", {repr(self.free2)}"
        if self.free3 is not None:
            info_str += f", {repr(self.free3)}"
        if self.free4 is not None:
            info_str += f", {repr(self.free4)}"
        if self.free5 is not None:
            info_str += f", {repr(self.free5)}"
        if self.free6 is not None:
            info_str += f", {repr(self.free6)}"
        if self.color is not None:
            info_str += f" ({self.color.name})"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Telephone":
        text = ""
        color: Optional[frame_mod.Colors] = None
        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.color
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
            name, number, address, free1, free2, free3, free4, free5, free6, color
        )

    def to_frames(self) -> List[frame_mod.Frame]:
        text_list: List[str] = _raw_list_to_text_list(
            [
                self.name,
                self.number,
                self.address,
                self.free1,
                self.free2,
                self.free3,
                self.free4,
                self.free5,
                self.free6,
            ]
        )

        frames: List[frame_mod.Frame] = []
        if self.color is not None:
            frames.append(frame_mod.Color.from_color(self.color))
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
    color: Optional[frame_mod.Colors]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.BusinessCardDirectory

    DESCRIPTION: str = "Business Card"

    def __str__(self) -> str:
        return f"Business Card: {repr(self.employer)}, {repr(self.name)}, {repr(self.telephone_number)}, {repr(self.telex_number)}, {repr(self.fax_number)}, {repr(self.position)}, {repr(self.department)}, {repr(self.po_box)}, {repr(self.address)}, {repr(self.memo)} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "BusinessCard":
        text = ""
        color: Optional[frame_mod.Colors] = None
        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.color
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
            frames.append(frame_mod.Color.from_color(self.color))
        frames.extend(frame_mod.Text.from_text_list(text_list))

        return frames


@dataclass
class Memo(Record):
    text: str
    color: Optional[frame_mod.Colors]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.MemoDirectory

    DESCRIPTION: str = "Memo"

    def __str__(self) -> str:
        info_str = f"Memo: {repr(self.text)}"
        if self.color is not None:
            info_str += f" ({self.color.name})"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Memo":
        text = ""
        color: Optional[frame_mod.Colors] = None
        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.color
            elif isinstance(f, frame_mod.Text):
                text += f.text
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        return cls(text, color)

    def to_frames(self) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []

        if self.color is not None:
            frames.append(frame_mod.Color.from_color(self.color))
        frames.extend(frame_mod.Text.from_text_list([self.text]))

        return frames


CalendarDays = Set[int]
CalendarDayColors = Optional[List[frame_mod.Colors]]


@dataclass
class Calendar(Record):
    year: int
    month: int
    days: CalendarDays
    colors: CalendarDayColors

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
        return f"{self.DESCRIPTION}: {self.year}-{self.month}: " + " ".join(info_list)

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Calendar":
        year: int = 0
        month: int = 0
        days: CalendarDays = set()
        colors: Optional[List[frame_mod.Colors]] = None
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
    color: Optional[frame_mod.Colors]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.ScheduleDirectory

    DESCRIPTION: str = "Schedule"

    def __post_init__(self) -> None:
        if self.start_time is None and self.description is None:
            raise ValueError("either start time or description must be set")
        if self.end_time is not None and self.start_time is None:
            raise ValueError("can't set end time without start time")
        if self.alarm_time is not None and self.start_time is None:
            raise ValueError("cant set alarm time without start time")

    def __str__(self) -> str:
        info_str = f"Schedule: {self.date}, {self.start_time}, {self.end_time}, {self.alarm_time}, {self.illustration}, {repr(self.description)}"
        if self.color is not None:
            info_str += f" ({self.color.name})"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Schedule":
        color: Optional[frame_mod.Colors] = None
        date: Optional[datetime.date] = None
        start_time: Optional[datetime.time] = None
        end_time: Optional[datetime.time] = None
        alarm_time: Optional[datetime.time] = None
        illustration: Optional[int] = None
        description: Optional[str] = None

        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.color
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
        frames: List[frame_mod.Frame] = []

        frames.append(frame_mod.Date.from_date(self.date))

        if self.start_time is not None:
            if self.end_time is None:
                frames.append(frame_mod.Time.from_time(self.start_time))
            else:
                frames.append(
                    frame_mod.StartEndTime.from_start_end_times(
                        self.start_time, self.end_time
                    )
                )

        if self.alarm_time is not None:
            frames.append(frame_mod.Alarm.from_time(self.alarm_time))

        if self.illustration is not None:
            frames.append(frame_mod.Illustration.from_number(self.illustration))

        if self.color is not None:
            frames.append(frame_mod.Color.from_color(self.color))

        if self.description is not None:
            frames.extend(frame_mod.Text.from_text(self.description))

        return frames


@dataclass
class Reminder(Record):
    month: Optional[int]
    day: Optional[int]
    alarm_time: Optional[datetime.time]
    description: str
    color: Optional[frame_mod.Colors]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.ReminderDirectory

    DESCRIPTION: str = "Reminder"

    def __post_init__(self) -> None:
        if self.month is not None and self.day is None:
            raise ValueError("cant set month without day")

    def __str__(self) -> str:
        info_str = "Reminder: "
        if self.month:
            info_str += str(self.month) + "-"
        else:
            info_str += "---"
        if self.day:
            info_str += str(self.day) + " "
        else:
            info_str += "-- "
        if self.alarm_time:
            info_str += f"{self.alarm_time}"
        else:
            info_str += "--:--"
        info_str += f" {repr(self.description)}"
        if self.color is not None:
            info_str += f" ({self.color.name})"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Reminder":
        color: Optional[frame_mod.Colors] = None
        month: Optional[int] = None
        day: Optional[int] = None
        alarm_time: Optional[datetime.time] = None
        description: str = ""

        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.color
            elif isinstance(f, frame_mod.Date):
                if f.year is not None:
                    raise ValueError("cant set reminder for a single year")
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

        return cls(month, day, alarm_time, description, color)

    def to_frames(self) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []

        frames.append(frame_mod.Date.from_values(None, self.month, self.day))

        if self.alarm_time is not None:
            frames.append(frame_mod.Alarm.from_time(self.alarm_time))

        if self.description is not None:
            frames.extend(frame_mod.Text.from_text(self.description))

        if self.color is not None:
            frames.append(frame_mod.Color.from_color(self.color))

        return frames


@dataclass
class ToDo(Record):
    deadline_date: Optional[datetime.date]
    deadline_time: Optional[datetime.time]
    alarm: Optional[datetime.time]
    checked_date: Optional[datetime.date]
    checked_time: Optional[datetime.time]
    description: str
    priority: Optional[frame_mod.Priorities]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.ToDoDirectory

    DESCRIPTION: str = "To Do"

    def __post_init__(self) -> None:
        if self.deadline_time is not None and self.deadline_date is None:
            raise ValueError("Missing deadline_date")
        if self.alarm is not None and self.deadline_date is None:
            raise ValueError("Missing deadline_date")
        if self.checked_time is not None:
            if self.checked_date is None:
                raise ValueError("Missing checked_date")
            if self.deadline_date is None:
                raise ValueError("Missing deadline_date")

    def __str__(self) -> str:
        info_str = "To Do: "
        if self.deadline_date is not None:
            info_str += "Deadline: " + str(self.deadline_date) + " "
        if self.deadline_time is not None:
            info_str += str(self.deadline_time) + " "
        if self.alarm is not None:
            info_str += "Alarm: " + str(self.alarm) + " "
        if self.checked_date is not None:
            info_str += "Checked: " + str(self.checked_date) + " "
        if self.checked_time is not None:
            info_str += str(self.checked_time) + " "
        if self.priority is not None:
            info_str += f"Priority: {self.priority.name} "
        info_str += repr(self.description) + " "
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "ToDo":
        deadline_date: Optional[datetime.date] = None
        deadline_time: Optional[datetime.time] = None
        alarm: Optional[datetime.time] = None
        checked_date: Optional[datetime.date] = None
        checked_time: Optional[datetime.time] = None
        description: str = ""
        priority: Optional[frame_mod.Priorities] = None

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
                priority = f.priority
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        if description == "":
            raise ValueError("Missing description")

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
        frames: List[frame_mod.Frame] = []

        if self.deadline_date is not None:
            frames.append(frame_mod.DeadlineDate.from_date(self.deadline_date))

        if self.deadline_time is not None:
            frames.append(frame_mod.DeadlineTime.from_time(self.deadline_time))

        if self.alarm is not None:
            frames.append(frame_mod.ToDoAlarm.from_time(self.alarm))

        if self.checked_date is not None:
            frames.append(frame_mod.Date.from_date(self.checked_date))

        if self.checked_time is not None:
            frames.append(frame_mod.Time.from_time(self.checked_time))

        if self.priority is not None:
            frames.append(frame_mod.Priority.from_priority(self.priority))

        if self.description is not None:
            frames.extend(frame_mod.Text.from_text(self.description))

        return frames


@dataclass
class Expense(Record):
    date: datetime.date
    amount: float
    payment_type: Optional[str]
    expense_type: Optional[str]
    rcpt: Optional[str]  # Empty for CSF-8950
    bus: Optional[str]  # Empty for CSF-8950
    description: Optional[str]
    color: Optional[frame_mod.Colors]

    DIRECTORY: ClassVar[Type[frame_mod.Directory]] = frame_mod.ExpenseManagerDirectory

    DESCRIPTION: str = "Expense"

    def __post_init__(self) -> None:
        pass

    def __str__(self) -> str:
        info_str = f"Expense: {self.date}, Amount: {self.amount}"
        if self.payment_type is not None:
            info_str += f", Payment Type: {repr(self.payment_type)}"
        if self.expense_type is not None:
            info_str += f", Expense Type: {repr(self.expense_type)}"
        if self.rcpt is not None:
            info_str += f", rcpt: {repr(self.rcpt)}"
        if self.bus is not None:
            info_str += f", bus: {repr(self.bus)}"
        if self.description is not None:
            info_str += f", Description: {repr(self.description)}"
        info_str += f" ({self.color})"
        return info_str

    @classmethod
    def from_frames(cls, frames: List[frame_mod.Frame]) -> "Expense":
        text = ""
        color: Optional[frame_mod.Colors] = None
        for f in frames:
            if isinstance(f, frame_mod.Color):
                color = f.color
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
        year_str, month_str, day_str = date_str.split(" ")
        date = datetime.date(int(year_str), int(month_str), int(day_str))

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
        frames: List[frame_mod.Frame] = []

        if self.color is not None:
            frames.append(frame_mod.Color.from_color(self.color))

        frames.extend(
            frame_mod.Text.from_text_list(
                [
                    "{} {} {}".format(
                        self.date.year,
                        self.date.month,
                        self.date.day,
                    )
                    if self.date
                    else "",
                    str(self.amount),
                    self.payment_type if self.payment_type else "",
                    self.expense_type if self.expense_type else "",
                    self.rcpt if self.rcpt else "",
                    self.bus if self.bus else "",
                    self.description if self.description else "",
                ]
            )
        )

        return frames
