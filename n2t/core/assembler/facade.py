from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class Assembler:
    @classmethod
    def create(cls) -> Assembler:
        return cls()

    def assemble(self, assembly: Iterable[str]) -> Iterable[str]:
        return []  # TODO: your work for Project 6 starts here
