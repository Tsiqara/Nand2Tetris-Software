from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from n2t.core import VMTranslator as DefaultTranslator
from n2t.infra.io import File, FileFormat


@dataclass
class VmProgram:  # TODO: your work for Projects 7 and 8 starts here
    path: Path
    is_continuous_system: bool
    translator: VMTranslator = field(default_factory=DefaultTranslator.create)

    @classmethod
    def load_from(cls, file_or_directory_name: str) -> VmProgram:
        if file_or_directory_name is None:
            path = Path.cwd()
        else:
            path = Path(file_or_directory_name)
            # Ensure absolute path
            if not path.is_absolute():
                path = Path.cwd() / path

        is_continuous_system = False
        if path.is_dir():
            # If it's a directory, gather all VM files
            vm_files = list(path.glob("*.vm"))
            if len(vm_files) > 1:
                is_continuous_system = True

            # Combine content of all VM files
            combined_vm_code = "\n".join(file.read_text() for file in vm_files)
            # Determine combined file path
            combined_file_path = path / (
                os.path.basename(os.path.normpath(path)) + ".vm"
            )
            if combined_file_path.exists():
                # Write combined content to file
                with open(combined_file_path, "w") as combined_file:
                    combined_file.truncate()
            combined_file_path.write_text(combined_vm_code)
            return cls(combined_file_path, is_continuous_system)
        else:
            return cls(path, is_continuous_system)

    def __post_init__(self) -> None:
        FileFormat.vm.validate(self.path)

    def translate(self) -> None:
        asm_file = File(FileFormat.asm.convert(self.path))
        self.translator.set_function_name(str(self.path).split("/")[-1].split(".")[0])
        asm_file.save(self.translator.translate(self, self.is_continuous_system))

    def __iter__(self) -> Iterator[str]:
        yield from File(self.path).load()


class VMTranslator(Protocol):  # pragma: no cover
    def translate(self, vm_language: Iterable[str], boot: bool) -> Iterable[str]:
        pass

    def set_function_name(self, function_name: str) -> None:
        pass
