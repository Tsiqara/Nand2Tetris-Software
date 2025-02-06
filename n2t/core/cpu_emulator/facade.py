from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from n2t.core.assembler.parser import comp, dest, instruction_type, jump, symbol


@dataclass
class Emulator:
    ram: dict[int, int] = field(default_factory=dict)
    a_register: int = 0
    d_register: int = 0
    pc_register: int = 0
    indentation: int = 0
    index: int = 0

    @classmethod
    def create(cls) -> Emulator:
        return cls(dict())

    def emulate(self, assembly: Iterable[str], cycles: int) -> Iterable[str]:
        translations = list()
        translations.append("{")
        self.indentation += 1
        translations.append(" " * 2 * self.indentation + '"RAM": {')
        self.indentation += 1

        instructions = list(assembly)
        while cycles > 0 and self.index < len(instructions):
            instruction = instructions[self.index]
            if instruction_type(instruction) == "A_INSTRUCTION":
                self.a_register = int(symbol(instruction))
                self.pc_register += 1
                cycles -= 1
                self.index += 1
            elif instruction_type(instruction) == "C_INSTRUCTION":
                self.emulate_c_instruction(instruction)
                self.pc_register += 1
                cycles -= 1

        c = 0
        for i in sorted(self.ram.keys()):
            pair = '"' + str(i) + '": ' + str(self.ram[i])
            if c != len(self.ram) - 1:
                pair += ","
            translations.append(" " * 2 * self.indentation + pair)
            c += 1

        self.indentation -= 1
        translations.append(" " * 2 * self.indentation + "}")
        self.indentation -= 1
        translations.append(" " * 2 * self.indentation + "}")
        return translations

    def emulate_c_instruction(self, instruction: str) -> None:
        destination = dest(instruction)
        comparator = comp(instruction)
        jmp = jump(instruction)
        result = self.compute_comp(comparator)
        if "M" in destination:
            self.ram[self.a_register] = result
        if "A" in destination:
            self.a_register = result
        if "D" in destination:
            self.d_register = result

        if jmp != "":
            self.emulate_jump(jmp)
        else:
            self.index += 1

    def compute_comp(self, comparator: str) -> int:
        ops = ["+", "-", "&", "|", "!"]
        for op in ops:
            if op in comparator:
                return self.compute_operation(comparator, op)
        if comparator == "A":
            return self.a_register
        elif comparator == "M":
            if self.a_register not in self.ram.keys():
                self.ram[self.a_register] = 0
            return self.ram[self.a_register]
        elif comparator == "D":
            return self.d_register
        else:
            # comparator.isdigit()
            return int(comparator)

    def compute_operation(self, comparator: str, operation: str) -> int:
        first_operand, second_operand = comparator.split(operation)
        first_operand = self.replace_operand_with_value(first_operand)
        second_operand = self.replace_operand_with_value(second_operand)
        if operation == "!":
            operation = "~"
        result = eval(first_operand + operation + second_operand)
        result = result & 0xFFFF
        if result & 0x8000:
            result -= 0x10000
        return int(result)

    def replace_operand_with_value(self, operand: str) -> str:
        if operand == "":
            return ""
        if operand == "A":
            return str(self.a_register)
        elif operand == "D":
            return str(self.d_register)
        elif operand == "M":
            if self.a_register not in self.ram.keys():
                self.ram[self.a_register] = 0
            return str(self.ram[self.a_register])
        else:
            return operand

    def emulate_jump(self, jmp: str) -> None:
        if jmp == "JMP":
            self.index = self.a_register
        elif jmp == "JGT":
            if self.d_register > 0:
                self.index = self.a_register
            else:
                self.index += 1
        elif jmp == "JGE":
            if self.d_register >= 0:
                self.index = self.a_register
            else:
                self.index += 1
        elif jmp == "JLT":
            if self.d_register < 0:
                self.index = self.a_register
            else:
                self.index += 1
        elif jmp == "JLE":
            if self.d_register <= 0:
                self.index = self.a_register
            else:
                self.index += 1
        elif jmp == "JEQ":
            if self.d_register == 0:
                self.index = self.a_register
            else:
                self.index += 1
        elif jmp == "JNE":
            if self.d_register != 0:
                self.index = self.a_register
            else:
                self.index += 1
