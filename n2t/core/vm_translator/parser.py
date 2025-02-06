def command_type(instruction: str) -> str:
    if instruction.startswith(" ") or instruction.startswith("//") or instruction == "":
        return "ERROR"
    instruction = instruction.strip()
    instruction = instruction.split("//")[0]
    parts = instruction.split()
    if parts[0] == "return":
        return "C_RETURN"
    elif len(parts) == 1:
        return "C_ARITHMETIC"
    elif parts[0] == "push":
        return "C_PUSH"
    elif parts[0] == "pop":
        return "C_POP"
    elif parts[0] == "label":
        return "C_LABEL"
    elif parts[0] == "goto":
        return "C_GOTO"
    elif parts[0] == "if-goto":
        return "C_IF"
    elif parts[0] == "function":
        return "C_FUNCTION"
    elif parts[0] == "call":
        return "C_CALL"
    return "ERROR"


def arg1(instruction: str) -> str:
    instruction = instruction.split("//")[0]
    parts = instruction.split()
    c_type = command_type(instruction)
    if c_type == "C_RETURN":
        return "ERROR"
    if len(parts) == 1:
        return parts[0]
    else:
        return parts[1]


def arg2(instruction: str) -> int:
    return int(instruction.split()[2])


segments = {
    "local": 1,
    "argument": 2,
    "this": 3,
    "that": 4,
}


def get_segment_pointer(segment: str) -> str:
    return str(segments[segment.lower()])
