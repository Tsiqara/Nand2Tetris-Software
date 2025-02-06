from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from n2t.core.assembler.code import Code
from n2t.core.assembler.parser import (
    comp,
    dest,
    instruction_type,
    jump,
    remove_comments,
    string_to_binary,
    symbol,
)
from n2t.core.assembler.symbol_table import SymbolTable


@dataclass
class Assembler:
    code: Code
    symbol_table: SymbolTable

    @classmethod
    def create(cls) -> Assembler:
        return cls(Code(), SymbolTable())

    def assemble(self, assembly: Iterable[str]) -> Iterable[str]:
        translations = list()
        self.first_pass(assembly)
        for instruction in assembly:
            if instruction_type(instruction) == "A_INSTRUCTION":
                translations.append(self.translate_a_instruction(instruction))
            elif instruction_type(instruction) == "C_INSTRUCTION":
                translations.append(self.translate_c_instruction(instruction))
        return translations

    def first_pass(self, assembly: Iterable[str]) -> None:
        line_number = 0
        for instruction in assembly:
            if instruction_type(instruction) == "L_INSTRUCTION":
                self.symbol_table.add_entry(symbol(instruction), line_number)
            elif instruction_type(instruction) != "BLANK":
                line_number += 1

    def translate_a_instruction(self, instruction: str) -> str:
        instruction = instruction.strip()
        instruction = remove_comments(instruction)
        sym = symbol(instruction)
        if not sym[0].isdigit():
            if not self.symbol_table.contains(sym):
                self.symbol_table.add_variable(sym)
            address = self.symbol_table.get_address(sym)
            binary = string_to_binary(address)
        else:
            binary = string_to_binary(int(sym))
        return (16 - len(binary)) * "0" + binary

    def translate_c_instruction(self, instruction: str) -> str:
        instruction = instruction.strip()
        instruction = remove_comments(instruction)
        destination = dest(instruction)
        comparator = comp(instruction)
        jmp = jump(instruction)

        return (
            "111"
            + self.code.comp(comparator)
            + self.code.dest(destination)
            + self.code.jump(jmp)
        )
