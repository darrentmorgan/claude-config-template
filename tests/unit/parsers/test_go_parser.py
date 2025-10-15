"""Unit tests for Go parser.

Following TDD principles:
1. Write tests FIRST
2. Verify tests FAIL
3. Implement code to pass tests
4. Refactor

Tests T035-T037: Go parser tests
Implementation T042: Go parser implementation
"""

import pytest
from pathlib import Path

from code_graph.indexer.parsers.go_parser import GoParser
from code_graph.models.nodes.file_node import FileNode, ParseStatus
from code_graph.models.nodes.function_node import FunctionNode
from code_graph.models.edges.base_edge import EdgeType


class TestGoParserBasic:
    """Test basic Go parser functionality."""

    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        return GoParser()

    def test_parser_initialization(self, parser):
        """Test parser initializes correctly."""
        assert parser is not None
        assert parser.language == "go"

    def test_parse_simple_function(self, parser, tmp_path):
        """Test parsing a simple function definition."""
        test_file = tmp_path / "simple.go"
        test_file.write_text("""package main

func greet() string {
    return "Hello, world!"
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert result.file_node.path == str(test_file)
        assert result.file_node.language == "go"
        assert result.file_node.parse_status == ParseStatus.SUCCESS
        assert len(result.functions) == 1

        func = result.functions[0]
        assert func.name == "greet"
        assert func.return_type == "string"
        assert len(func.parameters) == 0

    def test_parse_function_with_parameters(self, parser, tmp_path):
        """Test parsing function with parameters and multiple returns."""
        test_file = tmp_path / "params.go"
        test_file.write_text("""package main

func divide(a int, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 1

        func = result.functions[0]
        assert func.name == "divide"
        assert len(func.parameters) == 2
        assert func.parameters[0].name == "a"
        assert func.parameters[0].type_hint == "int"
        assert func.parameters[1].name == "b"
        assert func.parameters[1].type_hint == "int"
        # Go supports multiple returns - capture as tuple or array
        assert "int" in func.return_type
        assert "error" in func.return_type

    def test_parse_method_with_receiver(self, parser, tmp_path):
        """Test parsing method with receiver type."""
        test_file = tmp_path / "method.go"
        test_file.write_text("""package main

type Calculator struct {
    value int
}

func (c *Calculator) Add(n int) int {
    c.value += n
    return c.value
}

func (c Calculator) GetValue() int {
    return c.value
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 2

        # Methods should be captured
        add_method = next(f for f in result.functions if f.name == "Add")
        assert add_method.name == "Add"
        assert len(add_method.parameters) == 1
        assert add_method.parameters[0].name == "n"

        get_method = next(f for f in result.functions if f.name == "GetValue")
        assert get_method.name == "GetValue"

    def test_parse_struct_definition(self, parser, tmp_path):
        """Test parsing struct definitions."""
        test_file = tmp_path / "struct.go"
        test_file.write_text("""package main

type User struct {
    ID       int
    Name     string
    Email    string
    IsActive bool
}

type Admin struct {
    User
    Permissions []string
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.classes) == 2

        user = next(c for c in result.classes if c.name == "User")
        assert user.name == "User"

        admin = next(c for c in result.classes if c.name == "Admin")
        assert admin.name == "Admin"
        # Admin embeds User
        assert "User" in admin.base_classes

    def test_parse_interface(self, parser, tmp_path):
        """Test parsing interface definitions."""
        test_file = tmp_path / "interface.go"
        test_file.write_text("""package main

type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type ReadWriter interface {
    Reader
    Writer
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.classes) >= 3

        # ReadWriter should show composition of Reader and Writer
        rw = next(c for c in result.classes if c.name == "ReadWriter")
        assert rw.is_interface is True
        assert "Reader" in rw.base_classes or "Writer" in rw.base_classes

    def test_parse_imports(self, parser, tmp_path):
        """Test extracting import statements."""
        test_file = tmp_path / "imports.go"
        test_file.write_text("""package main

import (
    "fmt"
    "errors"
    "net/http"
    json "encoding/json"
    . "github.com/user/repo"
)
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.imports) >= 4

        import_modules = [imp.module for imp in result.imports]
        assert "fmt" in import_modules
        assert "errors" in import_modules
        assert "net/http" in import_modules


class TestGoParserAdvanced:
    """Test advanced parsing scenarios."""

    @pytest.fixture
    def parser(self):
        return GoParser()

    def test_parse_generic_functions(self, parser, tmp_path):
        """Test parsing functions with generics (Go 1.18+)."""
        test_file = tmp_path / "generics.go"
        test_file.write_text("""package main

func Map[T, U any](items []T, fn func(T) U) []U {
    result := make([]U, len(items))
    for i, item := range items {
        result[i] = fn(item)
    }
    return result
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 1

        map_func = result.functions[0]
        assert map_func.name == "Map"
        # Generic type parameters should be captured

    def test_parse_variadic_functions(self, parser, tmp_path):
        """Test parsing variadic functions."""
        test_file = tmp_path / "variadic.go"
        test_file.write_text("""package main

func sum(numbers ...int) int {
    total := 0
    for _, n := range numbers {
        total += n
    }
    return total
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 1

        sum_func = result.functions[0]
        assert sum_func.name == "sum"
        assert len(sum_func.parameters) == 1
        assert sum_func.parameters[0].name == "numbers"

    def test_parse_pointer_types(self, parser, tmp_path):
        """Test parsing pointer types."""
        test_file = tmp_path / "pointers.go"
        test_file.write_text("""package main

func updateValue(ptr *int, value int) {
    *ptr = value
}

func createUser(name string) *User {
    return &User{Name: name}
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 2

        update_func = next(f for f in result.functions if f.name == "updateValue")
        assert update_func.parameters[0].type_hint == "*int"

    def test_parse_named_return_values(self, parser, tmp_path):
        """Test parsing named return values."""
        test_file = tmp_path / "named_returns.go"
        test_file.write_text("""package main

func divide(a, b int) (result int, err error) {
    if b == 0 {
        err = errors.New("division by zero")
        return
    }
    result = a / b
    return
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.functions) == 1

        func = result.functions[0]
        assert func.name == "divide"
        assert "int" in func.return_type
        assert "error" in func.return_type

    def test_parse_struct_methods(self, parser, tmp_path):
        """Test parsing multiple methods on a struct."""
        test_file = tmp_path / "struct_methods.go"
        test_file.write_text("""package main

type Counter struct {
    count int
}

func (c *Counter) Increment() {
    c.count++
}

func (c *Counter) Decrement() {
    c.count--
}

func (c *Counter) Value() int {
    return c.count
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert len(result.classes) == 1
        assert len(result.functions) == 3

        counter = result.classes[0]
        assert counter.name == "Counter"


class TestGoParserErrorHandling:
    """Test parser error handling and partial parsing."""

    @pytest.fixture
    def parser(self):
        return GoParser()

    def test_parse_syntax_error_partial_success(self, parser, tmp_path):
        """Test parsing file with syntax errors."""
        test_file = tmp_path / "syntax_error.go"
        test_file.write_text("""package main

func validFunction() string {
    return "works"
}

func brokenFunction(
    // Missing closing parenthesis and body

func anotherValid() {
    fmt.Println("also works")
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
        """Test parsing an empty Go file."""
        test_file = tmp_path / "empty.go"
        test_file.write_text("package main\n")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert result.file_node.parse_status == ParseStatus.SUCCESS
        assert len(result.functions) == 0
        assert len(result.classes) == 0

    def test_parse_nonexistent_file(self, parser):
        """Test parsing a file that doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/path/that/does/not/exist.go")

    def test_parse_comments_only(self, parser, tmp_path):
        """Test parsing file with only comments."""
        test_file = tmp_path / "comments.go"
        test_file.write_text("""package main

// This is a comment
/* Block comment */
/*
 * Multi-line comment
 */
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True
        assert result.file_node.parse_status == ParseStatus.SUCCESS
        assert len(result.functions) == 0


class TestGoParserEdges:
    """Test edge extraction for relationships."""

    @pytest.fixture
    def parser(self):
        return GoParser()

    def test_extract_import_edges(self, parser, tmp_path):
        """Test extracting import relationships."""
        test_file = tmp_path / "imports.go"
        test_file.write_text("""package main

import (
    "fmt"
    "errors"
)
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True

        import_edges = [e for e in result.edges if e.type == EdgeType.IMPORTS]
        assert len(import_edges) >= 2

    def test_extract_embedding_edges(self, parser, tmp_path):
        """Test extracting struct embedding relationships."""
        test_file = tmp_path / "embedding.go"
        test_file.write_text("""package main

type Base struct {
    ID int
}

type Derived struct {
    Base
    Name string
}
""")

        result = parser.parse_file(str(test_file))

        assert result.success is True

        # Embedding should create inheritance-like edges
        inherit_edges = [e for e in result.edges if e.type == EdgeType.INHERITS]
        assert len(inherit_edges) >= 1


@pytest.mark.parametrize("code_snippet,expected_functions", [
    ("package main\n\nfunc simple() {}", 1),
    ("package main\n\nfunc f1() {}\nfunc f2() {}", 2),
    ("package main\n\ntype T struct{}\n\nfunc (t *T) method() {}", 1),
])
def test_function_counting(code_snippet, expected_functions, tmp_path):
    """Parametrized test for counting functions in various scenarios."""
    parser = GoParser()
    test_file = tmp_path / "test.go"
    test_file.write_text(code_snippet)

    result = parser.parse_file(str(test_file))

    assert result.success is True
    assert len(result.functions) == expected_functions
