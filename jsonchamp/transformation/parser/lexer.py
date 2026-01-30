"""
SchemaMap Lexer (Tokenizer)

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Tokenizes SchemaMap DSL source code into a stream of tokens.
"""

from __future__ import annotations
import re
from typing import Iterator, List, Optional, Any
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    """Token types for the SchemaMap lexer."""
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()
    COLON = auto()
    PIPE = auto()
    DOT = auto()
    COMMA = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    DOUBLE_QUESTION = auto()
    QUESTION = auto()
    AT = auto()
    TILDE = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    GREATER = auto()
    LESS = auto()
    GREATER_EQ = auto()
    LESS_EQ = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    LBRACE = auto()
    RBRACE = auto()
    LPAREN = auto()
    RPAREN = auto()
    # Directives
    CONFIG = auto()
    ALIASES = auto()
    LOOKUPS = auto()
    FUNCTIONS = auto()  # NEW: @functions block
    WHEN = auto()
    ELSE = auto()
    COMPUTE = auto()
    CALL = auto()       # NEW: @call directive
    EXPR = auto()
    NOW = auto()
    UUID = auto()
    CONSTANT = auto()
    REPEAT = auto()
    COLLECT = auto()
    FILTER = auto()
    FLATTEN = auto()
    NEWLINE = auto()
    COMMENT = auto()
    EOF = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """A single token from the lexer."""
    type: TokenType
    value: Any
    line: int
    column: int


