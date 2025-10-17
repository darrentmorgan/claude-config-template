"""Go parser using tree-sitter.

Implements T042: Go parser with full language support.
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

    def __init__(self, module: str, names: list[str], alias: str | None = None):
        self.module = module
        self.names = names
        self.alias = alias


class ClassInfo:
    """Represents a struct or interface definition."""

    def __init__(self, name: str, base_classes: list[str], methods: list[FunctionNode], is_interface: bool = False):
        self.name = name
        self.base_classes = base_classes
        self.methods = methods
        self.is_interface = is_interface


class GoParser(BaseParser):
    """Parser for Go source code using tree-sitter."""

    def __init__(self):
        """Initialize Go parser."""
        super().__init__("go")

        # Get Go language and parser from tree-sitter-language-pack
        self._language = get_language("go")
        self._parser = get_parser("go")

    def parse_file(self, file_path: str, content: str | None = None) -> ParserResult:
        """Parse a Go source file.

        Args:
            file_path: Path to the Go file
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
            language="go",
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
            imports=imports,
            errors=[],
            edges=edges,
            success=parse_status != ParseStatus.FAILED,
        )

    def extract_imports(self, tree: Node) -> list[ImportInfo]:
        """Extract import statements from Go AST.

        Args:
            tree: Tree-sitter syntax tree root node

        Returns:
            List of ImportInfo objects
        """
        imports = []

        for node in self._walk_tree(tree):
            if node.type == "import_declaration":
                # Single import: import "fmt"
                # import ( ... ) group handled by import_spec children
                for child in node.children:
                    if child.type == "import_spec":
                        import_info = self._extract_import_spec(child)
                        if import_info:
                            imports.append(import_info)
                    elif child.type == "import_spec_list":
                        # Grouped imports
                        for spec in child.children:
                            if spec.type == "import_spec":
                                import_info = self._extract_import_spec(spec)
                                if import_info:
                                    imports.append(import_info)

        return imports

    def _extract_import_spec(self, node: Node) -> ImportInfo | None:
        """Extract information from an import_spec node."""
        module_path = None
        alias = None

        for child in node.children:
            if child.type == "interpreted_string_literal":
                # Remove quotes from import path
                module_path = self._get_node_text(child).strip('"')
            elif child.type == "package_identifier":
                # Aliased import: alias "path"
                alias = self._get_node_text(child)
            elif child.type == "dot":
                # Dot import: . "path"
                alias = "."

        if module_path:
            return ImportInfo(module_path, [], alias)

        return None

    def extract_functions(self, tree: Node, parent_path: str) -> list[FunctionNode]:
        """Extract function definitions from Go AST.

        Args:
            tree: Tree-sitter syntax tree node
            parent_path: Qualified name of parent (for methods)

        Returns:
            List of FunctionNode instances
        """
        functions = []

        for node in self._walk_tree(tree):
            if node.type == "function_declaration":
                func_info = self._extract_function_info(node, parent_path)
                if func_info:
                    functions.append(func_info)
            elif node.type == "method_declaration":
                func_info = self._extract_method_info(node, parent_path)
                if func_info:
                    functions.append(func_info)

        return functions

    def extract_classes(self, tree: Node, parent_path: str) -> list[ClassInfo]:
        """Extract struct and interface definitions from Go AST.

        Args:
            tree: Tree-sitter syntax tree node
            parent_path: Qualified name of parent module

        Returns:
            List of ClassInfo instances
        """
        classes = []

        for node in self._walk_tree(tree):
            if node.type == "type_declaration":
                # type X struct { ... } or type X interface { ... }
                for child in node.children:
                    if child.type == "type_spec":
                        class_info = self._extract_type_spec(child, parent_path)
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
            return ParseStatus.PARTIAL, error_count
        else:
            return ParseStatus.FAILED, error_count

    # Helper methods

    def _extract_function_info(self, node: Node, parent_path: str) -> FunctionNode | None:
        """Extract information about a function declaration."""
        func_name = None
        parameters = []
        return_type = None

        # Get function name
        for child in node.children:
            if child.type == "identifier":
                func_name = self._get_node_text(child)
                break

        if not func_name:
            return None

        # Get parameters
        for child in node.children:
            if child.type == "parameter_list":
                parameters = self._extract_parameters(child)
                break

        # Get return type (can be multiple returns)
        for child in node.children:
            if child.type in ["type_identifier", "pointer_type", "slice_type", "array_type", "qualified_type"]:
                return_type = self._get_node_text(child)
                break
            elif child.type == "parameter_list":
                # Check if this is the return values parameter list (comes after function params)
                # In Go AST, return values can be a parameter_list
                if parameters:  # We already got function parameters
                    return_type = self._extract_return_type(child)

        # Build qualified name
        qualified_name = f"{parent_path}.{func_name}" if parent_path else func_name

        # Build signature
        param_str = ", ".join([p.name for p in parameters])
        signature = f"func {func_name}({param_str})"

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
            decorators=[],
            line_start=line_start,
            line_end=line_end,
            is_async=False,
            docstring=None,
        )

    def _extract_method_info(self, node: Node, parent_path: str) -> FunctionNode | None:
        """Extract information about a method declaration."""
        func_name = None
        parameters = []
        return_type = None
        receiver_type = None

        # Get receiver type
        for child in node.children:
            if child.type == "parameter_list":
                # First parameter_list is the receiver
                receiver_params = self._extract_parameters(child)
                if receiver_params:
                    receiver_type = receiver_params[0].type_hint
                break

        # Get method name
        for child in node.children:
            if child.type == "field_identifier":
                func_name = self._get_node_text(child)
                break

        if not func_name:
            return None

        # Get parameters (second parameter_list)
        param_lists = [child for child in node.children if child.type == "parameter_list"]
        if len(param_lists) > 1:
            parameters = self._extract_parameters(param_lists[1])

        # Get return type
        for child in node.children:
            if child.type in ["type_identifier", "pointer_type", "slice_type", "array_type", "qualified_type"]:
                return_type = self._get_node_text(child)
                break
            elif child.type == "parameter_list" and len(param_lists) > 2:
                # Return values as parameter_list (third one)
                return_type = self._extract_return_type(param_lists[2])

        # Build qualified name with receiver type
        if receiver_type:
            # Clean up pointer syntax
            clean_receiver = receiver_type.lstrip("*")
            qualified_name = f"{clean_receiver}.{func_name}"
        else:
            qualified_name = f"{parent_path}.{func_name}" if parent_path else func_name

        # Build signature
        param_str = ", ".join([p.name for p in parameters])
        if receiver_type:
            signature = f"func ({receiver_type}) {func_name}({param_str})"
        else:
            signature = f"func {func_name}({param_str})"

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
            decorators=[],
            line_start=line_start,
            line_end=line_end,
            is_async=False,
            docstring=None,
        )

    def _extract_parameters(self, params_node: Node) -> list[Parameter]:
        """Extract function parameters."""
        parameters = []

        for child in params_node.children:
            if child.type == "parameter_declaration":
                param_info = self._extract_parameter_info(child)
                if param_info:
                    # Go can have multiple params with same type: (a, b int)
                    if isinstance(param_info, list):
                        parameters.extend(param_info)
                    else:
                        parameters.append(param_info)
            elif child.type == "variadic_parameter_declaration":
                param_info = self._extract_variadic_parameter(child)
                if param_info:
                    parameters.append(param_info)

        return parameters

    def _extract_parameter_info(self, param_node: Node) -> Parameter | list[Parameter] | None:
        """Extract information about a single parameter or group of parameters."""
        param_names = []
        param_type = None

        for child in param_node.children:
            if child.type == "identifier":
                param_names.append(self._get_node_text(child))
            elif child.type in ["type_identifier", "pointer_type", "slice_type", "array_type", "qualified_type"]:
                param_type = self._get_node_text(child)

        if param_names and param_type:
            # Multiple params with same type
            return [
                Parameter(name=name, type_hint=param_type, default_value=None, is_optional=False)
                for name in param_names
            ]
        elif param_type and not param_names:
            # Unnamed parameter (rare but valid in Go)
            return Parameter(name="_", type_hint=param_type, default_value=None, is_optional=False)

        return None

    def _extract_variadic_parameter(self, param_node: Node) -> Parameter | None:
        """Extract variadic parameter (...type)."""
        param_name = None
        param_type = None

        for child in param_node.children:
            if child.type == "identifier":
                param_name = self._get_node_text(child)
            elif child.type in ["type_identifier", "pointer_type", "slice_type"]:
                param_type = f"...{self._get_node_text(child)}"

        if param_name and param_type:
            return Parameter(name=param_name, type_hint=param_type, default_value=None, is_optional=False)

        return None

    def _extract_return_type(self, param_list_node: Node) -> str | None:
        """Extract return type from parameter list (for multiple return values)."""
        types = []

        for child in param_list_node.children:
            if child.type == "parameter_declaration":
                # Extract type from parameter
                for param_child in child.children:
                    if param_child.type in ["type_identifier", "pointer_type", "slice_type", "qualified_type"]:
                        types.append(self._get_node_text(param_child))
                    elif param_child.type == "identifier":
                        # Named return value - we still want the type
                        pass

        if len(types) > 1:
            return f"({', '.join(types)})"
        elif len(types) == 1:
            return types[0]

        return None

    def _extract_type_spec(self, node: Node, parent_path: str) -> ClassInfo | None:
        """Extract information about a type specification (struct or interface)."""
        type_name = None
        base_classes = []
        is_interface = False

        # Get type name
        for child in node.children:
            if child.type == "type_identifier":
                type_name = self._get_node_text(child)
                break

        if not type_name:
            return None

        # Check if it's a struct or interface
        for child in node.children:
            if child.type == "struct_type":
                base_classes = self._extract_struct_embedding(child)
                is_interface = False
                break
            elif child.type == "interface_type":
                base_classes = self._extract_interface_composition(child)
                is_interface = True
                break

        return ClassInfo(type_name, base_classes, [], is_interface)

    def _extract_struct_embedding(self, struct_node: Node) -> list[str]:
        """Extract embedded types from struct."""
        embedded = []

        for child in struct_node.children:
            if child.type == "field_declaration_list":
                for field in child.children:
                    if field.type == "field_declaration":
                        # Check if it's an embedded field (no field name, just type)
                        has_name = False
                        embedded_type = None

                        for field_child in field.children:
                            if field_child.type == "field_identifier":
                                has_name = True
                            elif field_child.type in ["type_identifier", "qualified_type", "pointer_type"]:
                                embedded_type = self._get_node_text(field_child)

                        if not has_name and embedded_type:
                            # This is an embedded field
                            embedded.append(embedded_type.lstrip("*"))

        return embedded

    def _extract_interface_composition(self, interface_node: Node) -> list[str]:
        """Extract composed interfaces from interface."""
        composed = []

        for child in interface_node.children:
            if child.type == "type_elem":
                # Type element can be a composed interface
                for elem_child in child.children:
                    if elem_child.type == "type_identifier":
                        composed.append(self._get_node_text(elem_child))

        return composed

    def _extract_edges(
        self,
        tree: Node,
        file_id: str,
        functions: list[FunctionNode],
        classes: list[ClassInfo]
    ) -> list[BaseEdge]:
        """Extract relationship edges from the parse tree."""
        edges = []

        # IMPORTS edges - extract from imports list for accurate per-import edges
        imports = self.extract_imports(tree)
        for imp in imports:
            edges.append(BaseEdge(
                type=EdgeType.IMPORTS,
                confidence=1.0,
                metadata={
                    "source_id": file_id,
                    "target_id": f"module_{imp.module}",
                }
            ))

        # INHERITS edges (struct embedding and interface composition)
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
