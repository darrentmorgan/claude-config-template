"""TypeScript parser using tree-sitter.

Implements T041: TypeScript parser with full language support.
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

    def __init__(self, module: str, names: list[str], is_type_import: bool = False):
        self.module = module
        self.names = names
        self.is_type_import = is_type_import


class ClassInfo:
    """Represents a class or interface definition."""

    def __init__(self, name: str, base_classes: list[str], methods: list[FunctionNode], is_interface: bool = False):
        self.name = name
        self.base_classes = base_classes
        self.methods = methods
        self.is_interface = is_interface


class TypeScriptParser(BaseParser):
    """Parser for TypeScript source code using tree-sitter."""

    def __init__(self):
        """Initialize TypeScript parser."""
        super().__init__("typescript")

        # Get TypeScript language and parser from tree-sitter-language-pack
        self._language = get_language("typescript")
        self._parser = get_parser("typescript")

    def parse_file(self, file_path: str, content: str | None = None) -> ParserResult:
        """Parse a TypeScript source file.

        Args:
            file_path: Path to the TypeScript file
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
            language="typescript",
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
        """Extract import statements from TypeScript AST.

        Args:
            tree: Tree-sitter syntax tree root node

        Returns:
            List of ImportInfo objects
        """
        imports = []

        for node in self._walk_tree(tree):
            if node.type == "import_statement":
                # import { name1, name2 } from 'module'
                # import * as name from 'module'
                # import defaultName from 'module'
                module_name = None
                imported_names = []
                is_type_import = False

                # Check for type import
                for child in node.children:
                    if child.type == "type" or self._get_node_text(child) == "type":
                        is_type_import = True

                # Get module name (string literal)
                for child in node.children:
                    if child.type == "string":
                        module_name = self._get_node_text(child).strip('"').strip("'")

                # Get imported names
                for child in node.children:
                    if child.type == "import_clause":
                        imported_names = self._extract_import_names(child)

                if module_name:
                    imports.append(ImportInfo(module_name, imported_names, is_type_import))

        return imports

    def _extract_import_names(self, import_clause: Node) -> list[str]:
        """Extract names from import clause."""
        names = []

        for child in import_clause.children:
            if child.type == "identifier":
                # Default import
                names.append(self._get_node_text(child))
            elif child.type == "named_imports":
                # { name1, name2 }
                for named_child in child.children:
                    if named_child.type == "import_specifier":
                        for spec_child in named_child.children:
                            if spec_child.type == "identifier":
                                names.append(self._get_node_text(spec_child))
                                break
            elif child.type == "namespace_import":
                # * as name
                for ns_child in child.children:
                    if ns_child.type == "identifier":
                        names.append(self._get_node_text(ns_child))

        return names

    def extract_functions(self, tree: Node, parent_path: str) -> list[FunctionNode]:
        """Extract function definitions from TypeScript AST.

        Args:
            tree: Tree-sitter syntax tree node
            parent_path: Qualified name of parent (for methods)

        Returns:
            List of FunctionNode instances
        """
        functions = []

        for node in self._walk_tree(tree):
            if node.type in ["function_declaration", "function_signature", "function_expression"]:
                # function_expression appears in error recovery scenarios
                func_info = self._extract_function_info(node, parent_path)
                if func_info:
                    functions.append(func_info)
            elif node.type == "lexical_declaration":
                # const/let fn = () => {}
                func_info = self._extract_arrow_function(node, parent_path)
                if func_info:
                    functions.append(func_info)
            elif node.type == "method_definition":
                func_info = self._extract_method_info(node, parent_path)
                if func_info:
                    functions.append(func_info)

        return functions

    def extract_classes(self, tree: Node, parent_path: str) -> list[ClassInfo]:
        """Extract class and interface definitions from TypeScript AST.

        Args:
            tree: Tree-sitter syntax tree node
            parent_path: Qualified name of parent module

        Returns:
            List of ClassInfo instances
        """
        classes = []

        for node in tree.children:
            if node.type == "class_declaration":
                class_info = self._extract_class_info(node, parent_path, False)
                if class_info:
                    classes.append(class_info)
            elif node.type == "interface_declaration":
                class_info = self._extract_class_info(node, parent_path, True)
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
        is_async = False

        # Check for async (it's a child of function_declaration)
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
            if child.type == "formal_parameters":
                parameters = self._extract_parameters(child)
                break

        # Get return type
        for child in node.children:
            if child.type == "type_annotation":
                return_type = self._extract_type(child)
                break

        # Build qualified name
        qualified_name = f"{parent_path}.{func_name}" if parent_path else func_name

        # Build signature
        param_str = ", ".join([p.name for p in parameters])
        signature = f"function {func_name}({param_str})"

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
            is_async=is_async,
            docstring=None,
        )

    def _extract_arrow_function(self, node: Node, parent_path: str) -> FunctionNode | None:
        """Extract information about an arrow function (const fn = () => {})."""
        func_name = None
        parameters = []
        return_type = None
        is_async = False
        has_arrow_function = False

        # Find variable declarator
        for child in node.children:
            if child.type == "variable_declarator":
                # Get function name from variable name
                for decl_child in child.children:
                    if decl_child.type == "identifier":
                        func_name = self._get_node_text(decl_child)

                    # Find arrow function
                    elif decl_child.type == "arrow_function":
                        has_arrow_function = True

                        # Check for async
                        for arrow_child in decl_child.children:
                            if arrow_child.type == "async" or self._get_node_text(arrow_child) == "async":
                                is_async = True

                        # Get parameters
                        for arrow_child in decl_child.children:
                            if arrow_child.type == "formal_parameters":
                                parameters = self._extract_parameters(arrow_child)
                                break

                        # Get return type
                        for arrow_child in decl_child.children:
                            if arrow_child.type == "type_annotation":
                                return_type = self._extract_type(arrow_child)
                                break

        # Only create function node if we actually found an arrow function
        if not func_name or not has_arrow_function:
            return None

        # Build qualified name
        qualified_name = f"{parent_path}.{func_name}" if parent_path else func_name

        # Build signature
        param_str = ", ".join([p.name for p in parameters])
        signature = f"const {func_name} = ({param_str}) =>"

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
            is_async=is_async,
            docstring=None,
        )

    def _extract_method_info(self, node: Node, parent_path: str) -> FunctionNode | None:
        """Extract information about a class method."""
        func_name = None
        parameters = []
        return_type = None
        decorators = []
        is_async = False

        # Check for async
        for child in node.children:
            if child.type == "async" or self._get_node_text(child) == "async":
                is_async = True

        # Get method name (property_identifier)
        for child in node.children:
            if child.type == "property_identifier":
                func_name = self._get_node_text(child)
                break

        if not func_name:
            return None

        # Get decorators (check previous siblings)
        current = node.prev_sibling
        while current:
            if current.type == "decorator":
                decorator_name = self._extract_decorator_name(current)
                if decorator_name:
                    decorators.insert(0, decorator_name)
            current = current.prev_sibling

        # Get parameters
        for child in node.children:
            if child.type == "formal_parameters":
                parameters = self._extract_parameters(child)
                break

        # Get return type
        for child in node.children:
            if child.type == "type_annotation":
                return_type = self._extract_type(child)
                break

        # Build qualified name
        qualified_name = f"{parent_path}.{func_name}" if parent_path else func_name

        # Build signature
        param_str = ", ".join([p.name for p in parameters])
        signature = f"{func_name}({param_str})"

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
            docstring=None,
        )

    def _extract_parameters(self, params_node: Node) -> list[Parameter]:
        """Extract function parameters."""
        parameters = []

        for child in params_node.children:
            if child.type == "required_parameter":
                param_info = self._extract_parameter_info(child)
                if param_info:
                    parameters.append(param_info)
            elif child.type == "optional_parameter":
                param_info = self._extract_parameter_info(child, is_optional=True)
                if param_info:
                    parameters.append(param_info)

        return parameters

    def _extract_parameter_info(self, param_node: Node, is_optional: bool = False) -> Parameter | None:
        """Extract information about a single parameter."""
        param_name = None
        param_type = None
        default_value = None

        for child in param_node.children:
            if child.type == "identifier":
                param_name = self._get_node_text(child)
            elif child.type == "type_annotation":
                param_type = self._extract_type(child)
            elif child.type in ["number", "string", "true", "false", "null", "undefined"]:
                default_value = self._get_node_text(child)

        if param_name and param_name != "this":
            return Parameter(
                name=param_name,
                type_hint=param_type,
                default_value=default_value,
                is_optional=is_optional or (default_value is not None),
            )

        return None

    def _extract_type(self, type_annotation: Node) -> str | None:
        """Extract type from type annotation."""
        for child in type_annotation.children:
            if child.type == "type_identifier":
                return self._get_node_text(child)
            elif child.type == "predefined_type":
                return self._get_node_text(child)
            elif child.type == "generic_type":
                # For generics like Promise<T>, return the full text
                return self._get_node_text(child)

        return None

    def _extract_decorator_name(self, decorator_node: Node) -> str | None:
        """Extract just the decorator name from a decorator node.

        Handles both @Decorator and @Decorator(...) forms.
        Returns just the identifier name without @ or arguments.

        Args:
            decorator_node: Tree-sitter decorator node

        Returns:
            Decorator name string or None
        """
        for child in decorator_node.children:
            if child.type == "call_expression":
                # @Decorator(...) - extract identifier from call_expression
                for call_child in child.children:
                    if call_child.type == "identifier":
                        return self._get_node_text(call_child)
            elif child.type == "identifier":
                # @Decorator - direct identifier
                return self._get_node_text(child)

        return None

    def _extract_class_info(self, node: Node, parent_path: str, is_interface: bool) -> ClassInfo | None:
        """Extract information about a class or interface definition."""
        class_name = None
        base_classes = []
        methods = []

        # Get class/interface name
        for child in node.children:
            if child.type == "type_identifier":
                class_name = self._get_node_text(child)
                break

        if not class_name:
            return None

        # Get base classes/interfaces
        for child in node.children:
            if child.type == "class_heritage":
                # extends Base implements Interface
                for heritage_child in child.children:
                    if heritage_child.type in ["extends_clause", "implements_clause"]:
                        for type_node in heritage_child.children:
                            if type_node.type in ["type_identifier", "identifier"]:
                                base_classes.append(self._get_node_text(type_node))

        # Get methods from class body
        for child in node.children:
            if child.type == "class_body":
                class_path = f"{parent_path}.{class_name}" if parent_path else class_name
                methods = self.extract_functions(child, class_path)
                break

        return ClassInfo(class_name, base_classes, methods, is_interface)

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
        for node in self._walk_tree(tree):
            if node.type == "import_statement":
                edges.append(BaseEdge(
                    type=EdgeType.IMPORTS,
                    confidence=1.0,
                    metadata={
                        "source_id": file_id,
                        "target_id": "module_" + self._get_node_text(node),
                    }
                ))

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
