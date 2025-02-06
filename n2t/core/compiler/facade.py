from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from n2t.core.compiler.compilation_engine import CompilationEngine
from n2t.core.compiler.tokenizer import Tokenizer
from n2t.core.compiler.xml_compilation_engine import XMLCompilationEngine


@dataclass
class Compiler:
    translations: list[str]
    tokenizer: Tokenizer = field(default_factory=Tokenizer)
    xml_compilation_engine: XMLCompilationEngine = field(
        default_factory=XMLCompilationEngine
    )
    compilation_engine: CompilationEngine = field(default_factory=CompilationEngine)

    @classmethod
    def create(cls) -> Compiler:
        return cls(list())

    def compile(self, jack_lines: Iterable[str]) -> list[Iterable[str]]:
        jack_tokens = Tokenizer().tokenize(jack_lines)
        # print(jack_tokens)
        self.xml_compilation_engine = XMLCompilationEngine(list(jack_tokens))
        self.compilation_engine = CompilationEngine(list(jack_tokens))
        return [
            self.xml_compilation_engine.compile_class(),
            self.compilation_engine.compile_class(),
        ]
