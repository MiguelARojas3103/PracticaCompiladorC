"""Pruebas del analizador léxico de Mini C según SKILL.md y la especificación."""

import pytest
from minic.diagnostics.diagnostic_code import LEX001
from minic.lexer.lexer import Lexer
from minic.lexer.token_type import TokenType
from minic.output.diagnostic_printer import format_diagnostic
from minic.output.token_printer import format_token


def test_empty_source() -> None:
    tokens, diagnostics = Lexer("").scan()
    assert len(diagnostics) == 0
    assert len(tokens) == 1
    assert tokens[0].type == TokenType.EOF
    assert tokens[0].lexeme == ""
    assert tokens[0].literal is None
    assert tokens[0].line == 1
    assert tokens[0].column == 1


def test_whitespace_and_positions() -> None:
    source = " \t\r\n a"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 0
    assert len(tokens) == 2
    assert tokens[0].type == TokenType.IDENTIFIER
    assert tokens[0].lexeme == "a"
    assert tokens[0].line == 2
    assert tokens[0].column == 2
    assert tokens[1].type == TokenType.EOF
    assert tokens[1].line == 2
    assert tokens[1].column == 3


def test_tab_counts_as_one_column() -> None:
    source = "\ta"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 0
    assert tokens[0].lexeme == "a"
    assert tokens[0].line == 1
    assert tokens[0].column == 2


def test_all_single_and_double_operators() -> None:
    source = "+ - = == != ( ) { } ;"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 0
    expected_types = [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.ASSIGN,
        TokenType.EQUAL_EQUAL,
        TokenType.NOT_EQUAL,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types


def test_integer_literal_values() -> None:
    source = "0 42 007"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 0
    assert tokens[0].literal == 0
    assert tokens[0].lexeme == "0"
    assert tokens[1].literal == 42
    assert tokens[1].lexeme == "42"
    assert tokens[2].literal == 7
    assert tokens[2].lexeme == "007"


def test_keywords_vs_identifiers() -> None:
    source = "int while int2 whilex _int my_var"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 0
    expected = [
        (TokenType.KW_INT, "int"),
        (TokenType.KW_WHILE, "while"),
        (TokenType.IDENTIFIER, "int2"),
        (TokenType.IDENTIFIER, "whilex"),
        (TokenType.IDENTIFIER, "_int"),
        (TokenType.IDENTIFIER, "my_var"),
        (TokenType.EOF, ""),
    ]
    assert [(t.type, t.lexeme) for t in tokens] == expected


def test_number_followed_by_letters() -> None:
    source = "12abc"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 0
    assert len(tokens) == 3
    assert tokens[0].type == TokenType.INTEGER_LITERAL
    assert tokens[0].lexeme == "12"
    assert tokens[0].literal == 12
    assert tokens[0].line == 1
    assert tokens[0].column == 1
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "abc"
    assert tokens[1].line == 1
    assert tokens[1].column == 3


def test_negative_number_splits_into_minus_and_literal() -> None:
    source = "-5"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 0
    assert len(tokens) == 3
    assert tokens[0].type == TokenType.MINUS
    assert tokens[0].lexeme == "-"
    assert tokens[1].type == TokenType.INTEGER_LITERAL
    assert tokens[1].lexeme == "5"
    assert tokens[1].literal == 5


def test_skill_section_7_valid_case() -> None:
    source = "int2 = 12abc;\nwhilex == -5"
    tokens, diagnostics = Lexer(source).scan()
    assert len(diagnostics) == 0

    expected_output = [
        "IDENTIFIER 'int2' 1 1",
        "ASSIGN '=' 1 6",
        "INTEGER_LITERAL '12' 1 8",
        "IDENTIFIER 'abc' 1 10",
        "SEMICOLON ';' 1 13",
        "IDENTIFIER 'whilex' 2 1",
        "EQUAL_EQUAL '==' 2 8",
        "MINUS '-' 2 11",
        "INTEGER_LITERAL '5' 2 12",
        "EOF '' 2 13",
    ]
    actual_output = [format_token(t) for t in tokens]
    assert actual_output == expected_output


def test_skill_section_7_errors_case() -> None:
    source = "int x = @;\nx ! = 0; // fin"
    tokens, diagnostics = Lexer(source).scan()

    expected_tokens = [
        "KW_INT 'int' 1 1",
        "IDENTIFIER 'x' 1 5",
        "ASSIGN '=' 1 7",
        "SEMICOLON ';' 1 10",
        "IDENTIFIER 'x' 2 1",
        "ASSIGN '=' 2 5",
        "INTEGER_LITERAL '0' 2 7",
        "SEMICOLON ';' 2 8",
        "IDENTIFIER 'fin' 2 13",
        "EOF '' 2 16",
    ]
    expected_diagnostics = [
        "LEX001 error 1:9 Carácter no reconocido: '@'",
        "LEX001 error 2:3 Carácter no reconocido: '!'",
        "LEX001 error 2:10 Carácter no reconocido: '/'",
        "LEX001 error 2:11 Carácter no reconocido: '/'",
    ]

    actual_tokens = [format_token(t) for t in tokens]
    actual_diagnostics = [format_diagnostic(d) for d in diagnostics]

    assert actual_tokens == expected_tokens
    assert actual_diagnostics == expected_diagnostics
