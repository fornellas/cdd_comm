import datetime
from typing import ClassVar, List, Type, cast

from testslide import TestCase

import cdd_comm.frame as frame_mod


class FrameTest(TestCase):
    def test_get_kebab_case_description(self) -> None:
        self.assertEqual(
            frame_mod.Frame(
                length=0, type=1, address=2, data=[], checksum=0
            ).get_kebab_case_description(),
            "frame",
        )

    def test_eq(self) -> None:
        self.assertTrue(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=1, type=1, address=2, data=[0], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=0, type=11, address=2, data=[], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=0, type=1, address=22, data=[], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=2, type=1, address=2, data=[0, 1], checksum=0)
            == frame_mod.Frame(length=2, type=1, address=2, data=[0, 2], checksum=0)
        )
        self.assertFalse(
            frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=0)
            == frame_mod.Frame(length=0, type=1, address=2, data=[], checksum=1)
        )

    def test_calculate_checksum(self) -> None:
        self.assertEqual(
            frame_mod.Frame.calculate_checksum(
                length=3, frame_type=244, address=134, data=[0, 1, 2]
            ),
            128,
        )
        self.assertEqual(
            frame_mod.Frame.calculate_checksum(
                length=2, frame_type=3, address=134, data=[0, 1]
            ),
            116,
        )

    def test_is_checksum_valid(self) -> None:
        self.assertTrue(
            frame_mod.Frame(
                length=3, type=244, address=134, data=[0, 1, 2], checksum=128
            ).is_checksum_valid()
        )
        self.assertFalse(
            frame_mod.Frame(
                length=3, type=244, address=134, data=[0, 1, 2], checksum=127
            ).is_checksum_valid()
        )

    def test_bytes(self) -> None:
        self.assertEqual(
            frame_mod.Frame(
                length=3, type=244, address=134, data=[0, 1, 2], checksum=128
            ).bytes(),
            b":03F4860000010280",
        )
        self.assertEqual(
            frame_mod.Frame(
                length=3, type=234, address=55, data=[0, 1, 2], checksum=34
            ).bytes(),
            b":03EA370000010222",
        )

    def test_match(self) -> None:
        frame = frame_mod.Frame(
            length=3, type=234, address=55, data=[0, 1, 2], checksum=34
        )
        self.assertFalse(
            frame.match(length=3, frame_type=234, address=55, data=[0, 1, 2])
        )
        self.assertFalse(
            frame.match(length=3, frame_type=232, address=55, data=[0, 1, 2])
        )


class DirectoryTest(TestCase):
    def test_directory(self) -> None:
        self.assertTrue(
            type(
                frame_mod.Frame.from_data(
                    length=frame_mod.Directory.LENGTH,
                    frame_type=frame_mod.Directory.TYPE,
                    address=frame_mod.Directory.ADDRESS,
                    data=[0, 0],
                    checksum=0,
                )
            )
            == frame_mod.Directory
        )

    def assert_match(self, directory_class: Type[frame_mod.Directory]) -> None:
        self.assertTrue(
            type(
                frame_mod.Frame.from_data(
                    length=frame_mod.Directory.LENGTH,
                    frame_type=frame_mod.Directory.TYPE,
                    address=frame_mod.Directory.ADDRESS,
                    data=directory_class.DATA,
                    checksum=0,
                )
            )
            == directory_class
        )

    def test_TelephoneDirectory_match(self) -> None:
        self.assert_match(frame_mod.TelephoneDirectory)

    def test_BusinessCardDirectory_match(self) -> None:
        self.assert_match(frame_mod.BusinessCardDirectory)

    def test_MemoDirectory_match(self) -> None:
        self.assert_match(frame_mod.MemoDirectory)

    def test_CalendarDirectory_match(self) -> None:
        self.assert_match(frame_mod.CalendarDirectory)

    def test_ScheduleKeeperDirectory_match(self) -> None:
        self.assert_match(frame_mod.ScheduleKeeperDirectory)

    def test_ReminderDirectory_match(self) -> None:
        self.assert_match(frame_mod.ReminderDirectory)

    def test_ToDoDirectory_match(self) -> None:
        self.assert_match(frame_mod.ToDoDirectory)

    def test_ExpenseManagerDirectory_match(self) -> None:
        self.assert_match(frame_mod.ExpenseManagerDirectory)


