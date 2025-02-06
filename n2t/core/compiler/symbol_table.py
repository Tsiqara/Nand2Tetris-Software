from dataclasses import dataclass, field


@dataclass
class SymbolTable:
    table: dict[str, list[str]] = field(default_factory=dict)
    field_count: int = 0
    static_count: int = 0
    local_count: int = 0
    argument_count: int = 0

    def reset(self) -> None:
        self.field_count = 0
        self.static_count = 0
        self.local_count = 0
        self.argument_count = 0

    def define(self, name: str, type: str, kind: str) -> None:
        if kind == "static":
            self.table[name] = [type, kind, str(self.static_count)]
            self.static_count += 1
        elif kind == "local":
            self.table[name] = [type, kind, str(self.local_count)]
            self.local_count += 1
        elif kind == "argument":
            self.table[name] = [type, kind, str(self.argument_count)]
            self.argument_count += 1
        elif kind == "field":
            self.table[name] = [type, "this", str(self.field_count)]
            self.field_count += 1

    def var_count(self, kind: str) -> int:
        if kind == "static":
            return self.static_count
        elif kind == "local":
            return self.local_count
        elif kind == "argument":
            return self.argument_count
        elif kind == "field":
            return self.field_count
        return -1

    def kind_of(self, name: str) -> str:
        return self.table[name][1]

    def type_of(self, name: str) -> str:
        return self.table[name][0]

    def index_of(self, name: str) -> str:
        return self.table[name][2]

    def in_table(self, name: str) -> bool:
        return name in self.table
