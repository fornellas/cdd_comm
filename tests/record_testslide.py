import datetime
from typing import Any, ClassVar, Dict, List, Optional, Type, get_type_hints

from testslide import TestCase

import cdd_comm.frame as frame_mod
import cdd_comm.record as record_mod


class RecordTestCase(TestCase):
    RECORD_CLASS: ClassVar[Type[record_mod.Record]]

    def run(self, result=None):
        if type(self) is RecordTestCase:
            return
        else:
            super().run(result=result)

    def test_DESCRIPTION(self) -> None:
        self.assertNotEqual(self.RECORD_CLASS.DESCRIPTION, "Record")

    def test_DIRECTORY(self) -> None:
        self.assertTrue(issubclass(self.RECORD_CLASS.DIRECTORY, frame_mod.Directory))

    def get_cases_kwargs(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
        raise NotImplementedError

    def test_from_frames(self) -> None:
        for kwargs in self.get_cases_kwargs():
            with self.subTest(**kwargs):
                record = self.RECORD_CLASS.from_frames(self.get_frames(kwargs))
                for name, value in kwargs.items():
                    self.assertEqual(getattr(record, name), value)

    def test_to_frames(self) -> None:
        for kwargs in self.get_cases_kwargs():
            with self.subTest(**kwargs):
                frames = self.RECORD_CLASS(**kwargs).to_frames()  # type: ignore[call-arg]
                expected_frames = self.get_frames(kwargs)
                self.assertEqual(frames, expected_frames)

    def test__str__(self) -> None:
        for kwargs in self.get_cases_kwargs():
            with self.subTest(**kwargs):
                record_str = str(self.RECORD_CLASS(**kwargs))  # type: ignore[call-arg]
                for name, value in kwargs.items():
                    attr_type = get_type_hints(self.RECORD_CLASS)[name]
                    if attr_type == str or (
                        attr_type == Optional[str] and value is not None
                    ):
                        self.assertTrue(
                            repr(value) in record_str,
                            f"Expected\n{repr(value)}\nin\n{repr(record_str)}",
                        )
                    elif (
                        attr_type == Optional[frame_mod.Colors] and value is not None
                    ) or attr_type == frame_mod.Priorities:
                        self.assertTrue(
                            value.name in record_str,
                            f"Expected\n{value.name}\nin\n{repr(record_str)}",
                        )
                    elif attr_type in [int, datetime.date, datetime.time] or (
                        attr_type
                        in [
                            Optional[datetime.time],
                            Optional[datetime.date],
                            Optional[int],
                        ]
                        and value is not None
                    ):
                        self.assertTrue(
                            str(value) in record_str,
                            f"Expected\n{value}\nin\n{repr(record_str)}",
                        )
                    elif attr_type == record_mod.CalendarDays:
                        for day in value:
                            self.assertTrue(
                                str(day) in record_str,
                                f"Expected\n{day}\nin\n{repr(record_str)}",
                            )
                    elif (
                        attr_type == record_mod.CalendarDayColors and value is not None
                    ):
                        for color in value:
                            self.assertTrue(
                                color.name[0].lower() in record_str,
                                f"Expected\n{color.name[0].lower()}\nin\n{repr(record_str)}",
                            )
                    elif value is None:
                        pass
                    else:
                        raise RuntimeError("Unexpected type: ", attr_type)


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


class TelephoneTest(RecordTestCase):
    RECORD_CLASS = record_mod.Telephone

    def get_cases_kwargs(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "John Doe",
                "number": None,
                "address": None,
                "field1": None,
                "field2": None,
                "field3": None,
                "field4": None,
                "field5": None,
                "field6": None,
                "color": None,
            },
            {
                "name": "John Doe",
                "number": "123-456",
                "address": None,
                "field1": None,
                "field2": None,
                "field3": None,
                "field4": None,
                "field5": None,
                "field6": None,
                "color": None,
            },
            {
                "name": "John Doe",
                "number": None,
                "address": "Nowhere St",
                "field1": None,
                "field2": None,
                "field3": None,
                "field4": None,
                "field5": None,
                "field6": None,
                "color": None,
            },
            {
                "name": "John Doe",
                "number": "123-456",
                "address": None,
                "field1": None,
                "field2": None,
                "field3": None,
                "field4": None,
                "field5": None,
                "field6": None,
                "color": frame_mod.Colors.GREEN,
            },
            {
                "name": "John Doe",
                "number": "123-456",
                "address": "Nowhere St",
                "field1": "Field 1",
                "field2": None,
                "field3": "Field 3",
                "field4": "Field 4",
                "field5": None,
                "field6": "Field 6",
                "color": None,
            },
            {
                "name": "John Doe",
                "number": "123-456",
                "address": "Nowhere St",
                "field1": "Field 1",
                "field2": "Field 2",
                "field3": "Field 3",
                "field4": "Field 4",
                "field5": "Field 5",
                "field6": "Field 6",
                "color": frame_mod.Colors.GREEN,
            },
        ]

    def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
        text_list = _raw_list_to_text_list(
            [
                kwargs["name"],
                kwargs["number"],
                kwargs["address"],
                kwargs["field1"],
                kwargs["field2"],
                kwargs["field3"],
                kwargs["field4"],
                kwargs["field5"],
                kwargs["field6"],
            ]
        )

        frames: List[frame_mod.Frame] = []
        if kwargs["color"] is not None:
            frames.append(frame_mod.Color.from_color(kwargs["color"]))

        frames.extend(frame_mod.Text.from_text_list(text_list))

        return frames


