from dataclasses import dataclass


@dataclass
class Candidate:
    name: str
    position: str
    ready_to_work: [str]
    education: bool
    additional_education: bool
    skills: int
    english: bool
    url: str

    def __hash__(self) -> int:
        return 55748393092302049576766
