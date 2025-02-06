from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from n2t.core import Compiler as DefaultCompiler
from n2t.infra import FileFormat
from n2t.infra.io import File


def iterate(file: Path) -> Iterator[str]:
    yield from File(file).load()


@dataclass
class JackProgram:  # TODO: your work for Projects 10 and 11 starts here
    paths: list[Path]
    compiler: Compiler = field(default_factory=DefaultCompiler.create)

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> JackProgram:
        path = Path(file_or_directory_name)
        paths = []
        if path.is_dir():
            jack_files = list(path.glob("*.jack"))
            for file in jack_files:
                cur_path = Path(file)
                if not cur_path.is_absolute():
                    cur_path = Path.cwd() / cur_path
                paths.append(cur_path)
        else:
            if not path.is_absolute():
                path = Path.cwd() / path
            paths.append(path)
        return cls(paths)

    def compile(self) -> None:
        for path in self.paths:
            xml_file = File(FileFormat.xml.convert(path))
            code = self.compiler.compile(iterate(path))
            xml_file.save(code[0])
            vm_file = File(FileFormat.vm.convert(path))
            vm_file.save(code[1])

    def __post_init__(self) -> None:
        for path in self.paths:
            FileFormat.jack.validate(path)


class Compiler(Protocol):  # pragma: no cover
    def compile(self, jack_lines: Iterable[str]) -> list[Iterable[str]]:
        pass
