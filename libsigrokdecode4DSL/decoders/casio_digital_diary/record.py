from abc import ABC, abstractmethod
from typing import List, Optional, Dict, ClassVar
from . import frame
from dataclasses import dataclass


class Record(ABC):

    DESCRIPTION: str = "Record"

    DIRECTORY: ClassVar[Optional[frame.Directory]] = None

    DIRECTORY_TO_RECORD: Dict[frame.Directory, "Record"] = {}

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
    memo: Optional[str]

    DIRECTORY: ClassVar[Optional[frame.Directory]] = frame.TelephoneDirectory

    DESCRIPTION: str = "Telephone"

    def __str__(self):
        return f"Telephone: {repr(self.name)}, {repr(self.number)}, {repr(self.address)}, {repr(self.memo)} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Telephone":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += str(f.text)
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")
        fields: List[str] = [None if v == "" else v for v in text.split(chr(0x1F))]
        if not len(fields):
            raise ValueError("Missing name text frame")
        name = fields[0]
        number = None
        if len(fields) > 1:
            number = fields[1]
        address = None
        if len(fields) > 2:
            address = fields[2]
        memo = None
        if len(fields) > 3:
            memo = fields[3]
        return cls(color, name, number, address, memo)

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError


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

    DIRECTORY: ClassVar[Optional[frame.Directory]] = frame.BusinessCardDirectory

    DESCRIPTION: str = "Business Card"

    def __str__(self):
        return f"Business Card: {repr(self.employer)}, {repr(self.name)}, {repr(self.telephone_number)}, {repr(self.telex_number)}, {repr(self.fax_number)}, {repr(self.position)}, {repr(self.department)}, {repr(self.po_box)}, {repr(self.address)}, {repr(self.memo)} ({self.color})"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Telephone":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += str(f.text)
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")
        fields: List[str] = [None if v == "" else v for v in text.split(chr(0x1F))]
        if len(fields) < 2:
            raise ValueError("Missing name and / or employer text frame")
        employer = fields[0]
        name = fields[1]
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

    DIRECTORY: ClassVar[Optional[frame.Directory]] = frame.MemoDirectory

    DESCRIPTION: str = "Memo"

    def __str__(self):
        return f"Memo: {repr(self.text)}"

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Telephone":
        text = ""
        color = "Blue"
        for f in frames:
            if isinstance(f, frame.Color):
                color = f.name
            elif isinstance(f, frame.Text):
                text += str(f.text)
            else:
                raise ValueError(f"Unknown frame type: {type(f)}")

        return cls(color, text)

    def to_frames(self) -> List[frame.Frame]:
        raise NotImplementedError
