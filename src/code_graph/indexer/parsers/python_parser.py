"""Python parser using tree-sitter.

Implements T040: Python parser with full language support.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from tree_sitter import Language, Parser, Node
from tree_sitter_language_pack import get_language, get_parser

from code_graph.indexer.parsers.base import BaseParser, ParserResult
from code_graph.models.nodes.file_node import FileNode, ParseStatus
from code_graph.models.nodes.function_node import FunctionNode, Parameter
from code_graph.models.edges.base_edge import BaseEdge, EdgeType


class ImportInfo:
    """Represents an import statement."""

    def __init__(self, module: str, names: list[str], is_from: bool = False):
        self.module = module
        self.names = names
        self.is_from = is_from


class ClassInfo:
    """Represents a class definition."""

    def __init__(self, name: str, base_classes: list[str], methods: list[FunctionNode]):
        self.name = name
        self.base_classes = base_classes
        self.methods = methods


class PythonParser(BaseParser):
    """Parser for Python source code using tree-sitter."""

    def __init__(self):
        """Initialize Python parser."""
        super().__init__("python")

        # Get Python language and parser from tree-sitter-language-pack
        self._language = get_language("python")
        self._parser = get_parser("python")

    def parse_file(self, file_path: str, content: str | None = None) -> ParserResult:
        """Parse a Python source file.

        Args:
            file_path: Path to the Python file
            content: Optional file content (if None, reads from file_path)

        Returns:
            ParserResult with extracted structure

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        # Read file content if not provided
        if content is None:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            content = path.read_text(encoding="utf-8")

        # Parse with tree-sitter
        tree = self._parser.parse(bytes(content, "utf8"))
        root_node = tree.root_node

        # Analyze parse status
        parse_status, error_count = self.handle_parse_errors(tree)

        # Calculate file hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # Create FileNode
        file_node = FileNode(
            id=content_hash[:16],
            path=str(file_path),
            language="python",
            content_hash=content_hash,
            size_bytes=len(content.encode("utf-8")),
            parse_status=parse_status,
            error_count=error_count,
            last_indexed=datetime.now(),
        )

        # Extract structure
        imports = self.extract_imports(root_node)
        classes = self.extract_classes(root_node, "")
        functions = self.extract_functions(root_node, "")

        # Extract edges (relationships)
        edges = self._extract_edges(root_node, file_node.id, functions, classes)

        # Create result with all fields
        return ParserResult(
            file_node=file_node,
            modules=[],
            classes=classes,
            functions=functions,
            imports=imports,  # ImportInfo objects
            errors=[],
            edges=edges,
            success=parse_status != ParseStatus.FAILED,
        )

    def extract_imports(self, tree: Node) -> list[ImportInfo]:
        """Extract import statements from Python AST.

        Args:
            tree: Tree-sitter syntax tree root node

        Returns:
            List of ImportInfo objects
        """
        imports = []

        # Query for import statements
        for node in tree.children:
            if node.type == "import_statement":
                # import module1, module2
                for child in node.children:
                    if child.type == "dotted_name":
                        module_name = self._get_node_text(child)
                        imports.append(ImportInfo(module_name, [module_name], False))

            elif node.type == "import_from_statement":
                # from module import name1, name2
                module_name = None
                imported_names = []
                found_import_keyword = False

                for child in node.children:
                    if child.type == "dotted_name" and not found_import_keyword:
                        # This is the module being imported FROM
                        module_name = self._get_node_text(child)
                    elif child.type == "relative_import":
                        module_name = self._get_node_text(child)
                    elif child.type == "import":
                        found_import_keyword = True
                    elif found_import_keyword:
                        # After "import" keyword, collect imported names
                        if child.type in ["dotted_name", "identifier"]:
                            name_text = self._get_node_text(child)
                            if name_text and name_text not in ["import", "from", ",", "(", ")"]:
                                imported_names.append(name_text)
                        elif child.type == "aliased_import":
                            # Get the name being imported (before "as")
                            for aliased_child in child.children:
                                if aliased_child.type in ["dotted_name", "identifier"]:
                                    name_text = self._get_node_text(aliased_child)
                                    if name_text and name_text != "as":
                                        imported_names.append(name_text)
                                        break

                if module_name:
                    imports.append(ImportInfo(module_name, imported_names, True))

        return imports

    def extract_functions(self, tree: Node, parent_path: str) -> list[FunctionNode]:
        """Extract function definitions from Python AST.

        Args:
            tree: Tree-sitter syntax tree node
            parent_path: Qualified name of parent (for methods)

        Returns:
            List of FunctionNode instances
        """
        functions = []

        for node in self._walk_tree(tree):
            if node.type == "function_definition":
                func_info = self._extract_function_info(node, parent_path)
                if func_info:
                    functions.append(func_info)

        return functions

    def extract_classes(self, tree: Node, parent_path: str) -> list[ClassInfo]:
        """Extract class definitions from Python AST.

        Args:
            tree: Tree-sitter syntax tree node
            parent_path: Qualified name of parent module

        Returns:
            List of ClassInfo instances
        """
        classes = []

        for node in tree.children:
            if node.type == "class_definition":
                class_info = self._extract_class_info(node, parent_path)
                if class_info:
                    classes.append(class_info)

        return classes

    def handle_parse_errors(self, tree: Any) -> tuple[ParseStatus, int]:
        """Analyze tree for parse errors.

        Args:
            tree: Tree-sitter parse tree

        Returns:
            Tuple of (parse_status, error_count)
        """
        root_node = tree.root_node
        error_count = self._count_errors(root_node)

        if error_count == 0:
            return ParseStatus.SUCCESS, 0
        elif root_node.has_error:
            # Has errors but got some structure
            return ParseStatus.PARTIAL, error_count
        else:
            return ParseStatus.FAILED, error_count

    # Helper methods

    def _extract_function_info(self, node: Node, parent_path: str) -> FunctionNode | None:
        """Extract information about a function definition."""
        func_name = None
        parameters = []
        return_type = None
        decorators = []
        is_async = False

        # Check for async (it's a child of function_definition)
        for child in node.children:
            if child.type == "async":
                is_async = True
                break

        # Get function name
        for child in node.children:
            if child.type == "identifier":
                func_name = self._get_node_text(child)
                break

        if not func_name:
            return None

        # Get parameters
        for child in node.children:
            if child.type == "parameters":
                parameters = self._extract_parameters(child)
                break

        # Get return type
        for child in node.children:
            if child.type == "type":
                return_type = self._get_node_text(child)
                break

        # Get decorators (check previous siblings)
        current = node.prev_sibling
        while current:
            if current.type == "decorator":
                decorator_name = self._get_node_text(current).lstrip("@")
                decorators.insert(0, decorator_name)
            current = current.prev_sibling

        # Build qualified name
        qualified_name = f"{parent_path}.{func_name}" if parent_path else func_name

        # Build signature
        param_str = ", ".join([p.name for p in parameters])
        signature = f"def {func_name}({param_str}):"

        # Create function node
        line_start = node.start_point[0] + 1
        line_end = node.end_point[0] + 1

        return FunctionNode(
            id=hashlib.md5(qualified_name.encode()).hexdigest()[:16],
            name=func_name,
            qualified_name=qualified_name,
            signature=signature,
            parameters=parameters,
            return_type=return_type,
            decorators=decorators,
            line_start=line_start,
            line_end=line_end,
            is_async=is_async,
            docstring=self._extract_docstring(node),
        )

    def _extract_parameters(self, params_node: Node) -> list[Parameter]:
        """Extract function parameters."""
        parameters = []

        for child in params_node.children:
            if child.type == "identifier":
                param_name = self._get_node_text(child)
                if param_name and param_name != "self":  # Skip 'self' parameter
                    parameters.append(Parameter(
                        name=param_name,
                        type_hint=None,
                        default_value=None,
                        is_optional=False
                    ))

            elif child.type == "typed_parameter":
                param_name = None
                param_type = None

                for param_child in child.children:
                    if param_child.type == "identifier":
                        param_name = self._get_node_text(param_child)
                    elif param_child.type == "type":
                        # Get the type identifier
                        for type_child in param_child.children:
                            if type_child.type == "identifier":
                                param_type = self._get_node_text(type_child)
                                break

                if param_name and param_name != "self":
                    parameters.append(Parameter(
                        name=param_name,
                        type_hint=param_type,
                        default_value=None,
                        is_optional=False
                    ))

            elif child.type == "typed_default_parameter":
                # Parameter with both type hint and default value (e.g., age: int = 25)
                param_name = None
                param_type = None
                default_value = None

                for param_child in child.children:
                    if param_child.type == "identifier":
                        param_name = self._get_node_text(param_child)
                    elif param_child.type == "type":
                        # Get the type identifier
                        for type_child in param_child.children:
                            if type_child.type == "identifier":
                                param_type = self._get_node_text(type_child)
                                break
                    elif param_child.type in ["integer", "string", "float", "true", "false", "none"]:
                        default_value = self._get_node_text(param_child)

                if param_name and param_name != "self":
                    parameters.append(Parameter(
                        name=param_name,
                        type_hint=param_type,
                        default_value=default_value,
                        is_optional=True
                    ))

            elif child.type == "default_parameter":
                # Parameter with default but no type hint (e.g., age = 25)
                param_name = None
                default_value = None

                for param_child in child.children:
                    if param_child.type == "identifier":
                        param_name = self._get_node_text(param_child)
                    elif param_child.type in ["integer", "string", "float", "true", "false", "none"]:
                        default_value = self._get_node_text(param_child)

                if param_name and param_name != "self":
                    parameters.append(Parameter(
                        name=param_name,
                        type_hint=None,
                        default_value=default_value,
                        is_optional=True
                    ))

        return parameters

    def _extract_class_info(self, node: Node, parent_path: str) -> ClassInfo | None:
        """Extract information about a class definition."""
        class_name = None
        base_classes = []
        methods = []

        # Get class name
        for child in node.children:
            if child.type == "identifier":
                class_name = self._get_node_text(child)
                break

        if not class_name:
            return None

        # Get base classes
        for child in node.children:
            if child.type == "argument_list":
                for arg_child in child.children:
                    if arg_child.type == "identifier":
                        base_classes.append(self._get_node_text(arg_child))

        # Get methods from class body
        for child in node.children:
            if child.type == "block":
                class_path = f"{parent_path}.{class_name}" if parent_path else class_name
                methods = self.extract_functions(child, class_path)
                break

        return ClassInfo(class_name, base_classes, methods)

    def _extract_edges(
        self,
        tree: Node,
        file_id: str,
        functions: list[FunctionNode],
        classes: list[ClassInfo]
    ) -> list[BaseEdge]:
        """Extract relationship edges from the parse tree."""
        edges = []

        # IMPORTS edges (from imports)
        for node in tree.children:
            if node.type in ["import_statement", "import_from_statement"]:
                # Create IMPORTS edge
                edges.append(BaseEdge(
                    type=EdgeType.IMPORTS,
                    confidence=1.0,
                    metadata={
                        "source_id": file_id,
                        "target_id": "module_" + self._get_node_text(node),
                    }
                ))

        # CALLS edges (function calls)
        for func in functions:
            # Find call expressions in function body
            # This is a simplified version - full implementation would walk the function body
            pass

        # INHERITS edges (class inheritance)
        for cls in classes:
            for base in cls.base_classes:
                edges.append(BaseEdge(
                    type=EdgeType.INHERITS,
                    confidence=1.0,
                    metadata={
                        "source_id": cls.name,
                        "target_id": base,
                    }
                ))

        return edges

    def _extract_docstring(self, node: Node) -> str | None:
        """Extract docstring from function or class."""
        for child in node.children:
            if child.type == "block":
                for block_child in child.children:
                    if block_child.type == "expression_statement":
                        for expr_child in block_child.children:
                            if expr_child.type == "string":
                                return self._get_node_text(expr_child).strip('"""').strip("'''")
        return None

    def _get_node_text(self, node: Node) -> str:
        """Get text content of a node."""
        return node.text.decode("utf8") if node.text else ""

    def _count_errors(self, node: Node) -> int:
        """Count error nodes in tree."""
        count = 0
        if node.type == "ERROR" or node.is_missing:
            count += 1
        for child in node.children:
            count += self._count_errors(child)
        return count

    def _walk_tree(self, node: Node) -> list[Node]:
        """Walk tree and collect all nodes."""
        nodes = [node]
        for child in node.children:
            nodes.extend(self._walk_tree(child))
        return nodes
