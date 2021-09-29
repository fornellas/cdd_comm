import datetime
from typing import Type, cast

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
    LENGTH: int = frame_mod.Date.LENGTH
    TYPE: int = frame_mod.Date.TYPE
    ADDRESS: int = frame_mod.Date.ADDRESS

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
    LENGTH: int = frame_mod.DeadlineDate.LENGTH
    TYPE: int = frame_mod.DeadlineDate.TYPE
    ADDRESS: int = frame_mod.DeadlineDate.ADDRESS


class DeadlineTimeTest(TestCase):
    def test_time(self):
        self.assertEqual(
            frame_mod.Frame.from_data(
                length=frame_mod.DeadlineTime.LENGTH,
                frame_type=frame_mod.DeadlineTime.TYPE,
                address=frame_mod.DeadlineTime.ADDRESS,
                data=[ord(c) for c in "22:33"],
                checksum=0,
            ).time,
            datetime.time(22, 33),
        )

    def test_match(self) -> None:
        frame = frame_mod.Frame.from_data(
            length=frame_mod.DeadlineTime.LENGTH,
            frame_type=frame_mod.DeadlineTime.TYPE,
            address=frame_mod.DeadlineTime.ADDRESS,
            data=[ord(c) for c in "22:33"],
            checksum=0,
        )
        self.assertTrue(isinstance(frame, frame_mod.DeadlineTime))


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
