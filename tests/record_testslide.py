import datetime
from typing import List, Optional, Set

from testslide import TestCase

import cdd_comm.frame as frame_mod
import cdd_comm.record as record_mod


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


class TelephoneTest(TestCase):
    NAME: str = "John Doe"
    NUMBER: str = "123-456"
    ADDRESS: str = "Nowhere St"
    FIELD1: str = "Field 1"
    FIELD2: str = "Field 2"
    FIELD3: str = "Field 3"
    FIELD4: str = "Field 4"
    FIELD5: str = "Field 5"
    FIELD6: str = "Field 6"
    COLOR: frame_mod.ColorEnum = frame_mod.ColorEnum.GREEN

    def _get_frames(
        self,
        name: str,
        number: Optional[str] = None,
        address: Optional[str] = None,
        field1: Optional[str] = None,
        field2: Optional[str] = None,
        field3: Optional[str] = None,
        field4: Optional[str] = None,
        field5: Optional[str] = None,
        field6: Optional[str] = None,
        color: Optional[frame_mod.ColorEnum] = None,
    ) -> List[frame_mod.Frame]:
        text_list = _raw_list_to_text_list(
            [
                name,
                number,
                address,
                field1,
                field2,
                field3,
                field4,
                field5,
                field6,
            ]
        )

        frames: List[frame_mod.Frame] = []
        if color is not None:
            frames.append(frame_mod.Color.from_color_enum(color))

        frames.extend(frame_mod.Text.from_text_list(text_list))

        return frames

    def _assert_telephone(
        self,
        name: str,
        number: Optional[str] = None,
        address: Optional[str] = None,
        field1: Optional[str] = None,
        field2: Optional[str] = None,
        field3: Optional[str] = None,
        field4: Optional[str] = None,
        field5: Optional[str] = None,
        field6: Optional[str] = None,
        color: Optional[frame_mod.ColorEnum] = None,
    ) -> None:
        frames = self._get_frames(
            name,
            number,
            address,
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            color,
        )

        telephone = record_mod.Telephone.from_frames(frames)
        self.assertEqual(telephone.color, color)
        self.assertEqual(telephone.name, name)
        self.assertEqual(telephone.address, address)
        self.assertEqual(telephone.field1, field1)
        self.assertEqual(telephone.field2, field2)
        self.assertEqual(telephone.field3, field3)
        self.assertEqual(telephone.field4, field4)
        self.assertEqual(telephone.field5, field5)
        self.assertEqual(telephone.field6, field6)

    def test_from_frames(self) -> None:
        self._assert_telephone(
            name=self.NAME,
        )
        self._assert_telephone(
            name=self.NAME,
            number=self.NUMBER,
        )
        self._assert_telephone(
            name=self.NAME,
            address=self.ADDRESS,
        )
        self._assert_telephone(
            name=self.NAME,
            number=self.NUMBER,
            color=self.COLOR,
        )
        self._assert_telephone(
            name=self.NAME,
            number=self.NUMBER,
            address=self.ADDRESS,
            field1=self.FIELD1,
            field3=self.FIELD3,
            field4=self.FIELD4,
            field6=self.FIELD6,
        )
        self._assert_telephone(
            name=self.NAME,
            number=self.NUMBER,
            address=self.ADDRESS,
            field1=self.FIELD1,
            field2=self.FIELD2,
            field3=self.FIELD3,
            field4=self.FIELD4,
            field5=self.FIELD5,
            field6=self.FIELD6,
            color=self.COLOR,
        )

    def _assert_frames(
        self,
        name: str,
        number: Optional[str] = None,
        address: Optional[str] = None,
        field1: Optional[str] = None,
        field2: Optional[str] = None,
        field3: Optional[str] = None,
        field4: Optional[str] = None,
        field5: Optional[str] = None,
        field6: Optional[str] = None,
        color: Optional[frame_mod.ColorEnum] = None,
    ) -> None:
        frames = record_mod.Telephone(
            name,
            number,
            address,
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            color,
        ).to_frames()

        expected_frames = self._get_frames(
            name,
            number,
            address,
            field1,
            field2,
            field3,
            field4,
            field5,
            field6,
            color,
        )

        self.assertEqual(frames, expected_frames)

    def test_to_frames(self) -> None:
        self._assert_frames(
            name=self.NAME,
        )
        self._assert_frames(
            name=self.NAME,
            number=self.NUMBER,
        )
        self._assert_frames(
            name=self.NAME,
            address=self.ADDRESS,
        )
        self._assert_frames(
            name=self.NAME,
            number=self.NUMBER,
            color=self.COLOR,
        )
        self._assert_frames(
            name=self.NAME,
            number=self.NUMBER,
            address=self.ADDRESS,
            field1=self.FIELD1,
            field3=self.FIELD3,
            field4=self.FIELD4,
            field6=self.FIELD6,
        )
        self._assert_frames(
            name=self.NAME,
            number=self.NUMBER,
            address=self.ADDRESS,
            field1=self.FIELD1,
            field2=self.FIELD2,
            field3=self.FIELD3,
            field4=self.FIELD4,
            field5=self.FIELD5,
            field6=self.FIELD6,
            color=self.COLOR,
        )


