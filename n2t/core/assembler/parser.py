from sympy.parsing.sympy_parser import null


def string_to_binary(val: int) -> str:
    return "{0:b}".format(val)


def remove_comments(instruction: str) -> str:
    instructions = instruction.split("//")
    return instructions[0].strip()


def instruction_type(instruction: str) -> str:
    if instruction.startswith("@"):
        return "A_INSTRUCTION"
    if instruction.startswith("("):
        return "L_INSTRUCTION"
    if instruction.startswith(" ") or instruction.startswith("//") or instruction == "":
        return "BLANK"
    return "C_INSTRUCTION"


def symbol(instruction: str) -> str:
    if instruction.startswith("@"):
        return instruction[1:]
    if instruction.startswith("("):
        return instruction[1:-1]
    return null


def dest(instruction: str) -> str:
    components = instruction.split("=")
    if len(components) == 1:
        return ""
    else:
        return components[0]


def comp(instruction: str) -> str:
    components = instruction.split("=")
    if len(components) == 1:
        instruction = components[0]
    else:
        instruction = components[1]
    return instruction.split(";")[0]


def jump(instruction: str) -> str:
    components = instruction.split("=")
    if len(components) == 1:
        instruction = components[0]
    else:
        instruction = components[1]
    components = instruction.split(";")
    if len(components) == 2:
        return components[1]
    else:
        return null