class BusinessCardTest(RecordTestCase):
    RECORD_CLASS = record_mod.BusinessCard

    def get_cases_kwargs(self) -> List[Dict[str, Any]]:
        return [
            {
                "employer": "Acme Inc",
                "name": "John Doe",
                "telephone_number": None,
                "telex_number": None,
                "fax_number": None,
                "position": None,
                "department": None,
                "po_box": None,
                "address": None,
                "memo": None,
                "color": None,
            },
            {
                "employer": "Acme Inc",
                "name": "John Doe",
                "telephone_number": "123-456",
                "telex_number": None,
                "fax_number": None,
                "position": None,
                "department": None,
                "po_box": None,
                "address": None,
                "memo": None,
                "color": None,
            },
            {
                "employer": "Acme Inc",
                "name": "John Doe",
                "telephone_number": "123-456",
                "telex_number": "456-789",
                "fax_number": None,
                "position": None,
                "department": "Engineering",
                "po_box": None,
                "address": "Nowhere St",
                "memo": "NIce guy",
                "color": frame_mod.Colors.GREEN,
            },
            {
                "employer": "Acme Inc",
                "name": "John Doe",
                "telephone_number": "123-456",
                "telex_number": "456-789",
                "fax_number": "789-123",
                "position": "Engineer",
                "department": "Engineering",
                "po_box": "12345",
                "address": "Nowhere St",
                "memo": "NIce guy",
                "color": frame_mod.Colors.GREEN,
            },
        ]

    def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
        text_list = _raw_list_to_text_list(
            [
                kwargs["employer"],
                kwargs["name"],
                kwargs["telephone_number"],
                kwargs["telex_number"],
                kwargs["fax_number"],
                kwargs["position"],
                kwargs["department"],
                kwargs["po_box"],
                kwargs["address"],
                kwargs["memo"],
            ]
        )

        frames: List[frame_mod.Frame] = []
        if kwargs["color"] is not None:
            frames.append(frame_mod.Color.from_color(kwargs["color"]))

        frames.extend(frame_mod.Text.from_text_list(text_list))

        return frames


class MemoTest(RecordTestCase):
    RECORD_CLASS = record_mod.Memo

    def get_cases_kwargs(self) -> List[Dict[str, Any]]:
        return [
            {
                "text": "Hello\nWorld",
                "color": frame_mod.Colors.ORANGE,
            },
        ]

    def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []
        if kwargs["color"] is not None:
            frames.append(frame_mod.Color.from_color(kwargs["color"]))
        frames.extend(frame_mod.Text.from_text_list([kwargs["text"]]))
        return frames


