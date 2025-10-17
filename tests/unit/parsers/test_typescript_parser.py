"""Unit tests for TypeScript parser.

Following TDD principles:
1. Write tests FIRST
2. Verify tests FAIL
3. Implement code to pass tests
4. Refactor

Tests T032-T034: TypeScript parser tests
Implementation T041: TypeScript parser implementation
"""

import pytest
from pathlib import Path

from code_graph.indexer.parsers.typescript_parser import TypeScriptParser
from code_graph.models.nodes.file_node import FileNode, ParseStatus
from code_graph.models.nodes.function_node import FunctionNode
from code_graph.models.edges.base_edge import EdgeType


class TestTypeScriptParserBasic:
    """Test basic TypeScript parser functionality."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return TypeScriptParser()

    def test_parser_initialization(self, parser):
        """Test parser initializes correctly."""
        assert parser is not None
        assert parser.language == "typescript"

    def test_parse_simple_function(self, parser, tmp_path):
        """Test parsing a simple function definition."""
        test_file = tmp_path / "simple.ts"
        test_file.write_text("""
function greet(): string {
    return "Hello, world!";
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert result.file_node.path == str(test_file)
        assert result.file_node.language == "typescript"
        assert result.file_node.parse_status == ParseStatus.SUCCESS
        assert len(result.functions) == 1

        func = result.functions[0]
        assert func.name == "greet"
        assert func.return_type == "string"
        assert len(func.parameters) == 0

    def test_parse_arrow_function(self, parser, tmp_path):
        """Test parsing arrow function expressions."""
        test_file = tmp_path / "arrow.ts"
        test_file.write_text("""
const add = (a: number, b: number): number => {
    return a + b;
};

const multiply = (x: number, y: number): number => x * y;
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 2

        add_func = result.functions[0]
        assert add_func.name == "add"
        assert len(add_func.parameters) == 2
        assert add_func.return_type == "number"

        mult_func = result.functions[1]
        assert mult_func.name == "multiply"
        assert len(mult_func.parameters) == 2

    def test_parse_function_with_types(self, parser, tmp_path):
        """Test parsing function with TypeScript type annotations."""
        test_file = tmp_path / "types.ts"
        test_file.write_text("""
function processUser(name: string, age: number, active: boolean = true): User {
    return { name, age, active };
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 1

        func = result.functions[0]
        assert func.name == "processUser"
        assert len(func.parameters) == 3
        assert func.parameters[0].name == "name"
        assert func.parameters[0].type_hint == "string"
        assert func.parameters[1].name == "age"
        assert func.parameters[1].type_hint == "number"
        assert func.parameters[2].name == "active"
        assert func.parameters[2].type_hint == "boolean"
        assert func.parameters[2].default_value == "true"
        assert func.return_type == "User"

    def test_parse_class_definition(self, parser, tmp_path):
        """Test parsing a class definition."""
        test_file = tmp_path / "class.ts"
        test_file.write_text("""
class Calculator {
    add(a: number, b: number): number {
        return a + b;
    }

    subtract(a: number, b: number): number {
        return a - b;
    }
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.classes) == 1

        cls = result.classes[0]
        assert cls.name == "Calculator"
        assert len(cls.methods) == 2
        assert "add" in [m.name for m in cls.methods]
        assert "subtract" in [m.name for m in cls.methods]

    def test_parse_interface(self, parser, tmp_path):
        """Test parsing interface definitions."""
        test_file = tmp_path / "interface.ts"
        test_file.write_text("""
interface User {
    id: number;
    name: string;
    email: string;
    isActive: boolean;
}

interface Admin extends User {
    permissions: string[];
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        # Interfaces should be captured as a special type
        assert len(result.classes) >= 2  # Treating interfaces as class-like structures

    def test_parse_imports(self, parser, tmp_path):
        """Test extracting import statements."""
        test_file = tmp_path / "imports.ts"
        test_file.write_text("""
import { useState, useEffect } from 'react';
import type { User } from './types';
import axios from 'axios';
import * as utils from './utils';
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.imports) >= 4

        import_modules = [imp.module for imp in result.imports]
        assert "react" in import_modules
        assert "./types" in import_modules or "types" in import_modules
        assert "axios" in import_modules


class TestTypeScriptParserAdvanced:
    """Test advanced parsing scenarios."""

    @pytest.fixture
    def parser(self):
        return TypeScriptParser()

    def test_parse_generic_functions(self, parser, tmp_path):
        """Test parsing functions with generics."""
        test_file = tmp_path / "generics.ts"
        test_file.write_text("""
function identity<T>(arg: T): T {
    return arg;
}

function map<T, U>(items: T[], fn: (item: T) => U): U[] {
    return items.map(fn);
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 2

        identity_func = result.functions[0]
        assert identity_func.name == "identity"
        # Generic type parameters should be captured

    def test_parse_class_inheritance(self, parser, tmp_path):
        """Test parsing class inheritance."""
        test_file = tmp_path / "inheritance.ts"
        test_file.write_text("""
class Animal {
    speak(): void {
        console.log("...");
    }
}

class Dog extends Animal {
    speak(): void {
        console.log("Woof!");
    }
}

class Cat extends Animal {
    speak(): void {
        console.log("Meow!");
    }
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.classes) == 3

        animal = next(c for c in result.classes if c.name == "Animal")
        assert animal.base_classes == []

        dog = next(c for c in result.classes if c.name == "Dog")
        assert "Animal" in dog.base_classes

        cat = next(c for c in result.classes if c.name == "Cat")
        assert "Animal" in cat.base_classes

    def test_parse_decorators(self, parser, tmp_path):
        """Test parsing decorators."""
        test_file = tmp_path / "decorators.ts"
        test_file.write_text("""
class UserService {
    @Get('/users')
    getUsers(): User[] {
        return [];
    }

    @Post('/users')
    @ValidateBody()
    createUser(user: User): User {
        return user;
    }
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.classes) == 1

        cls = result.classes[0]
        get_method = next(m for m in cls.methods if m.name == "getUsers")
        assert "Get" in get_method.decorators

        create_method = next(m for m in cls.methods if m.name == "createUser")
        assert "Post" in create_method.decorators
        assert "ValidateBody" in create_method.decorators

    def test_parse_async_functions(self, parser, tmp_path):
        """Test parsing async function definitions."""
        test_file = tmp_path / "async.ts"
        test_file.write_text("""
async function fetchData(url: string): Promise<Response> {
    const response = await fetch(url);
    return response;
}

const getData = async (): Promise<Data> => {
    return await fetchData('/api/data');
};
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 2

        fetch_func = result.functions[0]
        assert fetch_func.is_async is True
        assert "Promise" in fetch_func.return_type

        get_data = result.functions[1]
        assert get_data.is_async is True

    def test_parse_type_aliases(self, parser, tmp_path):
        """Test parsing type aliases."""
        test_file = tmp_path / "types.ts"
        test_file.write_text("""
type ID = string | number;
type UserRole = 'admin' | 'user' | 'guest';
type Callback = (error: Error | null, result: any) => void;
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        # Type aliases should be captured (implementation detail)


class TestTypeScriptParserErrorHandling:
    """Test parser error handling and partial parsing."""

    @pytest.fixture
    def parser(self):
        return TypeScriptParser()

    def test_parse_syntax_error_partial_success(self, parser, tmp_path):
        """Test parsing file with syntax errors."""
        test_file = tmp_path / "syntax_error.ts"
        test_file.write_text("""
function validFunction(): string {
    return "works";
}

function brokenFunction(
    // Missing closing parenthesis and body

function anotherValid(): void {
    console.log("also works");
}
""")

        result = parser.parse_file(str(test_file))

        # Tree-sitter should parse partially
        assert result.success is True
        assert result.file_node.parse_status == ParseStatus.PARTIAL
        assert result.file_node.error_count > 0

        # Should still capture valid functions
        assert len(result.functions) >= 2

    def test_parse_empty_file(self, parser, tmp_path):
        """Test parsing an empty TypeScript file."""
        test_file = tmp_path / "empty.ts"
        test_file.write_text("")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert result.file_node.parse_status == ParseStatus.SUCCESS
        assert len(result.functions) == 0
        assert len(result.classes) == 0

    def test_parse_nonexistent_file(self, parser):
        """Test parsing a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/path/that/does/not/exist.ts")

    def test_parse_comments_only(self, parser, tmp_path):
        """Test parsing file with only comments."""
        test_file = tmp_path / "comments.ts"
        test_file.write_text("""
// This is a comment
/* Block comment */
/**
 * JSDoc comment
 */
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert result.file_node.parse_status == ParseStatus.SUCCESS
        assert len(result.functions) == 0


class TestTypeScriptParserEdges:
    """Test edge extraction for relationships."""

    @pytest.fixture
    def parser(self):
        return TypeScriptParser()

    def test_extract_import_edges(self, parser, tmp_path):
        """Test extracting import relationships."""
        test_file = tmp_path / "imports.ts"
        test_file.write_text("""
import { Component } from 'react';
import type { User } from './types';
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True

        import_edges = [e for e in result.edges if e.type == EdgeType.IMPORTS]
        assert len(import_edges) >= 2

    def test_extract_inheritance_edges(self, parser, tmp_path):
        """Test extracting class inheritance relationships."""
        test_file = tmp_path / "inheritance.ts"
        test_file.write_text("""
class Base {
    value: number;
}

class Derived extends Base {
    name: string;
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True

        inherit_edges = [e for e in result.edges if e.type == EdgeType.INHERITS]
        assert len(inherit_edges) == 1

        inherit = inherit_edges[0]
        assert "Derived" in inherit.metadata["source_id"]
        assert "Base" in inherit.metadata["target_id"]


@pytest.mark.parametrize("code_snippet,expected_functions", [
    ("function simple() {}", 1),
    ("const arrow = () => {};", 1),
    ("function f1() {}\nfunction f2() {}", 2),
    ("class C { method() {} }", 1),  # Count method
])
def test_function_counting(code_snippet, expected_functions, tmp_path):
    """Parametrized test for counting functions in various scenarios."""
    parser = TypeScriptParser()
    test_file = tmp_path / "test.ts"
    test_file.write_text(code_snippet)

    result = parser.parse_file(str(test_file))

    assert result.success is True
    assert len(result.functions) == expected_functions
