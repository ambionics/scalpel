"""Quick and dirty transpiler for porting Python 3.10 _basic_ match statements and type hints to Python 3.8"""

import ast


class MatchToIfElseTransformer(ast.NodeTransformer):
    def _case_to_if(self, case: ast.match_case, subject: ast.expr) -> ast.If:
        """Transform a match case to an if statement

        Args:
            case (ast.match_case): The match case to transform
            subject (ast.expr):  The subject of the match statement

        Returns:
            ast.If: The transformed if statement
        """
        test = self._pattern_to_expr(case.pattern, subject)
        if case.guard is not None:
            # Handle case like 'case x if x > 0:'
            # Simply add the condition to the if statement
            test = ast.BoolOp(
                op=ast.And(),
                values=[
                    test,
                    self.visit(case.guard),
                ],
            )

        # Ensure recursive transformation within the body of each case
        body = [self.visit(stmt) for stmt in case.body]
        return ast.If(test=test, body=body, orelse=[])

    def visit_Match(self, node: ast.Match) -> ast.AST:
        """Transform a Python 3.10 match statement to a series of if-else statements

        Args:
            node (ast.Match): The match statement to transform

        Returns:
            ast.AST: The transformed if-else statements
        """
        if_stmts = []

        # Transform each case to an if statement
        for case in node.cases:
            if_stmts.append(self._case_to_if(case, node.subject))

        # Link the if-else statements together
        for i in range(len(if_stmts) - 1, 0, -1):
            if_stmts[i - 1].orelse = [if_stmts[i]]

        return if_stmts[0] if if_stmts else node

    def _pattern_to_expr(self, pattern: ast.AST, subject: ast.expr) -> ast.expr:
        match pattern:
            # Transform case "abc" to subject == value
            case ast.MatchValue():
                return ast.Compare(
                    left=subject,
                    ops=[ast.Eq()],
                    comparators=[pattern.value],
                )

            # Transform to isinstance(subject, cls) and subject.attr == value and ...
            case ast.MatchClass(
                cls=cls, kwd_attrs=kwd_attrs, kwd_patterns=kwd_patterns
            ):
                # Check if the subject is an instance of the class
                comparisons = [
                    ast.Call(
                        func=ast.Name(id="isinstance", ctx=ast.Load()),
                        args=[subject, ast.Name(id=cls.id, ctx=ast.Load())],
                        keywords=[],
                    )
                ]

                # Check the attributes of the subject
                for attr, pattern in zip(kwd_attrs, kwd_patterns):
                    left = ast.Call(
                        func=ast.Name(id="getattr", ctx=ast.Load()),
                        args=[subject, ast.Constant(value=attr)],
                        keywords=[],
                    )
                    comparator = self._pattern_to_expr(pattern, subject)
                    comparison = ast.Compare(
                        left=left,
                        ops=[ast.Eq()],
                        comparators=[comparator],
                    )
                    comparisons.append(comparison)

                return ast.BoolOp(
                    op=ast.And(),
                    values=comparisons,
                )

            #  Handle case _ if <condition>: ...
            case ast.MatchAs():
                if pattern.pattern is None:
                    return ast.Constant(value=True)

                return self._pattern_to_expr(pattern.pattern, subject)

            # Transform to <transformed_pattern1> or <transformed_pattern2> or ...
            case ast.MatchOr():
                return ast.BoolOp(
                    op=ast.Or(),
                    values=[
                        self._pattern_to_expr(p, subject) for p in pattern.patterns
                    ],
                )

            # Handle list/tuple patterns
            # Transform to subject[0] == value1 and subject[1] == value2 and ...
            case ast.MatchSequence():
                checks = []
                for i, elt in enumerate(pattern.patterns):
                    element_check = self._pattern_to_expr(
                        elt,
                        ast.Subscript(
                            value=subject,
                            slice=ast.Index(value=ast.Constant(value=i)),
                            ctx=ast.Load(),
                        ),
                    )
                    checks.append(element_check)

                # Combine checks with logical AND
                return ast.BoolOp(op=ast.And(), values=checks)

            case ast.MatchSingleton():
                return ast.Compare(
                    left=subject,
                    ops=[ast.Is()],
                    comparators=[pattern],
                )

            # Default case, transform to subject == pattern
            case _:
                return ast.Compare(
                    left=subject,
                    ops=[ast.Eq()],
                    comparators=[pattern],
                )