class CalendarTest(RecordTestCase):
    RECORD_CLASS = record_mod.Calendar

    def get_cases_kwargs(self) -> List[Dict[str, Any]]:
        return [
            {
                "year": 2021,
                "month": 12,
                "days": {1, 10, 19, 28},
                "colors": None,
            },
            {
                "year": 2021,
                "month": 12,
                "days": {1, 10, 19, 28},
                "colors": (
                    [frame_mod.Colors.BLUE] * 10
                    + [frame_mod.Colors.GREEN] * 10
                    + [frame_mod.Colors.ORANGE] * 11
                ),
            },
        ]

    def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []
        frames.append(
            frame_mod.Date.from_date(datetime.date(kwargs["year"], kwargs["month"], 1))
        )
        frames.append(frame_mod.DayHighlight.from_days(kwargs["days"]))
        if kwargs["colors"] is not None:
            frames.append(
                frame_mod.DayColorHighlight.from_days_and_colors(
                    kwargs["days"],
                    kwargs["colors"],
                )
            )
        return frames


class ScheduleTest(RecordTestCase):
    RECORD_CLASS = record_mod.Schedule

    def get_cases_kwargs(self) -> List[Dict[str, Any]]:
        return [
            {
                "date": datetime.date(2020, 11, 1),
                "start_time": None,
                "end_time": None,
                "alarm_time": None,
                "illustration": None,
                "description": "do something",
                "color": None,
            },
            {
                "date": datetime.date(2020, 11, 1),
                "start_time": datetime.time(23, 3),
                "end_time": None,
                "alarm_time": None,
                "illustration": None,
                "description": None,
                "color": None,
            },
            {
                "date": datetime.date(2020, 11, 1),
                "start_time": datetime.time(22, 3),
                "end_time": datetime.time(23, 4),
                "alarm_time": None,
                "illustration": None,
                "description": None,
                "color": None,
            },
            {
                "date": datetime.date(2020, 11, 1),
                "start_time": datetime.time(22, 3),
                "end_time": datetime.time(23, 4),
                "alarm_time": datetime.time(21, 0),
                "illustration": None,
                "description": None,
                "color": None,
            },
            {
                "date": datetime.date(2020, 11, 1),
                "start_time": datetime.time(22, 3),
                "end_time": datetime.time(23, 4),
                "alarm_time": datetime.time(21, 0),
                "illustration": 3,
                "description": "Do something",
                "color": frame_mod.Colors.ORANGE,
            },
        ]

    def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []

        frames.append(frame_mod.Date.from_date(kwargs["date"]))

        if kwargs["start_time"] is not None:
            if kwargs["end_time"] is None:
                frames.append(frame_mod.Time.from_time(kwargs["start_time"]))
            else:
                frames.append(
                    frame_mod.StartEndTime.from_start_end_times(
                        kwargs["start_time"], kwargs["end_time"]
                    )
                )

        if kwargs["alarm_time"] is not None:
            frames.append(frame_mod.Alarm.from_time(kwargs["alarm_time"]))

        if kwargs["illustration"] is not None:
            frames.append(frame_mod.Illustration.from_number(kwargs["illustration"]))

        if kwargs["color"] is not None:
            frames.append(frame_mod.Color.from_color(kwargs["color"]))

        if kwargs["description"] is not None:
            frames.extend(frame_mod.Text.from_text(kwargs["description"]))

        return frames


