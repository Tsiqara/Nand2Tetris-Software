from dataclasses import dataclass, field
from typing import Iterable

from n2t.core.compiler.tokenizer import token_type


@dataclass
class XMLCompilationEngine:
    tokens: list[str] = field(default_factory=list)
    index: int = 0
    indentation: int = 0
    compilations: list[str] = field(default_factory=list)

    def get_current_token(self) -> str:
        return self.tokens[self.index]

    def process(self, correct_strs: list[str]) -> None:
        cur_token = self.get_current_token()
        write_token = cur_token
        if cur_token in correct_strs:
            if cur_token == "<":
                write_token = "&lt;"
            elif cur_token == ">":
                write_token = "&gt;"
            elif cur_token == "&":
                write_token = "&amp;"

            self.compilations.append(
                " " * 2 * self.indentation
                + "<"
                + token_type(cur_token).lower()
                + "> "
                + write_token
                + " </"
                + token_type(cur_token).lower()
                + ">"
            )
        else:
            self.compilations.append(" " * 2 * self.indentation + "syntax error")
            print("syntax error")
        self.index += 1

    def write_identifier(self) -> None:
        cur_token = self.get_current_token()
        if token_type(cur_token) == "IDENTIFIER":
            self.compilations.append(
                " " * 2 * self.indentation
                + "<identifier> "
                + cur_token
                + " </identifier>"
            )
        self.index += 1

    def compile_class(self) -> Iterable[str]:
        self.compilations.append("<class>")
        self.indentation += 1
        self.process(["class"])
        self.write_identifier()
        self.process(["{"])
        while self.get_current_token() in ["static", "field"]:
            self.compile_class_var_dec()
        while self.get_current_token() in ["constructor", "function", "method"]:
            self.compile_subroutine_dec()
        self.process(["}"])
        self.indentation -= 1
        self.compilations.append("</class>")
        return self.compilations

    def compile_class_var_dec(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<classVarDec>")
        self.indentation += 1
        self.process(["static", "field"])
        self.compile_type_varname()
        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</classVarDec>")

    def compile_subroutine_dec(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<subroutineDec>")
        self.indentation += 1
        self.process(["constructor", "function", "method"])
        if token_type(self.get_current_token()) == "KEYWORD":
            self.process(["int", "char", "boolean", "void"])
        elif token_type(self.get_current_token()) == "IDENTIFIER":
            self.write_identifier()
        self.write_identifier()

        self.process(["("])
        self.compile_parameter_list()
        self.process([")"])

        self.compile_subroutine_body()
        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</subroutineDec>")

    def compile_parameter_list(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<parameterList>")
        self.indentation += 1
        while token_type(self.get_current_token()) != "SYMBOL":
            if token_type(self.get_current_token()) == "KEYWORD":
                self.process(["int", "char", "boolean"])
            elif token_type(self.get_current_token()) == "IDENTIFIER":
                self.write_identifier()
            self.write_identifier()
            if self.get_current_token() == ",":
                self.process([","])

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</parameterList>")

    def compile_subroutine_body(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<subroutineBody>")
        self.indentation += 1

        self.process(["{"])
        while self.get_current_token() == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.process(["}"])

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</subroutineBody>")

    def compile_var_dec(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<varDec>")
        self.indentation += 1

        self.process(["var"])
        self.compile_type_varname()

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</varDec>")

    def compile_type_varname(self) -> None:
        if token_type(self.get_current_token()) == "KEYWORD":
            self.process(["int", "char", "boolean"])
        elif token_type(self.get_current_token()) == "IDENTIFIER":
            self.write_identifier()
        self.write_identifier()
        while self.get_current_token() == ",":
            self.process([","])
            self.write_identifier()
        self.process([";"])

    def compile_statements(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<statements>")
        self.indentation += 1

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

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</statements>")

    def compile_let(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<letStatement>")
        self.indentation += 1

        self.process(["let"])
        self.write_identifier()
        if self.get_current_token() == "[":
            self.process(["["])
            self.compile_expression()
            self.process(["]"])
        self.process(["="])
        self.compile_expression()
        self.process([";"])

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</letStatement>")

    def compile_if(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<ifStatement>")
        self.indentation += 1

        self.process(["if"])
        self.process(["("])
        self.compile_expression()
        self.process([")"])

        self.process(["{"])
        self.compile_statements()
        self.process(["}"])

        if self.get_current_token() == "else":
            self.process(["else"])
            self.process(["{"])
            self.compile_statements()
            self.process(["}"])

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</ifStatement>")

    def compile_while(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<whileStatement>")
        self.indentation += 1

        self.process(["while"])
        self.process(["("])
        self.compile_expression()
        self.process([")"])

        self.process(["{"])
        self.compile_statements()
        self.process(["}"])

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</whileStatement>")

    def compile_do(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<doStatement>")
        self.indentation += 1

        self.process(["do"])
        # parse subroutine
        self.write_identifier()
        if self.get_current_token() == ".":
            self.process(["."])
            self.write_identifier()

        self.process(["("])
        self.compile_expression_list()
        self.process([")"])

        self.process([";"])

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</doStatement>")

    def compile_return(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<returnStatement>")
        self.indentation += 1

        self.process(["return"])
        if self.get_current_token() != ";":
            self.compile_expression()
        self.process([";"])

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</returnStatement>")

    def compile_expression(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<expression>")
        self.indentation += 1

        self.compile_term()
        if self.get_current_token() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            self.process(["+", "-", "*", "/", "&", "|", "<", ">", "="])
            self.compile_term()

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</expression>")

    def compile_expression_list(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<expressionList>")
        self.indentation += 1

        if self.get_current_token() != ")":
            self.compile_expression()
            while self.get_current_token() == ",":
                self.process([","])
                self.compile_expression()

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</expressionList>")

    def compile_term(self) -> None:
        self.compilations.append(" " * 2 * self.indentation + "<term>")
        self.indentation += 1

        cur_token = self.get_current_token()
        if token_type(cur_token) == "IDENTIFIER":
            #     varname| varname[expression] | subroutine
            next_token = self.tokens[self.index + 1]

            self.write_identifier()

            if next_token in ["(", "."]:
                if self.get_current_token() == ".":
                    self.process(["."])
                    self.write_identifier()

                self.process(["("])
                self.compile_expression_list()
                self.process([")"])
            elif next_token == "[":
                self.process(["["])
                self.compile_expression()
                self.process(["]"])
        else:
            #   integerConstant|stringConstant|keywordConstant|
            #   '(' expression ')'|unaryOp term
            if token_type(cur_token) == "INT_CONST":
                self.compilations.append(
                    " " * 2 * self.indentation
                    + "<integerConstant> "
                    + cur_token
                    + " </integerConstant>"
                )
                self.index += 1
            elif token_type(cur_token) == "STRING_CONST":
                if cur_token.startswith('"'):
                    cur_token = cur_token[1:]
                if cur_token.endswith('"'):
                    cur_token = cur_token[:-1]

                self.compilations.append(
                    " " * 2 * self.indentation
                    + "<stringConstant> "
                    + cur_token
                    + " </stringConstant>"
                )
                self.index += 1
            elif token_type(cur_token) == "KEYWORD" and cur_token in [
                "true",
                "false",
                "null",
                "this",
            ]:
                self.process(["true", "false", "null", "this"])
            elif cur_token == "(":
                self.process(["("])
                self.compile_expression()
                self.process([")"])
            elif token_type(cur_token) == "SYMBOL" and cur_token in ["-", "~"]:
                self.process(["-", "~"])
                self.compile_term()

        self.indentation -= 1
        self.compilations.append(" " * 2 * self.indentation + "</term>")