class TypeHintTransformer(ast.NodeTransformer):
    """Transform Python 3.10 type hints to Python 3.8 compatible type hints

    Args:
        ast (_type_): The abstract syntax tree to transform
    """

    def __init__(self):
        self.need_imports = set()

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        """Transform binary operations in type hints
        E.g. type1 | type2 -> Union[type1, type2]

        Args:
            node (ast.BinOp): The binary operation to transform

        Returns:
            ast.AST: The transformed binary operation
        """
        if isinstance(node.op, ast.BitOr):
            # Import Union if not already imported
            self.need_imports.add("Union")
            left = self.visit(node.left)
            right = self.visit(node.right)
            return ast.Subscript(
                value=ast.Name(id="Union", ctx=ast.Load()),
                slice=ast.Index(value=ast.Tuple(elts=[left, right], ctx=ast.Load())),
                ctx=ast.Load(),
            )

        return self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        """Transform subscript slices in type hints
        E.g. list[int] -> List[int]

        Args:
            node (ast.Subscript): The subscript slice to transform

        Returns:
            ast.AST:    The transformed subscript slice
        """
        # Transform the subscript slice if it's a type hint using '[]'
        # Eg. list[int] -> List[int]
        node.value = self.visit(node.value)
        node.slice = self.visit(node.slice)

        # Handle unsunported suscript type hints like Mapping[K, V]
        if isinstance(node.value, ast.Name) and node.value.id in {
            "Mapping",
            "MutableMapping",
        }:
            # Transform Mapping[K, V] to plain Mapping
            # E.g. Mapping[K, V] -> Mapping
            return ast.Name(id=node.value.id, ctx=node.ctx)

        if isinstance(node.value, ast.Name) and node.value.id in {
            "list",
            "tuple",
            "dict",
            "set",
            "Sequence",
        }:
            self.need_imports.add(node.value.id.capitalize())

            # Ensure the slice is properly transformed, including nested type hints
            transformed_slice = self.transform_slice(node.slice)
            return ast.Subscript(
                value=ast.Name(id=node.value.id.capitalize(), ctx=ast.Load()),
                slice=transformed_slice,
                ctx=node.ctx,
            )

        return node

    def transform_slice(self, slice: ast.AST) -> ast.AST:
        """Recursively transform slices for nested type hints
        E.g. list[list[int]] -> List[List[int]]

        Args:
            slice (ast.AST): The slice to transform

        Returns:
            ast.AST:   The transformed slices
        """
        if isinstance(slice, ast.Index):
            return ast.Index(value=self.visit(slice.value))

        return slice

    def visit_Tuple(self, node: ast.Tuple) -> ast.AST:
        """Transform tuples in type hints
        E.g. (int, str) -> Tuple[int, str]


        Args:
            node (ast.Tuple): The tuple to transform

        Returns:
            ast.AST:   The transformed tuple
        """
        elts = [self.visit(elt) for elt in node.elts]
        return ast.Tuple(elts=elts, ctx=ast.Load())

    def visit_Module(self, node: ast.Module) -> ast.AST:
        """Ensure all necessary imports are added to the module

        Args:
            node (ast.Module): The module to transform

        Returns:
            ast.AST:  The transformed module
        """
        self.generic_visit(node)
        for import_name in sorted(self.need_imports):
            typing_import = ast.ImportFrom(
                module="typing", names=[ast.alias(name=import_name)], level=0
            )
            node.body.insert(0, typing_import)

        return node


class FutureImportTransformer(ast.NodeTransformer):
    """Add __future__ imports to the top of the module

    Args:
        ast (_type_): The abstract syntax tree to transform
    """

    def __init__(self):
        self.future_imports = []

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        """Remove existing __future__ imports and collect them for later re-insertion"""
        if node.module == "__future__":
            self.future_imports.append(node)
            return None  # Remove the node from its original position

        return node

    def visit_Module(self, node: ast.Module) -> ast.AST:
        """Prepend collected __future__ imports to the module body

        Args:
            node (ast.Module): The module to transform

        Returns:
            ast.AST: The transformed module
        """
        self.generic_visit(node)  # First, process and collect all __future__ imports
        # Prepend collected __future__ imports to the module body
        node.body = self.future_imports + node.body
        return node


def transform_to_legacy(source_code: str) -> str:
    """Transform Python 3.10 code to Python 3.8 compatible code

    Args:
        source_code (str): The Python 3.10 code to transform

    Returns:
        str: The transformed Python 3.8 compatible code
    """
    parsed_source = ast.parse(source_code)
    # Transform match statements to if-else statements
    transformed = MatchToIfElseTransformer().visit(parsed_source)

    # Transform type hints to Python 3.8 compatible type hints
    transformed = TypeHintTransformer().visit(transformed)

    # Add __future__ imports to the top of the module
    transformed = FutureImportTransformer().visit(transformed)
    return ast.unparse(transformed)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python transpiler.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    with open(file_path, "r") as file:
        code = file.read()

    new_code = transform_to_legacy(code)
    print(new_code)
