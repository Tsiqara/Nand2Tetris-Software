from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from n2t.core import Assembler, Disassembler
from n2t.core import Assembler as DefaultAssembler
from n2t.core import Disassembler as DefaultDisassembler
from n2t.core import Emulator as DefaultEmulator
from n2t.infra.io import File, FileFormat


@dataclass
class Program:
    path: Path
    file_name: str
    cycles: int
    emulator: Emulator = field(default_factory=DefaultEmulator.create)
    assembler: Assembler = field(default_factory=DefaultAssembler.create)
    disassembler: Disassembler = field(default_factory=DefaultDisassembler.create)

    @classmethod
    def load_from(cls, file_name: str, cycles: int) -> Program:
        path = Path(file_name)
        if not path.is_absolute():
            path = Path.cwd() / path
        return cls(path, file_name, cycles)

    def __post_init__(self) -> None:
        if self.path.suffix == ".asm":
            hack_file = File(FileFormat.hack.convert(self.path))
            hack_file.save(self.assembler.assemble(self))
            self.path = Path(FileFormat.hack.convert(self.path))
            assembly_file = File(Path(self.file_name[:-4] + "1.asm"))
        else:
            assembly_file = File(Path(self.file_name[:-5] + "1.asm"))

        assembly_file.save(self.disassembler.disassemble(self))
        self.path = Path(assembly_file.path)

    def execute(self) -> None:
        json_file = File(FileFormat.json.convert(Path(self.file_name)))
        json_file.save(self.emulator.emulate(self, self.cycles))

    def __iter__(self) -> Iterator[str]:
        yield from File(self.path).load()


class Emulator(Protocol):  # pragma: no cover
    def emulate(self, assembly: Iterable[str], cycles: int) -> Iterable[str]:
        pass
