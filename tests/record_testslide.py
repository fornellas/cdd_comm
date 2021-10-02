from typing import List, Optional

from testslide import TestCase

import cdd_comm.frame as frame_mod
import cdd_comm.record as record_mod


class TelephoneTest(TestCase):
    COLOR: frame_mod.ColorEnum = frame_mod.ColorEnum.GREEN
    NAME: str = "John Doe"
    NUMBER: str = "123-456"
    ADDRESS: str = "Nowhere St"
    FIELD1: str = "Field 1"
    FIELD2: str = "Field 2"
    FIELD3: str = "Field 3"
    FIELD4: str = "Field 4"
    FIELD5: str = "Field 5"
    FIELD6: str = "Field 6"

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
        raw_list: List[Optional[str]] = [name]
        raw_list.append(number)
        raw_list.append(address)
        raw_list.append(field1)
        raw_list.append(field2)
        raw_list.append(field3)
        raw_list.append(field4)
        raw_list.append(field5)
        raw_list.append(field6)

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