class ReminderTest(RecordTestCase):
    RECORD_CLASS = record_mod.Reminder

    def get_cases_kwargs(self) -> List[Dict[str, Any]]:
        return [
            {
                "month": None,
                "day": None,
                "alarm_time": None,
                "description": "Do something",
                "color": None,
            },
            {
                "month": None,
                "day": None,
                "alarm_time": datetime.time(15, 33),
                "description": "Do something",
                "color": frame_mod.Colors.ORANGE,
            },
            {
                "month": None,
                "day": 30,
                "alarm_time": None,
                "description": "Do something",
                "color": frame_mod.Colors.ORANGE,
            },
            {
                "month": None,
                "day": 30,
                "alarm_time": datetime.time(15, 33),
                "description": "Do something",
                "color": frame_mod.Colors.ORANGE,
            },
            {
                "month": 12,
                "day": 30,
                "alarm_time": datetime.time(15, 33),
                "description": "Do something",
                "color": None,
            },
            {
                "month": 12,
                "day": 30,
                "alarm_time": datetime.time(15, 33),
                "description": "Do something",
                "color": frame_mod.Colors.ORANGE,
            },
        ]

    def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []

        frames.append(frame_mod.Date.from_values(None, kwargs["month"], kwargs["day"]))

        if kwargs["alarm_time"] is not None:
            frames.append(frame_mod.Alarm.from_time(kwargs["alarm_time"]))

        if kwargs["description"] is not None:
            frames.extend(frame_mod.Text.from_text(kwargs["description"]))

        if kwargs["color"] is not None:
            frames.append(frame_mod.Color.from_color(kwargs["color"]))

        return frames


class ToDoTest(RecordTestCase):
    RECORD_CLASS = record_mod.ToDo

    def get_cases_kwargs(self) -> List[Dict[str, Any]]:
        return [
            {
                "deadline_date": None,
                "deadline_time": None,
                "alarm": None,
                "checked_date": None,
                "checked_time": None,
                "description": "Do something",
                "priority": frame_mod.Priorities.B,
            },
            {
                "deadline_date": datetime.date(2021, 2, 25),
                "deadline_time": None,
                "alarm": None,
                "checked_date": None,
                "checked_time": None,
                "description": "Do something",
                "priority": frame_mod.Priorities.B,
            },
            {
                "deadline_date": datetime.date(2021, 2, 25),
                "deadline_time": datetime.time(22, 11),
                "alarm": None,
                "checked_date": None,
                "checked_time": None,
                "description": "Do something",
                "priority": frame_mod.Priorities.B,
            },
            {
                "deadline_date": datetime.date(2021, 2, 25),
                "deadline_time": None,
                "alarm": datetime.time(21, 11),
                "checked_date": None,
                "checked_time": None,
                "description": "Do something",
                "priority": frame_mod.Priorities.B,
            },
            {
                "deadline_date": datetime.date(2021, 2, 25),
                "deadline_time": datetime.time(22, 11),
                "alarm": datetime.time(21, 11),
                "checked_date": None,
                "checked_time": None,
                "description": "Do something",
                "priority": frame_mod.Priorities.B,
            },
            {
                "deadline_date": datetime.date(2021, 2, 25),
                "deadline_time": datetime.time(22, 11),
                "alarm": datetime.time(21, 11),
                "checked_date": datetime.date(2021, 2, 24),
                "checked_time": datetime.time(23, 21),
                "description": "Do something",
                "priority": frame_mod.Priorities.B,
            },
        ]

    def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []

        if kwargs["deadline_date"] is not None:
            frames.append(frame_mod.DeadlineDate.from_date(kwargs["deadline_date"]))

        if kwargs["deadline_time"] is not None:
            frames.append(frame_mod.DeadlineTime.from_time(kwargs["deadline_time"]))

        if kwargs["alarm"] is not None:
            frames.append(frame_mod.ToDoAlarm.from_time(kwargs["alarm"]))

        if kwargs["checked_date"] is not None:
            frames.append(frame_mod.Date.from_date(kwargs["checked_date"]))

        if kwargs["checked_time"] is not None:
            frames.append(frame_mod.Time.from_time(kwargs["checked_time"]))

        if kwargs["priority"] is not None:
            frames.append(frame_mod.Priority.from_priority(kwargs["priority"]))

        if kwargs["description"] is not None:
            frames.extend(frame_mod.Text.from_text(kwargs["description"]))

        return frames


# class ExpenseTest(RecordTestCase):
#     RECORD_CLASS = record_mod.Expense
#
#     def get_cases_kwargs(self) -> List[Dict[str, Any]]:
#         return [
#             {
#             },
#         ]
#
#     def get_frames(self, kwargs: Dict[str, Any]) -> List[frame_mod.Frame]:
#         raise NotImplementedError