class LexerError(Exception):
    """Exception raised for lexer errors."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Column {column}: {message}")


class SchemaMapLexer:
    """Lexer for the SchemaMap DSL."""
    
    KEYWORDS = {
        "true": (TokenType.BOOLEAN, True),
        "false": (TokenType.BOOLEAN, False),
        "null": (TokenType.NULL, None),
        "constant": (TokenType.CONSTANT, "constant"),
        "filter": (TokenType.FILTER, "filter"),
        "flatten": (TokenType.FLATTEN, "flatten"),
    }
    
    DIRECTIVES = {
        "@config": TokenType.CONFIG,
        "@aliases": TokenType.ALIASES,
        "@lookups": TokenType.LOOKUPS,
        "@functions": TokenType.FUNCTIONS,
        "@when": TokenType.WHEN,
        "@else": TokenType.ELSE,
        "@compute": TokenType.COMPUTE,
        "@call": TokenType.CALL,
        "@expr": TokenType.EXPR,
        "@now": TokenType.NOW,
        "@uuid": TokenType.UUID,
        "@repeat": TokenType.REPEAT,
        "@collect": TokenType.COLLECT,
    }
    
    TWO_CHAR_OPS = {
        "??": TokenType.DOUBLE_QUESTION,
        "==": TokenType.EQUALS,
        "!=": TokenType.NOT_EQUALS,
        ">=": TokenType.GREATER_EQ,
        "<=": TokenType.LESS_EQ,
    }
    
    SINGLE_CHAR_OPS = {
        ":": TokenType.COLON,
        "|": TokenType.PIPE,
        ".": TokenType.DOT,
        ",": TokenType.COMMA,
        "+": TokenType.PLUS,
        "-": TokenType.MINUS,
        "*": TokenType.STAR,
        "/": TokenType.SLASH,
        "?": TokenType.QUESTION,
        "@": TokenType.AT,
        "~": TokenType.TILDE,
        ">": TokenType.GREATER,
        "<": TokenType.LESS,
        "[": TokenType.LBRACKET,
        "]": TokenType.RBRACKET,
        "{": TokenType.LBRACE,
        "}": TokenType.RBRACE,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
    }
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source and return list of tokens."""
        self.tokens = []
        while self.pos < len(self.source):
            token = self._next_token()
            if token and token.type != TokenType.COMMENT:
                self.tokens.append(token)
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
    
    def _next_token(self) -> Optional[Token]:
        self._skip_whitespace()
        if self.pos >= len(self.source):
            return None
        
        start_line = self.line
        start_col = self.column
        char = self.source[self.pos]
        
        if char == "#":
            return self._read_comment(start_line, start_col)
        if char in ('"', "'"):
            return self._read_string(char, start_line, start_col)
        if char.isdigit() or (char == "-" and self._peek(1) and self._peek(1).isdigit()):
            return self._read_number(start_line, start_col)
        if char == "@":
            return self._read_directive(start_line, start_col)
        if char.isalpha() or char == "_":
            return self._read_identifier(start_line, start_col)
        
        two_char = self.source[self.pos:self.pos + 2]
        if two_char in self.TWO_CHAR_OPS:
            self._advance(2)
            return Token(self.TWO_CHAR_OPS[two_char], two_char, start_line, start_col)
        
        if char in self.SINGLE_CHAR_OPS:
            self._advance()
            return Token(self.SINGLE_CHAR_OPS[char], char, start_line, start_col)
        
        if char == "\n":
            self._advance()
            return Token(TokenType.NEWLINE, "\n", start_line, start_col)
        
        self._advance()
        return Token(TokenType.UNKNOWN, char, start_line, start_col)
    
    def _skip_whitespace(self) -> None:
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char in (" ", "\t", "\r"):
                self._advance()
            elif char == "\n":
                break
            else:
                break
    
    def _advance(self, count: int = 1) -> None:
        for _ in range(count):
            if self.pos < len(self.source):
                if self.source[self.pos] == "\n":
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
    
    def _peek(self, offset: int = 0) -> Optional[str]:
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def _read_comment(self, line: int, col: int) -> Token:
        start = self.pos
        while self.pos < len(self.source) and self.source[self.pos] != "\n":
            self._advance()
        return Token(TokenType.COMMENT, self.source[start:self.pos], line, col)
    
    def _read_string(self, quote: str, line: int, col: int) -> Token:
        self._advance()
        value = []
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char == quote:
                self._advance()
                return Token(TokenType.STRING, "".join(value), line, col)
            if char == "\\":
                self._advance()
                if self.pos < len(self.source):
                    escape_char = self.source[self.pos]
                    if escape_char == "n":
                        value.append("\n")
                    elif escape_char == "t":
                        value.append("\t")
                    elif escape_char == "\\":
                        value.append("\\")
                    elif escape_char == quote:
                        value.append(quote)
                    else:
                        value.append(escape_char)
                    self._advance()
            else:
                value.append(char)
                self._advance()
        raise LexerError(f"Unterminated string", line, col)
    
    def _read_number(self, line: int, col: int) -> Token:
        start = self.pos
        if self.source[self.pos] == "-":
            self._advance()
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self._advance()
        if self.pos < len(self.source) and self.source[self.pos] == ".":
            if self._peek(1) and self._peek(1).isdigit():
                self._advance()
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    self._advance()
        value_str = self.source[start:self.pos]
        if "." in value_str:
            value = float(value_str)
        else:
            value = int(value_str)
        return Token(TokenType.NUMBER, value, line, col)
    
    def _read_directive(self, line: int, col: int) -> Token:
        start = self.pos
        self._advance()
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == "_"):
            self._advance()
        directive = self.source[start:self.pos]
        if directive in self.DIRECTIVES:
            return Token(self.DIRECTIVES[directive], directive, line, col)
        # It's an alias reference
        self.pos = start + 1
        self.column = col + 1
        return Token(TokenType.AT, "@", line, col)
    
    def _read_identifier(self, line: int, col: int) -> Token:
        start = self.pos
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char.isalnum() or char == "_":
                self._advance()
            else:
                break
        value = self.source[start:self.pos]
        if value in self.KEYWORDS:
            token_type, token_value = self.KEYWORDS[value]
            return Token(token_type, token_value, line, col)
        return Token(TokenType.IDENTIFIER, value, line, col)
