from dataclasses import dataclass, field
from typing import Iterable

from n2t.core.compiler.symbol_table import SymbolTable
from n2t.core.compiler.tokenizer import token_type
from n2t.core.compiler.tokens import OPERATORS


@dataclass
class CompilationEngine:
    tokens: list[str] = field(default_factory=list)
    index: int = 0
    indentation: int = 0
    labels: int = 0
    class_symbol_table: SymbolTable = field(default_factory=SymbolTable)
    method_symbol_table: SymbolTable = field(default_factory=SymbolTable)
    class_name: str = ""
    compilations: list[str] = field(default_factory=list)

    def get_current_token(self) -> str:
        if self.index == len(self.tokens):
            return "ERROR"
        return self.tokens[self.index]

    def advance(self) -> None:
        self.index += 1

    def compile_class(self) -> Iterable[str]:
        current_token = self.get_current_token()
        assert current_token == "class"
        self.advance()
        assert token_type(self.get_current_token()) == "IDENTIFIER"
        self.class_name = self.get_current_token()
        self.advance()
        assert self.get_current_token() == "{"
        self.advance()
        if self.get_current_token() in ["field", "static"]:
            self.compile_class_var_dec()

        while self.get_current_token() in ["constructor", "method", "function"]:
            self.compile_subroutine_dec()

        # assert self.get_current_token() == "}"
        # assert self.index == len(self.tokens) - 1
        print(self.class_symbol_table)
        print(self.method_symbol_table)
        return self.compilations

    def compile_class_var_dec(self) -> None:
        current_token = self.get_current_token()
        assert current_token in ["field", "static"]
        kind = current_token
        self.advance()

        current_token = self.get_current_token()
        assert (
            current_token in ["int", "char", "boolean", "void"]
            or token_type(current_token) == "IDENTIFIER"
        )
        var_type = current_token
        self.advance()

        current_token = self.get_current_token()
        assert token_type(current_token) == "IDENTIFIER"
        name = current_token
        self.class_symbol_table.define(name, var_type, kind)
        self.advance()

        while self.get_current_token() == ",":
            self.advance()
            current_token = self.get_current_token()
            assert token_type(current_token) == "IDENTIFIER"
            name = current_token
            self.class_symbol_table.define(name, var_type, kind)
            self.advance()

        assert self.get_current_token() == ";"
        self.advance()
        return

    def compile_subroutine_dec(self) -> None:
        self.method_symbol_table.reset()
        assert self.get_current_token() in ["constructor", "method", "function"]
        subroutine_type = self.get_current_token()
        self.advance()
        if subroutine_type == "method":
            self.method_symbol_table.define("this", self.class_name, "argument")

        current_token = self.get_current_token()
        assert (
            current_token in ["int", "char", "boolean", "void"]
            or token_type(current_token) == "IDENTIFIER"
        )
        self.advance()

        assert token_type(self.get_current_token()) == "IDENTIFIER"
        subroutine_name = self.class_name + "." + self.get_current_token()
        self.advance()

        assert self.get_current_token() == "("
        self.advance()

        if self.get_current_token() != ")":
            self.compile_parameter_list()

        assert self.get_current_token() == ")"
        self.advance()

        self.compilations.append(
            subroutine_type
            + " "
            + subroutine_name
            + " "
            + str(self.method_symbol_table.var_count("local"))
        )
        self.indentation += 1
        if subroutine_type == "method":
            self.compilations.append(" " * 2 * self.indentation + "push argument 0")
            self.compilations.append(" " * 2 * self.indentation + "pop pointer 0")
        elif subroutine_type == "constructor":
            self.compilations.append(
                " " * 2 * self.indentation
                + "push constant "
                + str(self.method_symbol_table.var_count("field"))
            )
            self.compilations.append(" " * 2 * self.indentation + "call Memory.alloc 1")
            self.compilations.append(" " * 2 * self.indentation + "pop pointer 0")
        self.compile_subroutine_body()

    def compile_parameter_list(self) -> None:
        current_token = self.get_current_token()
        if (
            current_token in ["int", "char", "boolean"]
            or token_type(current_token) == "IDENTIFIER"
        ):
            var_type = current_token
            self.advance()

            current_token = self.get_current_token()
            assert token_type(current_token) == "IDENTIFIER"
            name = current_token
            self.method_symbol_table.define(name, var_type, "argument")
            self.advance()

            while self.get_current_token() == ",":
                self.advance()
                current_token = self.get_current_token()
                assert (
                    current_token in ["int", "char", "boolean", "void"]
                    or token_type(current_token) == "IDENTIFIER"
                )
                var_type = current_token
                self.advance()

                current_token = self.get_current_token()
                assert token_type(current_token) == "IDENTIFIER"
                name = current_token
                self.method_symbol_table.define(name, var_type, "argument")
                self.advance()

    def compile_subroutine_body(self) -> None:
        assert self.get_current_token() == "{"
        self.advance()
        while self.get_current_token() == "var":
            self.compile_var_dec()
            self.advance()

        self.compile_statements()
        # assert self.get_current_token() == '}'

    def compile_var_dec(self) -> None:
        current_token = self.get_current_token()
        assert current_token == "var"
        self.advance()

        current_token = self.get_current_token()
        assert (
            current_token in ["int", "char", "boolean", "void"]
            or token_type(current_token) == "IDENTIFIER"
        )
        var_type = current_token
        self.advance()

        current_token = self.get_current_token()
        assert token_type(current_token) == "IDENTIFIER"
        name = current_token
        self.method_symbol_table.define(name, var_type, "local")
        self.advance()

        while self.get_current_token() == ",":
            self.advance()
            current_token = self.get_current_token()
            assert token_type(current_token) == "IDENTIFIER"
            name = current_token
            self.class_symbol_table.define(name, var_type, "local")
            self.advance()

        assert self.get_current_token() == ";"

    def compile_statements(self) -> None:
        while token_type(self.get_current_token()) == "KEYWORD":
            if self.get_current_token() == "let":
                self.compile_let()
            elif self.get_current_token() == "if":
                self.compile_if()
            elif self.get_current_token() == "while":
                self.compile_while()
            elif self.get_current_token() == "do":
                self.compile_do()
            elif self.get_current_token() == "return":
                self.compile_return()

    def compile_let(self) -> None:
        current_token = self.get_current_token()
        assert current_token == "let"
        self.advance()
        name = self.get_current_token()
        if self.method_symbol_table.in_table(name):
            name = (
                self.method_symbol_table.kind_of(name)
                + " "
                + self.method_symbol_table.index_of(name)
            )
        elif self.class_symbol_table.in_table(name):
            name = (
                self.class_symbol_table.kind_of(name)
                + " "
                + self.class_symbol_table.index_of(name)
            )
        self.compile_expression()
        self.compilations.append(" " * 2 * self.indentation + "pop " + name)

    def compile_if(self) -> None:
        current_token = self.get_current_token()
        assert current_token == "if"
        self.advance()
        assert self.get_current_token() == "("
        self.advance()
        self.compile_expression()
        self.compilations.append(" " * 2 * self.indentation + "not")
        label1 = self.class_name + "." + str(self.labels)
        self.labels += 1
        label2 = self.class_name + "." + str(self.labels)
        self.labels += 1
        self.compilations.append(" " * 2 * self.indentation + "if-goto " + label1)
        self.compile_statements()
        self.compilations.append(" " * 2 * self.indentation + "goto " + label2)
        self.compilations.append(" " * 2 * (self.indentation - 1) + label1)
        self.compile_statements()
        self.compilations.append(" " * 2 * (self.indentation - 1) + label2)

    def compile_while(self) -> None:
        current_token = self.get_current_token()
        assert current_token == "while"
        self.advance()
        assert self.get_current_token() == "("
        self.advance()
        label1 = self.class_name + "." + str(self.labels)
        self.labels += 1
        label2 = self.class_name + "." + str(self.labels)
        self.labels += 1
        self.compilations.append(" " * 2 * (self.indentation - 1) + label1)
        self.compile_expression()
        self.compilations.append(" " * 2 * self.indentation + "not")
        self.compilations.append(" " * 2 * self.indentation + "if-goto " + label2)
        self.compile_statements()
        self.compilations.append(" " * 2 * self.indentation + "goto " + label1)
        self.compilations.append(" " * 2 * (self.indentation - 1) + label2)

    def compile_do(self) -> None:
        current_token = self.get_current_token()
        assert current_token == "do"
        self.advance()

        self.compile_expression()
        self.compilations.append(" " * 2 * self.indentation + "pop temp 0")

    def compile_expression(self) -> None:
        self.compile_term()
        while self.get_current_token() in OPERATORS:
            operator = self.get_current_token()
            self.advance()
            # term2 = self.get_current_token()
            self.compile_term()
            self.compile_operator(operator)
            self.advance()

    def compile_expression_list(self) -> None:
        pass

    def compile_term(self) -> None:
        current_token = self.get_current_token()
        print("aa" + current_token)
        if (
            token_type(current_token) == "INT_CONST"
            or token_type(current_token) == "STRING_CONST"
        ):
            self.compilations.append(
                " " * 2 * self.indentation + "push " + current_token
            )
        elif self.method_symbol_table.in_table(current_token):
            name = (
                self.method_symbol_table.kind_of(current_token)
                + " "
                + self.method_symbol_table.index_of(current_token)
            )
            self.compilations.append(" " * 2 * self.indentation + "push " + name)
        elif self.class_symbol_table.in_table(current_token):
            name = (
                self.class_symbol_table.kind_of(current_token)
                + " "
                + self.class_symbol_table.index_of(current_token)
            )
            self.compilations.append(" " * 2 * self.indentation + "push " + name)
        elif current_token in ["false", "null"]:
            self.compilations.append(" " * 2 * self.indentation + "push constant 0")
        elif current_token == "true":
            self.compilations.append(" " * 2 * self.indentation + "push constant 0")
            self.compilations.append(" " * 2 * self.indentation + "not")
        elif current_token == "this":
            self.compilations.append(" " * 2 * self.indentation + "push pointer 0")
        if self.index < len(self.tokens):
            if (
                token_type(self.get_current_token()) == "IDENTIFIER"
                and self.next_token() == "("
            ):
                # function call
                function_name = self.get_current_token()
                self.advance()
                self.advance()
                i = 0
                while self.tokens[self.index] != ")":
                    print("cc " + self.tokens[self.index])
                    self.compile_expression()
                    i += 1
                self.compilations.append(
                    " " * 2 * self.indentation + "call " + function_name + " " + str(i)
                )
            elif self.next_token() == ".":
                # function call
                method_name = self.get_current_token()
                self.advance()
                self.advance()
                method_name += "." + self.get_current_token()
                print("b " + self.tokens[self.index])
                self.advance()
                i = 0
                print("c " + self.tokens[self.index])
                self.advance()
                while self.next_token() != ")":
                    print("d " + self.get_current_token())
                    self.compile_expression()
                    i += 1
                self.compilations.append(
                    " " * 2 * self.indentation
                    + "call "
                    + method_name
                    + " "
                    + str(i + 1)
                )
            elif current_token == "(":
                self.advance()
                self.compile_expression()

        self.advance()

    def next_token(self) -> str:
        try:
            return self.tokens[self.index + 1]
        except IndexError:
            return ""

    def compile_return(self) -> None:
        current_token = self.get_current_token()
        assert current_token == "return"
        self.advance()

        current_token = self.get_current_token()
        if current_token == ";":
            self.compilations.append(" " * 2 * self.indentation + "push constant 0")
            self.compilations.append(" " * 2 * self.indentation + "return")
        else:
            self.compile_expression()
            self.compilations.append(" " * 2 * self.indentation + "return")

    def compile_operator(self, operator: str) -> None:
        if operator == "+":
            self.compilations.append(" " * 2 * self.indentation + "add")
        elif operator == "-":
            self.compilations.append(" " * 2 * self.indentation + "sub")
        elif operator == "*":
            self.compilations.append(" " * 2 * self.indentation + "Math.multiply 2")
        elif operator == "/":
            self.compilations.append(" " * 2 * self.indentation + "Math.divide 2")
        elif operator == "&":
            self.compilations.append(" " * 2 * self.indentation + "and")
        elif operator == "|":
            self.compilations.append(" " * 2 * self.indentation + "or")
        elif operator == "<":
            self.compilations.append(" " * 2 * self.indentation + "lt")
        elif operator == ">":
            self.compilations.append(" " * 2 * self.indentation + "gt")
        elif operator == "=":
            self.compilations.append(" " * 2 * self.indentation + "eq")