class ColorTest(TestCase):
    def test_from_color_enum(self) -> None:
        for color_enum in list(frame_mod.ColorEnum):
            frame = frame_mod.Color.from_color_enum(color_enum)
            self.assertEqual(frame.enum, color_enum)
            self.assertEqual(frame.name, color_enum.name)

    def test_match(self) -> None:
        for color_enum in list(frame_mod.ColorEnum):
            frame = frame_mod.Frame.from_data(
                length=frame_mod.Color.LENGTH,
                frame_type=frame_mod.Color.TYPE,
                address=frame_mod.Color.ADDRESS,
                data=[color_enum.value],
                checksum=0,
            )
            self.assertTrue(isinstance(frame, frame_mod.Color))


class DateTest(TestCase):
    LENGTH: ClassVar[int] = frame_mod.Date.LENGTH
    TYPE: ClassVar[int] = frame_mod.Date.TYPE
    ADDRESS: ClassVar[int] = frame_mod.Date.ADDRESS

    def _get_date(self, date_str: str) -> frame_mod.Date:
        return cast(
            frame_mod.Date,
            frame_mod.Frame.from_data(
                length=self.LENGTH,
                frame_type=self.TYPE,
                address=self.ADDRESS,
                data=[ord(c) for c in date_str],
                checksum=0,
            ),
        )

    def test_year(self) -> None:
        self.assertEqual(
            self._get_date("----------").year,
            None,
        )
        self.assertEqual(
            self._get_date("2021------").year,
            2021,
        )

    def test_month(self) -> None:
        self.assertEqual(
            self._get_date("2021------").month,
            None,
        )
        self.assertEqual(
            self._get_date("2021-03---").month,
            3,
        )

    def test_day(self) -> None:
        self.assertEqual(
            self._get_date("2021-03---").day,
            None,
        )
        self.assertEqual(
            self._get_date("2021-03-29").day,
            29,
        )

    def test_date(self) -> None:
        frame = self._get_date("----------")
        with self.assertRaises(RuntimeError):
            frame.date

        frame = self._get_date("2021------")
        with self.assertRaises(RuntimeError):
            frame.date

        frame = self._get_date("2021-03---")
        with self.assertRaises(RuntimeError):
            frame.date

        frame = self._get_date("2021-03-29")
        self.assertEqual(frame.date, datetime.date(2021, 3, 29))

    def test_match(self) -> None:
        frame = self._get_date("----------")
        self.assertTrue(isinstance(frame, frame_mod.Date))


class DeadlineDateTest(DateTest):
    LENGTH: ClassVar[int] = frame_mod.DeadlineDate.LENGTH
    TYPE: ClassVar[int] = frame_mod.DeadlineDate.TYPE
    ADDRESS: ClassVar[int] = frame_mod.DeadlineDate.ADDRESS


class Time(TestCase):
    TIME_CLASS: ClassVar[Type[frame_mod.Time]] = frame_mod.Time
    TYPE: ClassVar[int] = frame_mod.Time.TYPE

    def test_time(self) -> None:
        self.assertEqual(
            cast(
                frame_mod.Time,
                frame_mod.Frame.from_data(
                    length=frame_mod.Time.LENGTH,
                    frame_type=self.TYPE,
                    address=frame_mod.Time.ADDRESS,
                    data=[ord(c) for c in "22:33"],
                    checksum=0,
                ),
            ).time,
            datetime.time(22, 33),
        )

    def test_match(self) -> None:
        frame = frame_mod.Frame.from_data(
            length=frame_mod.Time.LENGTH,
            frame_type=self.TYPE,
            address=frame_mod.Time.ADDRESS,
            data=[ord(c) for c in "22:33"],
            checksum=0,
        )
        self.assertTrue(isinstance(frame, self.TIME_CLASS))


