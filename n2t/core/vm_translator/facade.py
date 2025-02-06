from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from n2t.core.vm_translator.parser import arg1, arg2, command_type, get_segment_pointer


@dataclass
class VMTranslator:
    translations: list[str]
    function_name: str = ""
    comparisons: int = 0
    function_calls: int = 1

    @classmethod
    def create(cls) -> VMTranslator:
        return cls(list())

    def set_function_name(self, function_name: str) -> None:
        self.function_name = function_name

    def write_bootstrap(self) -> None:
        self.translations.append("@256")
        self.translations.append("D=A")
        self.translations.append("@SP")
        self.translations.append("M=D")
        self.translations.append("@LCL")
        self.translations.append("M=-1")
        self.translations.append("D=M")
        self.translations.append("@ARG")
        self.translations.append("M=D-1")
        self.translations.append("D=M")
        self.translations.append("@THIS")
        self.translations.append("M=D-1")
        self.translations.append("D=M")
        self.translations.append("@THAT")
        self.translations.append("M=D-1")
        self.translations.append("D=M")
        self.translate_call("Sys.init", 0)

    def translate(self, vm_language: Iterable[str], boot: bool) -> Iterable[str]:
        if boot:
            self.write_bootstrap()

        for instruction in vm_language:
            cmd_type = command_type(instruction)
            if cmd_type == "ERROR":
                continue
            elif cmd_type == "C_ARITHMETIC":
                self.translate_arithmetic(arg1(instruction))
            elif cmd_type == "C_LABEL":
                self.translate_label(arg1(instruction))
            elif cmd_type == "C_GOTO":
                self.translate_goto(arg1(instruction))
            elif cmd_type == "C_IF":
                self.translate_if(arg1(instruction))
            elif cmd_type == "C_FUNCTION":
                self.translate_function(arg1(instruction), arg2(instruction))
            elif cmd_type == "C_CALL":
                self.translate_call(arg1(instruction), arg2(instruction))
            elif cmd_type == "C_RETURN":
                self.translate_return()
            else:
                self.translate_push_pop(instruction)

        return self.translations

    def translate_arithmetic(self, command: str) -> None:
        if command not in ["not", "neg"]:
            self.pop_value_from_stack_to_d()
        self.pop_value_from_stack_to_a()

        if command == "add":
            self.translations.append("M=M+D")
        elif command == "sub":
            self.translations.append("M=M-D")
        elif command == "neg":
            self.translations.append("M=-M")
        elif command == "and":
            self.translations.append("M=M&D")
        elif command == "or":
            self.translations.append("M=M|D")
        elif command == "not":
            self.translations.append("M=!M")
        elif command in ["eq", "gt", "lt"]:
            self.translate_comparison(command)

        self.increment_pc()

    def translate_push_pop(self, instruction: str) -> None:
        i = str(arg2(instruction))
        segment = arg1(instruction)
        if command_type(instruction) == "C_PUSH":
            self.translate_push(i, segment)
        elif command_type(instruction) == "C_POP":
            self.translate_pop(i, segment)

    def translate_label(self, label: str) -> None:
        self.translations.append(f"({self.function_name}${label})")

    def translate_goto(self, label: str) -> None:
        self.translations.append(f"@{self.function_name}${label}")
        self.translations.append("0;JMP")

    def translate_if(self, label: str) -> None:
        self.pop_value_from_stack_to_d()
        self.translations.append(f"@{self.function_name}${label}")
        # not equals 0 is true
        self.translations.append("D;JNE")

    def translate_function(self, function_name: str, n_vars: int) -> None:
        self.function_name = function_name
        self.function_calls = 1
        self.translations.append(f"({function_name})")
        for _ in range(n_vars):
            self.translations.append("D=0")
            self.push_d_onto_stack()

    def translate_return(self) -> None:
        # end frame -> R13
        # return_address -> R14
        self.translations.append("@LCL")
        self.translations.append("D=M")
        self.translations.append("@R13")
        self.translations.append("M=D")

        self.translations.append("@R13")
        self.translations.append("D=M")
        self.translations.append("@5")
        self.translations.append("D=D-A")
        self.translations.append("A=D")
        self.translations.append("D=M")
        self.translations.append("@R14")
        self.translations.append("M=D")

        self.pop_value_from_stack_to_d()
        self.translations.append("@ARG")
        self.translations.append("A=M")
        self.translations.append("M=D")

        self.translations.append("@ARG")
        self.translations.append("D=M+1")
        self.translations.append("@SP")
        self.translations.append("M=D")

        self.restore_segment_pointer("THAT", 1)
        self.restore_segment_pointer("THIS", 2)
        self.restore_segment_pointer("ARG", 3)
        self.restore_segment_pointer("LCL", 4)

        self.translations.append("@R14")
        self.translations.append("A=M")
        self.translations.append("0;JMP")

    def restore_segment_pointer(self, segment: str, index: int) -> None:
        self.translations.append("@R13")
        self.translations.append("D=M")
        self.translations.append(f"@{index}")
        self.translations.append("D=D-A")
        self.translations.append("A=D")
        self.translations.append("D=M")
        self.translations.append(f"@{segment}")
        self.translations.append("M=D")

    def translate_call(self, function_name: str, n_args: int) -> None:
        return_address = self.function_name + "$ret." + str(self.function_calls)
        self.function_calls += 1

        self.translations.append(f"@{return_address}")
        self.translations.append("D=A")
        self.push_d_onto_stack()

        self.push_segment_pointer("LCL")
        self.push_segment_pointer("ARG")
        self.push_segment_pointer("THIS")
        self.push_segment_pointer("THAT")

        self.translations.append("@SP")
        self.translations.append("D=M")
        self.translations.append(f"@{str(5 + n_args)}")
        self.translations.append("D=D-A")
        self.translations.append("@ARG")
        self.translations.append("M=D")

        self.translations.append("@SP")
        self.translations.append("D=M")
        self.translations.append("@LCL")
        self.translations.append("M=D")

        self.translations.append(f"@{function_name}")
        self.translations.append("0;JMP")

        self.translations.append(f"({return_address})")

    def translate_push(self, i: str, segment: str) -> None:
        if segment == "constant":
            self.translate_push_constant(i)
        else:
            self.calculate_address(i, segment)
            self.translations.append("D=M")
            self.push_d_onto_stack()

    def calculate_address(self, i: str, segment: str) -> None:
        if segment == "static":
            self.translations.append(f"@{self.function_name.split('.')[0]}.{i}")
        elif segment == "temp":
            self.translations.append(f"@{str(5+int(i))}")
        elif segment == "pointer":
            segment_pointer = get_segment_pointer("this")
            if i == "1":
                segment_pointer = get_segment_pointer("that")
            self.translations.append(f"@{segment_pointer}")
        else:
            segment_pointer = get_segment_pointer(segment)
            self.translations.append(f"@{segment_pointer}")
            self.translations.append("D=M")
            self.translations.append(f"@{i}")
            self.translations.append("A=D+A")

    def translate_pop(self, i: str, segment: str) -> None:
        self.calculate_address(i, segment)
        self.translations.append("D=A")
        self.translations.append("@R14")  # save address to reg14
        self.translations.append("M=D")

        self.pop_value_from_stack_to_d()
        self.translations.append("@R14")
        self.translations.append("A=M")
        self.translations.append("M=D")

    def push_d_onto_stack(self) -> None:
        self.translations.append("@SP")
        self.translations.append("A=M")
        self.translations.append("M=D")
        self.increment_pc()

    def translate_push_constant(self, constant: str) -> None:
        self.translations.append(f"@{constant}")
        self.translations.append("D=A")
        self.set_a_to_sp()
        self.translations.append("M=D")
        self.increment_pc()

    def translate_comparison(self, command: str) -> None:
        self.translations.append("D=M-D")
        self.translations.append(f"@COMPARE_{self.comparisons}")

        if command == "eq":
            self.translations.append("D;JEQ")
        elif command == "gt":
            self.translations.append("D;JGT")
        elif command == "lt":
            self.translations.append("D;JLT")

        self.set_a_to_sp()
        self.translations.append("M=0")  # false

        self.translations.append(f"@END_CMP.{self.comparisons}")
        self.translations.append("0;JMP")

        self.translations.append(f"(COMPARE_{self.comparisons})")
        self.set_a_to_sp()
        self.translations.append("M=-1")  # true

        self.translations.append(f"(END_CMP.{self.comparisons})")
        self.comparisons += 1

    # A points to sp, A = RAM[SP]
    def set_a_to_sp(self) -> None:
        self.translations.append("@SP")
        self.translations.append("A=M")

    def decrement_pc(self) -> None:
        self.translations.append("@SP")
        self.translations.append("M=M-1")

    def increment_pc(self) -> None:
        self.translations.append("@SP")
        self.translations.append("M=M+1")

    def pop_value_from_stack_to_d(self) -> None:
        self.translations.append("@SP")
        self.translations.append("M=M-1")
        self.translations.append("A=M")
        self.translations.append("D=M")

    def pop_value_from_stack_to_a(self) -> None:
        self.translations.append("@SP")
        self.translations.append("M=M-1")
        self.translations.append("A=M")

    def push_segment_pointer(self, segment: str) -> None:
        self.translations.append(f"@{segment}")
        self.translations.append("D=M")
        self.push_d_onto_stack()
