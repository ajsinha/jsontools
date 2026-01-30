"""
SchemaMap Parser

Copyright (C) 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Parses SchemaMap DSL tokens into an Abstract Syntax Tree.
Supports @functions for external Python function registration and @call for invocation.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from .lexer import SchemaMapLexer, Token, TokenType, LexerError


class ParserError(Exception):
    """Exception raised for parser errors."""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Line {token.line}, Column {token.column}: {message}")
        else:
            super().__init__(message)


@dataclass
class SourcePath:
    """Represents a source path in a mapping."""
    segments: List[str]
    is_optional: bool = False
    array_access: Optional[str] = None

    def __str__(self) -> str:
        path = ".".join(self.segments)
        if self.array_access is not None:
            path += f"[{self.array_access}]"
        if self.is_optional:
            path += "?"
        return path


@dataclass
class TargetPath:
    """Represents a target path in a mapping."""
    segments: List[str]
    array_access: Optional[str] = None

    def __str__(self) -> str:
        path = ".".join(self.segments)
        if self.array_access is not None:
            path += f"[{self.array_access}]"
        return path


@dataclass
class Transform:
    """A single transformation function."""
    name: str
    args: List[Any] = field(default_factory=list)
    is_alias: bool = False


@dataclass
class TransformChain:
    """A chain of transformations."""
    transforms: List[Transform] = field(default_factory=list)


@dataclass
class MergeExpression:
    """Expression that merges multiple source paths."""
    parts: List[Union[SourcePath, str]]
    operator: str = "+"


@dataclass
class ComputeExpression:
    """A computed expression including external function calls."""
    expression: str
    type: str = "compute"  # "compute", "expr", "now", "uuid", "call"


@dataclass
class ConstantValue:
    """A constant value as source."""
    value: Any


@dataclass
class SkipTarget:
    """Target that indicates field should be skipped."""
    pass


@dataclass
class Condition:
    """A conditional expression."""
    field: str
    operator: str
    value: Any


@dataclass
class Mapping:
    """A single mapping rule."""
    source: Union[SourcePath, MergeExpression, ComputeExpression, ConstantValue]
    target: Union[TargetPath, SkipTarget]
    transforms: TransformChain = field(default_factory=TransformChain)
    line_number: int = 0


@dataclass
class NestedBlock:
    """A block of nested mappings."""
    base_path: Optional[SourcePath]
    target_prefix: Optional[TargetPath]
    mappings: List[Mapping] = field(default_factory=list)


@dataclass
class ConditionalBlock:
    """A @when/@else conditional block."""
    condition: Optional[Condition]
    mappings: List[Union[Mapping, NestedBlock]]


@dataclass
class AliasDefinition:
    """An alias definition."""
    name: str
    transforms: TransformChain
    parameters: List[str] = field(default_factory=list)


@dataclass
class LookupDefinition:
    """A lookup table definition."""
    name: str
    source: Union[str, Dict[str, Any]]


@dataclass
class FunctionDefinition:
    """An external function definition."""
    name: str
    spec: str  # Module:function or file path
    alias: Optional[str] = None


@dataclass
class MappingFile:
    """The root AST node."""
    config: Dict[str, Any] = field(default_factory=dict)
    aliases: Dict[str, AliasDefinition] = field(default_factory=dict)
    lookups: Dict[str, LookupDefinition] = field(default_factory=dict)
    functions: Dict[str, FunctionDefinition] = field(default_factory=dict)
    mappings: List[Union[Mapping, ConditionalBlock, NestedBlock]] = field(default_factory=list)
    source_file: Optional[str] = None


class SchemaMapParser:
    """Parser for the SchemaMap DSL."""
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.pos = 0
        self.current_token: Optional[Token] = None
    
    def parse(self, source: str, filename: str = None) -> MappingFile:
        """Parse SchemaMap source code into an AST."""
        lexer = SchemaMapLexer(source)
        self.tokens = lexer.tokenize()
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
        
        result = MappingFile(source_file=filename)
        
        while not self._is_at_end():
            self._skip_newlines()
            if self._is_at_end():
                break
            
            if self._check(TokenType.CONFIG):
                result.config = self._parse_config()
            elif self._check(TokenType.ALIASES):
                result.aliases = self._parse_aliases()
            elif self._check(TokenType.LOOKUPS):
                result.lookups = self._parse_lookups()
            elif self._check(TokenType.FUNCTIONS):
                result.functions = self._parse_functions()
            elif self._check(TokenType.WHEN):
                result.mappings.append(self._parse_conditional())
            elif self._check(TokenType.ELSE):
                result.mappings.append(self._parse_else_block())
            elif self._check(TokenType.LBRACE):
                result.mappings.append(self._parse_nested_block())
            elif self._check(TokenType.NEWLINE):
                self._advance()
            else:
                mapping = self._parse_mapping()
                if mapping:
                    result.mappings.append(mapping)
        
        return result
    
    def _is_at_end(self) -> bool:
        return self.current_token is None or self.current_token.type == TokenType.EOF
    
    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self.current_token.type == token_type
    
    def _advance(self) -> Optional[Token]:
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
        return token
    
    def _expect(self, token_type: TokenType, message: str = None) -> Token:
        if not self._check(token_type):
            msg = message or f"Expected {token_type.name}"
            raise ParserError(msg, self.current_token)
        return self._advance()
    
    def _skip_newlines(self) -> None:
        while self._check(TokenType.NEWLINE):
            self._advance()
    
    def _parse_config(self) -> Dict[str, Any]:
        """Parse @config block."""
        self._advance()
        self._expect(TokenType.LBRACE)
        config = {}
        
        self._skip_newlines()
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            name = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.COLON)
            value = self._parse_value()
            config[name] = value
            self._skip_newlines()
        
        self._expect(TokenType.RBRACE)
        return config
    
    def _parse_aliases(self) -> Dict[str, AliasDefinition]:
        """Parse @aliases block."""
        self._advance()
        self._expect(TokenType.LBRACE)
        aliases = {}
        
        self._skip_newlines()
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            name = self._expect(TokenType.IDENTIFIER).value
            params = []
            
            if self._check(TokenType.LPAREN):
                self._advance()
                while not self._check(TokenType.RPAREN):
                    params.append(self._expect(TokenType.IDENTIFIER).value)
                    if self._check(TokenType.COMMA):
                        self._advance()
                self._expect(TokenType.RPAREN)
            
            self._expect(TokenType.COLON)
            transforms = self._parse_transform_chain_direct()
            
            aliases[name] = AliasDefinition(name=name, transforms=transforms, parameters=params)
            self._skip_newlines()
        
        self._expect(TokenType.RBRACE)
        return aliases
    
    def _parse_lookups(self) -> Dict[str, LookupDefinition]:
        """Parse @lookups block."""
        self._advance()
        self._expect(TokenType.LBRACE)
        lookups = {}
        
        self._skip_newlines()
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            name = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.COLON)
            
            if self._check(TokenType.STRING):
                source = self._advance().value
            elif self._check(TokenType.LBRACE):
                source = self._parse_inline_dict()
            else:
                raise ParserError("Expected string or object for lookup", self.current_token)
            
            lookups[name] = LookupDefinition(name=name, source=source)
            self._skip_newlines()
        
        self._expect(TokenType.RBRACE)
        return lookups
    
    def _parse_functions(self) -> Dict[str, FunctionDefinition]:
        """
        Parse @functions block for external function registration.
        
        Syntax:
            @functions {
                func_name : "module.path:function_name"
                alias_name : "module.path:function_name as alias_name"
                from_file : "path/to/file.py:function_name"
            }
        """
        self._advance()
        self._expect(TokenType.LBRACE)
        functions = {}
        
        self._skip_newlines()
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            name = self._expect(TokenType.IDENTIFIER).value
            self._expect(TokenType.COLON)
            
            spec = self._expect(TokenType.STRING).value
            
            # Parse alias if present
            alias = None
            if " as " in spec:
                spec_parts = spec.split(" as ", 1)
                spec = spec_parts[0].strip()
                alias = spec_parts[1].strip()
            
            functions[name] = FunctionDefinition(name=name, spec=spec, alias=alias)
            self._skip_newlines()
        
        self._expect(TokenType.RBRACE)
        return functions
    
    def _parse_inline_dict(self) -> Dict[str, Any]:
        """Parse an inline dictionary."""
        self._expect(TokenType.LBRACE)
        result = {}
        
        self._skip_newlines()
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            key = self._parse_value()
            self._expect(TokenType.COLON)
            value = self._parse_value()
            result[str(key)] = value
            
            if self._check(TokenType.COMMA):
                self._advance()
            self._skip_newlines()
        
        self._expect(TokenType.RBRACE)
        return result
    
    def _parse_value(self) -> Any:
        """Parse a literal value."""
        if self._check(TokenType.STRING):
            return self._advance().value
        elif self._check(TokenType.NUMBER):
            return self._advance().value
        elif self._check(TokenType.BOOLEAN):
            return self._advance().value
        elif self._check(TokenType.NULL):
            self._advance()
            return None
        elif self._check(TokenType.IDENTIFIER):
            return self._advance().value
        elif self._check(TokenType.AT):
            self._advance()
            if self._check(TokenType.IDENTIFIER):
                return "@" + self._advance().value
            return "@"
        elif self._check(TokenType.LBRACE):
            return self._parse_inline_dict()
        elif self._check(TokenType.LBRACKET):
            return self._parse_inline_array()
        else:
            raise ParserError("Expected value", self.current_token)
    
    def _parse_inline_array(self) -> List[Any]:
        """Parse an inline array."""
        self._expect(TokenType.LBRACKET)
        result = []
        
        while not self._check(TokenType.RBRACKET) and not self._is_at_end():
            result.append(self._parse_value())
            if self._check(TokenType.COMMA):
                self._advance()
        
        self._expect(TokenType.RBRACKET)
        return result
    
    def _parse_mapping(self) -> Optional[Mapping]:
        """Parse a single mapping rule."""
        line_num = self.current_token.line if self.current_token else 0
        
        source = self._parse_source()
        if source is None:
            return None
        
        self._expect(TokenType.COLON, "Expected ':' in mapping")
        
        target = self._parse_target()
        
        transforms = TransformChain()
        if self._check(TokenType.PIPE):
            transforms = self._parse_transform_chain()
        
        return Mapping(source=source, target=target, transforms=transforms, line_number=line_num)
    
    def _parse_source(self) -> Optional[Union[SourcePath, MergeExpression, ComputeExpression, ConstantValue]]:
        """Parse the source side of a mapping."""
        # @compute(expression)
        if self._check(TokenType.COMPUTE):
            self._advance()
            self._expect(TokenType.LPAREN)
            expr = self._parse_expression_content()
            self._expect(TokenType.RPAREN)
            return ComputeExpression(expression=expr, type="compute")
        
        # @call(func_name, arg1, arg2, ...)
        if self._check(TokenType.CALL):
            self._advance()
            self._expect(TokenType.LPAREN)
            expr = self._parse_expression_content()
            self._expect(TokenType.RPAREN)
            return ComputeExpression(expression=expr, type="call")
        
        # @expr(expression)
        if self._check(TokenType.EXPR):
            self._advance()
            self._expect(TokenType.LPAREN)
            expr = self._parse_expression_content()
            self._expect(TokenType.RPAREN)
            return ComputeExpression(expression=expr, type="expr")
        
        # @now
        if self._check(TokenType.NOW):
            self._advance()
            return ComputeExpression(expression="", type="now")
        
        # @uuid
        if self._check(TokenType.UUID):
            self._advance()
            return ComputeExpression(expression="", type="uuid")
        
        # String constant
        if self._check(TokenType.STRING):
            return ConstantValue(value=self._advance().value)
        
        # Number constant
        if self._check(TokenType.NUMBER):
            return ConstantValue(value=self._advance().value)
        
        # Path or merge expression
        if self._check(TokenType.IDENTIFIER) or self._check(TokenType.DOT):
            path = self._parse_path()
            
            if self._check(TokenType.PLUS):
                return self._parse_merge_expression(path, "+")
            elif self._check(TokenType.DOUBLE_QUESTION):
                return self._parse_merge_expression(path, "??")
            
            return path
        
        return None
    
    def _parse_path(self) -> SourcePath:
        """Parse a dotted path with optional array notation anywhere."""
        segments = []
        is_optional = False
        array_access = None
        
        if self._check(TokenType.DOT):
            self._advance()
            segments.append("")
        
        # Parse first segment
        if self._check(TokenType.IDENTIFIER):
            segments.append(self._advance().value)
        
        # Continue parsing segments and array accesses
        while True:
            # Check for array access [*] or [0]
            if self._check(TokenType.LBRACKET):
                self._advance()
                if self._check(TokenType.STAR):
                    # Append [*] to last segment
                    if segments:
                        segments[-1] = segments[-1] + "[*]"
                    self._advance()
                elif self._check(TokenType.NUMBER):
                    idx = str(self._advance().value)
                    if segments:
                        segments[-1] = segments[-1] + f"[{idx}]"
                elif self._check(TokenType.MINUS):
                    self._advance()
                    num = self._expect(TokenType.NUMBER).value
                    if segments:
                        segments[-1] = segments[-1] + f"[-{num}]"
                self._expect(TokenType.RBRACKET)
            
            # Check for dot continuation
            if self._check(TokenType.DOT):
                self._advance()
                if self._check(TokenType.IDENTIFIER):
                    segments.append(self._advance().value)
                elif self._check(TokenType.STAR):
                    segments.append("*")
                    self._advance()
                else:
                    break
            else:
                break
        
        # Check for optional marker
        if self._check(TokenType.QUESTION):
            self._advance()
            is_optional = True
        
        return SourcePath(segments=segments, is_optional=is_optional, array_access=array_access)
    
    def _parse_merge_expression(self, first_path: SourcePath, operator: str) -> MergeExpression:
        """Parse a merge expression."""
        parts = [first_path]
        
        while self._check(TokenType.PLUS) or self._check(TokenType.DOUBLE_QUESTION):
            self._advance()
            
            if self._check(TokenType.STRING):
                parts.append(self._advance().value)
            elif self._check(TokenType.IDENTIFIER) or self._check(TokenType.DOT):
                parts.append(self._parse_path())
            else:
                raise ParserError("Expected path or string", self.current_token)
        
        return MergeExpression(parts=parts, operator=operator)
    
    def _parse_target(self) -> Union[TargetPath, SkipTarget]:
        """Parse the target side of a mapping with optional array notation."""
        if self._check(TokenType.TILDE):
            self._advance()
            return SkipTarget()
        
        segments = []
        array_access = None
        
        # Parse first segment
        if self._check(TokenType.IDENTIFIER):
            segments.append(self._advance().value)
        
        # Continue parsing segments and array accesses
        while True:
            # Check for array access [*] or [0]
            if self._check(TokenType.LBRACKET):
                self._advance()
                if self._check(TokenType.STAR):
                    if segments:
                        segments[-1] = segments[-1] + "[*]"
                    self._advance()
                elif self._check(TokenType.NUMBER):
                    idx = str(self._advance().value)
                    if segments:
                        segments[-1] = segments[-1] + f"[{idx}]"
                self._expect(TokenType.RBRACKET)
            
            # Check for dot continuation
            if self._check(TokenType.DOT):
                self._advance()
                if self._check(TokenType.IDENTIFIER):
                    segments.append(self._advance().value)
                else:
                    break
            else:
                break
        
        return TargetPath(segments=segments, array_access=array_access)
    
    def _parse_transform_chain(self) -> TransformChain:
        """Parse transforms after a mapping (starting with |)."""
        transforms = []
        
        while self._check(TokenType.PIPE):
            self._advance()
            transform = self._parse_transform()
            if transform:
                transforms.append(transform)
        
        return TransformChain(transforms=transforms)
    
    def _parse_transform_chain_direct(self) -> TransformChain:
        """Parse transforms directly (for aliases, no leading |)."""
        transforms = []
        
        transform = self._parse_transform()
        if transform:
            transforms.append(transform)
        
        while self._check(TokenType.PIPE):
            self._advance()
            transform = self._parse_transform()
            if transform:
                transforms.append(transform)
        
        return TransformChain(transforms=transforms)
    
    def _parse_transform(self) -> Optional[Transform]:
        """Parse a single transform."""
        is_alias = False
        
        if self._check(TokenType.AT):
            self._advance()
            is_alias = True
        
        if not self._check(TokenType.IDENTIFIER) and not self._check(TokenType.CONSTANT):
            return None
        
        name = self._advance().value
        args = []
        
        if self._check(TokenType.LPAREN):
            self._advance()
            while not self._check(TokenType.RPAREN) and not self._is_at_end():
                if self._check(TokenType.AT):
                    self._advance()
                    if self._check(TokenType.IDENTIFIER):
                        args.append("@" + self._advance().value)
                    else:
                        args.append("@")
                else:
                    args.append(self._parse_value())
                if self._check(TokenType.COMMA):
                    self._advance()
            self._expect(TokenType.RPAREN)
        
        return Transform(name=name, args=args, is_alias=is_alias)
    
    def _parse_expression_content(self) -> str:
        """Parse content inside @compute() or @call()."""
        content = []
        paren_depth = 1
        
        while paren_depth > 0 and not self._is_at_end():
            if self._check(TokenType.LPAREN):
                paren_depth += 1
                content.append("(")
                self._advance()
            elif self._check(TokenType.RPAREN):
                paren_depth -= 1
                if paren_depth > 0:
                    content.append(")")
                    self._advance()
            else:
                token = self._advance()
                if token.type == TokenType.STRING:
                    content.append(f'"{token.value}"')
                elif token.type == TokenType.DOT:
                    content.append(".")
                elif token.type == TokenType.LBRACKET:
                    content.append("[")
                elif token.type == TokenType.RBRACKET:
                    content.append("]")
                elif token.type == TokenType.STAR:
                    content.append("*")
                elif token.type == TokenType.COMMA:
                    content.append(",")
                else:
                    content.append(str(token.value))
        
        return "".join(content)
    
    def _parse_conditional(self) -> ConditionalBlock:
        """Parse a @when block."""
        self._advance()
        
        field = self._expect(TokenType.IDENTIFIER).value
        
        if self._check(TokenType.EQUALS):
            operator = "=="
            self._advance()
        elif self._check(TokenType.NOT_EQUALS):
            operator = "!="
            self._advance()
        elif self._check(TokenType.GREATER):
            operator = ">"
            self._advance()
        elif self._check(TokenType.LESS):
            operator = "<"
            self._advance()
        else:
            operator = "=="
        
        value = self._parse_value()
        condition = Condition(field=field, operator=operator, value=value)
        
        self._expect(TokenType.LBRACE)
        mappings = self._parse_block_mappings()
        self._expect(TokenType.RBRACE)
        
        return ConditionalBlock(condition=condition, mappings=mappings)
    
    def _parse_else_block(self) -> ConditionalBlock:
        """Parse an @else block."""
        self._advance()
        self._expect(TokenType.LBRACE)
        mappings = self._parse_block_mappings()
        self._expect(TokenType.RBRACE)
        
        return ConditionalBlock(condition=None, mappings=mappings)
    
    def _parse_nested_block(self) -> NestedBlock:
        """Parse a nested block."""
        self._expect(TokenType.LBRACE)
        mappings = self._parse_block_mappings()
        self._expect(TokenType.RBRACE)
        
        return NestedBlock(base_path=None, target_prefix=None, mappings=mappings)
    
    def _parse_block_mappings(self) -> List[Mapping]:
        """Parse mappings inside a block."""
        mappings = []
        self._skip_newlines()
        
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            mapping = self._parse_mapping()
            if mapping:
                mappings.append(mapping)
            self._skip_newlines()
        
        return mappings