class DeadlineTimeTest(Time):
    TIME_CLASS: ClassVar[Type[frame_mod.Time]] = frame_mod.DeadlineTime
    TYPE: ClassVar[int] = frame_mod.DeadlineTime.TYPE


class ToDoAlarmTest(Time):
    TIME_CLASS: ClassVar[Type[frame_mod.Time]] = frame_mod.ToDoAlarm
    TYPE: ClassVar[int] = frame_mod.ToDoAlarm.TYPE


class AlarmTest(Time):
    TIME_CLASS: ClassVar[Type[frame_mod.Time]] = frame_mod.Alarm
    TYPE: ClassVar[int] = frame_mod.Alarm.TYPE


class PriorityTest(TestCase):
    def _get_priority(
        self, priority_enum: frame_mod.PriorityEnum
    ) -> frame_mod.Priority:
        return cast(
            frame_mod.Priority,
            frame_mod.Frame.from_data(
                length=frame_mod.Priority.LENGTH,
                frame_type=frame_mod.Priority.TYPE,
                address=frame_mod.Priority.ADDRESS,
                data=[priority_enum.value],
                checksum=0,
            ),
        )

    def test_color(self) -> None:
        self.assertEqual(
            frame_mod.ColorEnum.ORANGE,
            self._get_priority(frame_mod.PriorityEnum.A).color,
        )
        self.assertEqual(
            frame_mod.ColorEnum.BLUE,
            self._get_priority(frame_mod.PriorityEnum.B).color,
        )
        self.assertEqual(
            frame_mod.ColorEnum.GREEN,
            self._get_priority(frame_mod.PriorityEnum.C).color,
        )

    def test_enum(self) -> None:
        for priority_enum in list(frame_mod.PriorityEnum):
            self.assertEqual(self._get_priority(priority_enum).enum, priority_enum)

    def test_from_priority_enum(self) -> None:
        for priority_enum in list(frame_mod.PriorityEnum):
            self.assertEqual(
                frame_mod.Priority.from_priority_enum(priority_enum).enum,
                priority_enum,
            )

    def test_match(self) -> None:
        self.assertTrue(
            isinstance(self._get_priority(frame_mod.PriorityEnum.A), frame_mod.Priority)
        )


class DayHighlightTest(TestCase):
    def setUp(self) -> None:
        self.frame = cast(
            frame_mod.DayHighlight,
            frame_mod.Frame.from_data(
                length=frame_mod.DayHighlight.LENGTH,
                frame_type=frame_mod.DayHighlight.TYPE,
                address=frame_mod.DayHighlight.ADDRESS,
                data=[2, 1, 0, 3],
                checksum=0,
            ),
        )

    def test_days(self) -> None:
        self.assertEqual(self.frame.days, {17, 26, 2, 1})

    def test_match(self) -> None:
        self.assertTrue(isinstance(self.frame, frame_mod.DayHighlight))


class DayColorHighlightTest(TestCase):
    def setUp(self) -> None:
        data: List[int] = []
        for idx in range(0, frame_mod.DayColorHighlight.LENGTH):
            color = frame_mod.ColorEnum.BLUE.value
            if ((idx + 1) % 3) == 0:
                color = frame_mod.ColorEnum.ORANGE.value
            if ((idx + 2) % 3) == 0:
                color = frame_mod.ColorEnum.GREEN.value
            highlight = 0
            if idx % 2:
                highlight = 0x80
            data.append(color | highlight)
        self.frame = cast(
            frame_mod.DayColorHighlight,
            frame_mod.Frame.from_data(
                length=frame_mod.DayColorHighlight.LENGTH,
                frame_type=frame_mod.DayColorHighlight.TYPE,
                address=frame_mod.DayColorHighlight.ADDRESS,
                data=data,
                checksum=0,
            ),
        )

    def test_days(self) -> None:
        self.assertEqual(
            self.frame.days, {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31}
        )

    def test_colors(self) -> None:
        self.assertEqual(
            self.frame.colors,
            [
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
                frame_mod.ColorEnum.BLUE,
                frame_mod.ColorEnum.ORANGE,
                frame_mod.ColorEnum.GREEN,
            ],
        )

    def test_match(self) -> None:
        self.assertTrue(isinstance(self.frame, frame_mod.DayColorHighlight))


