from dataclasses import dataclass


@dataclass
class SymbolTable:
    symbol_table = {
        "R0": 0,
        "R1": 1,
        "R2": 2,
        "R3": 3,
        "R4": 4,
        "R5": 5,
        "R6": 6,
        "R7": 7,
        "R8": 8,
        "R9": 9,
        "R10": 10,
        "R11": 11,
        "R12": 12,
        "R13": 13,
        "R14": 14,
        "R15": 15,
        "SCREEN": 16384,
        "KDB": 24576,
        "SP": 0,
        "LCL": 1,
        "ARG": 2,
        "THIS": 3,
        "THAT": 4,
    }
    var_value: int = 16

    def add_entry(self, symbol: str, value: int) -> None:
        self.symbol_table[symbol] = value

    def add_variable(self, symbol: str) -> None:
        self.symbol_table[symbol] = self.var_value
        self.var_value += 1

    def contains(self, symbol: str) -> bool:
        return symbol in self.symbol_table.keys()

    def get_address(self, symbol: str) -> int:
        return self.symbol_table[symbol]