class BusinessCardTest(TestCase):
    EMPLOYER: str = "Acme Inc"
    NAME: str = "John Doe"
    TELEPHONE_NUMBER: str = "123-456"
    TELEX_NUMBER: str = "456-789"
    FAX_NUMBER: str = "789-123"
    POSITION: str = "Engineer"
    DEPARTMENT: str = "Engineering"
    PO_BOX: str = "134235"
    ADDRESS: str = "Nowhere St"
    MEMO: str = "Nice guy"
    COLOR: frame_mod.ColorEnum = frame_mod.ColorEnum.GREEN

    def _get_frames(
        self,
        employer: str,
        name: str,
        telephone_number: Optional[str] = None,
        telex_number: Optional[str] = None,
        fax_number: Optional[str] = None,
        position: Optional[str] = None,
        department: Optional[str] = None,
        po_box: Optional[str] = None,
        address: Optional[str] = None,
        memo: Optional[str] = None,
        color: Optional[frame_mod.ColorEnum] = None,
    ) -> List[frame_mod.Frame]:
        text_list = _raw_list_to_text_list(
            [
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
            ]
        )

        frames: List[frame_mod.Frame] = []
        if color is not None:
            frames.append(frame_mod.Color.from_color_enum(color))

        frames.extend(frame_mod.Text.from_text_list(text_list))

        return frames

    def _assert_business_card(
        self,
        employer: str,
        name: str,
        telephone_number: Optional[str] = None,
        telex_number: Optional[str] = None,
        fax_number: Optional[str] = None,
        position: Optional[str] = None,
        department: Optional[str] = None,
        po_box: Optional[str] = None,
        address: Optional[str] = None,
        memo: Optional[str] = None,
        color: Optional[frame_mod.ColorEnum] = None,
    ) -> None:
        frames = self._get_frames(
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

        business_card = record_mod.BusinessCard.from_frames(frames)
        self.assertEqual(business_card.employer, employer)
        self.assertEqual(business_card.name, name)
        self.assertEqual(business_card.telephone_number, telephone_number)
        self.assertEqual(business_card.telex_number, telex_number)
        self.assertEqual(business_card.fax_number, fax_number)
        self.assertEqual(business_card.position, position)
        self.assertEqual(business_card.department, department)
        self.assertEqual(business_card.po_box, po_box)
        self.assertEqual(business_card.address, address)
        self.assertEqual(business_card.memo, memo)
        self.assertEqual(business_card.color, color)

    def test_from_frames(self) -> None:
        self._assert_business_card(
            employer=self.EMPLOYER,
            name=self.NAME,
        )

        self._assert_business_card(
            employer=self.EMPLOYER,
            name=self.NAME,
            telephone_number=self.TELEPHONE_NUMBER,
        )

        self._assert_business_card(
            employer=self.EMPLOYER,
            name=self.NAME,
            telephone_number=self.TELEPHONE_NUMBER,
            telex_number=self.TELEX_NUMBER,
            department=self.DEPARTMENT,
            address=self.ADDRESS,
            memo=self.MEMO,
            color=self.COLOR,
        )

        self._assert_business_card(
            employer=self.EMPLOYER,
            name=self.NAME,
            telephone_number=self.TELEPHONE_NUMBER,
            telex_number=self.TELEX_NUMBER,
            fax_number=self.FAX_NUMBER,
            position=self.POSITION,
            department=self.DEPARTMENT,
            po_box=self.PO_BOX,
            address=self.ADDRESS,
            memo=self.MEMO,
            color=self.COLOR,
        )

    def _assert_frames(
        self,
        employer: str,
        name: str,
        telephone_number: Optional[str] = None,
        telex_number: Optional[str] = None,
        fax_number: Optional[str] = None,
        position: Optional[str] = None,
        department: Optional[str] = None,
        po_box: Optional[str] = None,
        address: Optional[str] = None,
        memo: Optional[str] = None,
        color: Optional[frame_mod.ColorEnum] = None,
    ) -> None:
        frames = record_mod.BusinessCard(
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
        ).to_frames()

        expected_frames = self._get_frames(
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

        self.assertEqual(frames, expected_frames)

    def test_to_frames(self) -> None:
        self._assert_frames(
            employer=self.EMPLOYER,
            name=self.NAME,
        )

        self._assert_frames(
            employer=self.EMPLOYER,
            name=self.NAME,
            telephone_number=self.TELEPHONE_NUMBER,
        )

        self._assert_frames(
            employer=self.EMPLOYER,
            name=self.NAME,
            telephone_number=self.TELEPHONE_NUMBER,
            telex_number=self.TELEX_NUMBER,
            department=self.DEPARTMENT,
            address=self.ADDRESS,
            memo=self.MEMO,
            color=self.COLOR,
        )

        self._assert_frames(
            employer=self.EMPLOYER,
            name=self.NAME,
            telephone_number=self.TELEPHONE_NUMBER,
            telex_number=self.TELEX_NUMBER,
            fax_number=self.FAX_NUMBER,
            position=self.POSITION,
            department=self.DEPARTMENT,
            po_box=self.PO_BOX,
            address=self.ADDRESS,
            memo=self.MEMO,
            color=self.COLOR,
        )


class MemoTest(TestCase):
    TEXT: str = "Hello\nWorld"
    COLOR: frame_mod.ColorEnum = frame_mod.ColorEnum.GREEN

    def _get_frames(
        self, text: str, color: Optional[frame_mod.ColorEnum]
    ) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []
        if color is not None:
            frames.append(frame_mod.Color.from_color_enum(color))
        frames.extend(frame_mod.Text.from_text_list([text]))
        return frames

    def test_from_frames(self) -> None:
        memo = record_mod.Memo.from_frames(self._get_frames(self.TEXT, self.COLOR))
        self.assertEqual(memo.text, self.TEXT)
        self.assertEqual(memo.color, self.COLOR)

        memo = record_mod.Memo.from_frames(self._get_frames(self.TEXT, None))
        self.assertEqual(memo.text, self.TEXT)
        self.assertEqual(memo.color, None)

    def test_to_frames(self) -> None:
        self.assertEqual(
            record_mod.Memo(self.TEXT, self.COLOR).to_frames(),
            self._get_frames(self.TEXT, self.COLOR),
        )


class CalendarTest(TestCase):
    YEAR: int = 2021
    MONTH: int = 12
    DAYS: Set[int] = {1, 10, 19, 28}
    COLORS: List[frame_mod.ColorEnum] = (
        [frame_mod.ColorEnum.BLUE] * 10
        + [frame_mod.ColorEnum.GREEN] * 10
        + [frame_mod.ColorEnum.ORANGE] * 11
    )

    def _get_frames(
        self,
        year: int,
        month: int,
        days: Set[int],
        colors: Optional[List[frame_mod.ColorEnum]],
    ) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []
        frames.append(frame_mod.Date.from_date(datetime.date(year, month, 1)))
        frames.append(frame_mod.DayHighlight.from_days(days))
        if colors is not None:
            frames.append(
                frame_mod.DayColorHighlight.from_days_and_colors(
                    days,
                    colors,
                )
            )
        return frames

    def test_from_frames(self) -> None:
        calendar = record_mod.Calendar.from_frames(
            self._get_frames(
                year=self.YEAR,
                month=self.MONTH,
                days=self.DAYS,
                colors=None,
            )
        )
        self.assertEqual(calendar.year, self.YEAR)
        self.assertEqual(calendar.month, self.MONTH)
        self.assertEqual(calendar.days, self.DAYS)
        self.assertEqual(calendar.colors, None)

        calendar = record_mod.Calendar.from_frames(
            self._get_frames(
                year=self.YEAR,
                month=self.MONTH,
                days=self.DAYS,
                colors=self.COLORS,
            )
        )
        self.assertEqual(calendar.year, self.YEAR)
        self.assertEqual(calendar.month, self.MONTH)
        self.assertEqual(calendar.days, self.DAYS)
        self.assertEqual(calendar.colors, self.COLORS)

    def test_to_frames(self) -> None:
        self.assertEqual(
            record_mod.Calendar(self.YEAR, self.MONTH, self.DAYS, None).to_frames(),
            self._get_frames(
                year=self.YEAR,
                month=self.MONTH,
                days=self.DAYS,
                colors=None,
            ),
        )

        self.assertEqual(
            record_mod.Calendar(
                self.YEAR, self.MONTH, self.DAYS, self.COLORS
            ).to_frames(),
            self._get_frames(
                year=self.YEAR,
                month=self.MONTH,
                days=self.DAYS,
                colors=self.COLORS,
            ),
        )


class ScheduleTest(TestCase):
    def _get_frames(
        self,
        date: datetime.date,
        start_time: Optional[datetime.time],
        end_time: Optional[datetime.time],
        alarm_time: Optional[datetime.time],
        illustration: Optional[int],
        description: Optional[str],
        color: Optional[frame_mod.ColorEnum],
    ) -> List[frame_mod.Frame]:
        frames: List[frame_mod.Frame] = []

        frames.append(frame_mod.Date.from_date(date))

        if start_time is not None:
            if end_time is None:
                frames.append(frame_mod.Time.from_time(start_time))
            else:
                frames.append(
                    frame_mod.StartEndTime.from_start_end_times(start_time, end_time)
                )

        if alarm_time is not None:
            frames.append(frame_mod.Alarm.from_time(alarm_time))

        if illustration is not None:
            frames.append(frame_mod.Illustration.from_number(illustration))

        if color is not None:
            frames.append(frame_mod.Color.from_color_enum(color))

        if description is not None:
            frames.extend(frame_mod.Text.from_text(description))

        return frames

    def _assert_schedule(
        self,
        date: datetime.date,
        start_time: Optional[datetime.time],
        end_time: Optional[datetime.time],
        alarm_time: Optional[datetime.time],
        illustration: Optional[int],
        description: Optional[str],
        color: Optional[frame_mod.ColorEnum],
    ) -> None:
        frames = self._get_frames(
            date,
            start_time,
            end_time,
            alarm_time,
            illustration,
            description,
            color,
        )

        schedule = record_mod.Schedule.from_frames(frames)
        self.assertEqual(schedule.date, date)
        self.assertEqual(schedule.start_time, start_time)
        self.assertEqual(schedule.end_time, end_time)
        self.assertEqual(schedule.alarm_time, alarm_time)
        self.assertEqual(schedule.illustration, illustration)
        self.assertEqual(schedule.description, description)
        self.assertEqual(schedule.color, color)

    def test_from_frames(self) -> None:
        self._assert_schedule(
            date=datetime.date(2020, 11, 1),
            start_time=None,
            end_time=None,
            alarm_time=None,
            illustration=None,
            description="do something",
            color=None,
        )
        self._assert_schedule(
            date=datetime.date(2020, 11, 1),
            start_time=datetime.time(23, 3),
            end_time=None,
            alarm_time=None,
            illustration=None,
            description=None,
            color=None,
        )
        self._assert_schedule(
            date=datetime.date(2020, 11, 1),
            start_time=datetime.time(22, 3),
            end_time=datetime.time(23, 4),
            alarm_time=None,
            illustration=None,
            description=None,
            color=None,
        )
        self._assert_schedule(
            date=datetime.date(2020, 11, 1),
            start_time=datetime.time(22, 3),
            end_time=datetime.time(23, 4),
            alarm_time=datetime.time(21, 0),
            illustration=None,
            description=None,
            color=None,
        )
        self._assert_schedule(
            date=datetime.date(2020, 11, 1),
            start_time=datetime.time(22, 3),
            end_time=datetime.time(23, 4),
            alarm_time=datetime.time(21, 0),
            illustration=3,
            description="Do something",
            color=frame_mod.ColorEnum.ORANGE,
        )

    def _assert_frames(
        self,
        date: datetime.date,
        start_time: Optional[datetime.time],
        end_time: Optional[datetime.time],
        alarm_time: Optional[datetime.time],
        illustration: Optional[int],
        description: Optional[str],
        color: Optional[frame_mod.ColorEnum],
    ) -> None:
        schedule = record_mod.Schedule(
            date,
            start_time,
            end_time,
            alarm_time,
            illustration,
            description,
            color,
        )

        self.assertEqual(
            schedule.to_frames(),
            self._get_frames(
                date,
                start_time,
                end_time,
                alarm_time,
                illustration,
                description,
                color,
            ),
        )

    def test_to_frames(self) -> None:
        self._assert_frames(
            date=datetime.date(2020, 11, 1),
            start_time=None,
            end_time=None,
            alarm_time=None,
            illustration=None,
            description="do something",
            color=None,
        )
        self._assert_frames(
            date=datetime.date(2020, 11, 1),
            start_time=datetime.time(23, 3),
            end_time=None,
            alarm_time=None,
            illustration=None,
            description=None,
            color=None,
        )
        self._assert_frames(
            date=datetime.date(2020, 11, 1),
            start_time=datetime.time(22, 3),
            end_time=datetime.time(23, 4),
            alarm_time=None,
            illustration=None,
            description=None,
            color=None,
        )
        self._assert_frames(
            date=datetime.date(2020, 11, 1),
            start_time=datetime.time(22, 3),
            end_time=datetime.time(23, 4),
            alarm_time=datetime.time(21, 0),
            illustration=None,
            description=None,
            color=None,
        )
        self._assert_frames(
            date=datetime.date(2020, 11, 1),
            start_time=datetime.time(22, 3),
            end_time=datetime.time(23, 4),
            alarm_time=datetime.time(21, 0),
            illustration=3,
            description="Do something",
            color=frame_mod.ColorEnum.ORANGE,
        )


# class ReminderTest(TestCase):
#     def test_from_frames(self) -> None:
#         pass
#     def test_to_frames(self) -> None:
#         pass
# class ToDoTest(TestCase):
#     def test_from_frames(self) -> None:
#         pass
#     def test_to_frames(self) -> None:
#         pass
# class ExpenseTest(TestCasselfe): -> None:
#         pass
#     def test_to_frames(self) -> None:
#         pass
#     def test_from_frames()