class StartEndTimeTest(TestCase):
    def setUp(self) -> None:
        self.frame = cast(
            frame_mod.StartEndTime,
            frame_mod.Frame.from_data(
                length=frame_mod.StartEndTime.LENGTH,
                frame_type=frame_mod.StartEndTime.TYPE,
                address=frame_mod.StartEndTime.ADDRESS,
                data=[ord(c) for c in "22:33~23:21"],
                checksum=0,
            ),
        )

    def test_start_time(self) -> None:
        self.assertEqual(self.frame.start_time, datetime.time(22, 33))

    def test_end_time(self) -> None:
        self.assertEqual(self.frame.end_time, datetime.time(23, 21))

    def test_match(self) -> None:
        self.assertTrue(isinstance(self.frame, frame_mod.StartEndTime))


class IllustrationTest(TestCase):
    def setUp(self) -> None:
        self.frame = cast(
            frame_mod.Illustration,
            frame_mod.Frame.from_data(
                length=frame_mod.Illustration.LENGTH,
                frame_type=frame_mod.Illustration.TYPE,
                address=frame_mod.Illustration.ADDRESS,
                data=[0x8],
                checksum=0,
            ),
        )

    def test_end_time(self) -> None:
        self.assertEqual(self.frame.number, 0x8)

    def test_match(self) -> None:
        self.assertTrue(isinstance(self.frame, frame_mod.Illustration))


class TextTest(TestCase):
    def _assert_frame(
        self,
        frame: frame_mod.Text,
        length: int,
        frame_type: int,
        address: int,
        data: List[int],
        text: str,
    ) -> None:
        self.assertEqual(frame.length, length)
        self.assertEqual(frame.type, frame_type)
        self.assertEqual(frame.address, address)
        self.assertEqual(frame.data, data)
        self.assertEqual(frame.text, text)

    def test_from_text_list_one_frame(self) -> None:
        text = "Hello"
        frames = frame_mod.Text.from_text_list([text])
        self.assertEqual(len(frames), 1)
        frame0 = frames[0]
        self._assert_frame(
            frame=frame0,
            length=5,
            frame_type=0x80,
            address=0,
            data=[ord(c) for c in text],
            text=text,
        )

    def test_from_text_list_one_frame_multi_line(self) -> None:
        text = "Hello\nWorld"
        frames = frame_mod.Text.from_text_list([text])
        self.assertEqual(len(frames), 2)
        self._assert_frame(
            frame=frames[0],
            length=6,
            frame_type=0x80,
            address=0,
            data=[ord(c) for c in "Hello"] + [13],
            text="Hello\n",
        )
        self._assert_frame(
            frame=frames[1],
            length=5,
            frame_type=0x80,
            address=6,
            data=[ord(c) for c in "World"],
            text="World",
        )

    def test_from_text_list_two_frames(self) -> None:
        first_frame_text = "0123456789" * 12 + "01234567"
        second_frame_text = "second"
        text = first_frame_text + second_frame_text
        frames = frame_mod.Text.from_text_list([text])
        self.assertEqual(len(frames), 2)
        self._assert_frame(
            frame=frames[0],
            length=0x80,
            frame_type=0x80,
            address=0,
            data=[ord(c) for c in first_frame_text],
            text=first_frame_text,
        )
        self._assert_frame(
            frame=frames[1],
            length=len(second_frame_text),
            frame_type=0x80,
            address=0x80,
            data=[ord(c) for c in second_frame_text],
            text=second_frame_text,
        )

    def test_from_text_list_three_frames(self) -> None:
        first_frame_text = "0123456789" * 12 + "01234567"
        second_frame_text = "1234567890" * 12 + "12345678"
        third_frame_text = "third"
        text = first_frame_text + second_frame_text + third_frame_text
        frames = frame_mod.Text.from_text_list([text])
        self.assertEqual(len(frames), 3)
        self._assert_frame(
            frame=frames[0],
            length=0x80,
            frame_type=0x80,
            address=0,
            data=[ord(c) for c in first_frame_text],
            text=first_frame_text,
        )
        self._assert_frame(
            frame=frames[1],
            length=len(second_frame_text),
            frame_type=0x80,
            address=0x80,
            data=[ord(c) for c in second_frame_text],
            text=second_frame_text,
        )
        self._assert_frame(
            frame=frames[2],
            length=len(third_frame_text),
            frame_type=0x81,
            address=0,
            data=[ord(c) for c in third_frame_text],
            text=third_frame_text,
        )

    def test_match(self) -> None:
        frame = frame_mod.Frame.from_data(
            length=3,
            frame_type=0x80,
            address=0,
            data=[ord(c) for c in "abc"],
            checksum=0,
        )
        self.assertTrue(isinstance(frame, frame_mod.Text))
        frame = frame_mod.Frame.from_data(
            length=3,
            frame_type=0x80,
            address=0,
            data=[ord(c) for c in "abc"],
            checksum=0,
        )
        self.assertTrue(isinstance(frame, frame_mod.Text))


