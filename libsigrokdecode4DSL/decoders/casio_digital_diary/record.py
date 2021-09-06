from abc import ABC, abstractmethod
from typing import List
from . import frame
from dataclasses import dataclass


class Record(ABC):
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
    number: str
    address: str
    memo: str

    @classmethod
    def from_frames(cls, frames: List[frame.Frame]) -> "Record":
        pass

    def to_frames(self) -> List[frame.Frame]:
        pass
