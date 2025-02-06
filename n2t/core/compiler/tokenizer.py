import re
from dataclasses import dataclass, field
from typing import Iterable

from n2t.core.compiler.tokens import KEYWORDS, SYMBOLS


@dataclass
class Tokenizer:
    tokens: list[str] = field(default_factory=list)

    def tokenize(self, lines: Iterable[str]) -> Iterable[str]:
        first_split_tokens = []
        for line in lines:
            if (
                line.startswith(" ")
                or line.startswith("//")
                or line == ""
                or line.startswith("/**")
                or line.startswith("*")
            ):
                continue
            if "//" in line:
                line = line.split("//")[0]
            first_split_tokens += re.split(r"([{}\[\];(),.+\-*/~])", line)

        for token in first_split_tokens:
            if '"' not in token:
                self.tokens += token.split()
            else:
                self.tokens += token[: token.find('"')].split()
                self.tokens.append(token[token.find('"') : token.rfind('"') + 1])
                self.tokens += token[token.rfind('"') + 1 :].split()

        return self.tokens


def token_type(token: str) -> str:
    if token in KEYWORDS:
        return "KEYWORD"
    elif token in SYMBOLS:
        return "SYMBOL"
    elif '"' in token:
        return "STRING_CONST"
    try:
        if 0 <= int(token) <= 32767:
            return "INT_CONST"
    except ValueError:
        return "IDENTIFIER"
    return "ERROR"


def key_word(token: str) -> str:
    return KEYWORDS[token]


def symbol(token: str) -> str:
    return token


def identifier(token: str) -> str:
    return token


def int_val(token: str) -> int:
    return int(token)


def string_val(token: str) -> str:
    return token[1:-1]