class EndOfRecordTest(TestCase):
    def test_get(self) -> None:
        frame = frame_mod.EndOfRecord.get()
        self.assertEqual(frame.length, frame_mod.EndOfRecord.LENGTH)
        self.assertEqual(frame.type, frame_mod.EndOfRecord.TYPE)
        self.assertEqual(frame.address, frame_mod.EndOfRecord.ADDRESS)
        self.assertEqual(frame.data, [])

    def assert_match(self, directory_class: Type[frame_mod.Directory]) -> None:
        self.assertTrue(
            type(
                frame_mod.Frame.from_data(
                    length=frame_mod.EndOfRecord.LENGTH,
                    frame_type=frame_mod.EndOfRecord.TYPE,
                    address=frame_mod.EndOfRecord.ADDRESS,
                    data=[],
                    checksum=0,
                )
            )
            == frame_mod.EndOfRecord
        )


class EndOfTransmissionTest(TestCase):
    def test_get(self) -> None:
        frame = frame_mod.EndOfTransmission.get()
        self.assertEqual(frame.length, frame_mod.EndOfTransmission.LENGTH)
        self.assertEqual(frame.type, frame_mod.EndOfTransmission.TYPE)
        self.assertEqual(frame.address, frame_mod.EndOfTransmission.ADDRESS)
        self.assertEqual(frame.data, [])

    def assert_match(self, directory_class: Type[frame_mod.Directory]) -> None:
        self.assertTrue(
            type(
                frame_mod.Frame.from_data(
                    length=frame_mod.EndOfTransmission.LENGTH,
                    frame_type=frame_mod.EndOfTransmission.TYPE,
                    address=frame_mod.EndOfTransmission.ADDRESS,
                    data=[],
                    checksum=0,
                )
            )
            == frame_mod.EndOfTransmission
        )


class FrameBuilderTest(TestCase):
    def test_add_data(self) -> None:
        length = 2
        frame_type = 0x80
        address_low = 4
        address_high = 5
        address = (address_high << 8) | address_low
        data = [ord("0"), ord("1")]
        checksum = 45
        frame_builder = frame_mod.FrameBuilder()
        self.assertEqual(frame_builder.add_data(length), ("Length", None))
        self.assertEqual(frame_builder.add_data(frame_type), ("Type", None))
        self.assertEqual(frame_builder.add_data(address_low), ("Address Low", None))
        self.assertEqual(frame_builder.add_data(address_high), ("Address High", None))
        self.assertEqual(frame_builder.add_data(data[0]), ("Data", None))
        self.assertEqual(frame_builder.add_data(data[1]), ("Data", None))
        desc, frame = frame_builder.add_data(checksum)
        self.assertEqual(desc, "Checksum")
        assert frame
        self.assertTrue(isinstance(frame, frame_mod.Text))
        self.assertEqual(frame.length, length)
        self.assertEqual(frame.type, frame_type)
        self.assertEqual(frame.address, address)
        self.assertEqual(frame.data, data)
        self.assertEqual(frame.checksum, checksum)
