from typing import List, Optional

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
