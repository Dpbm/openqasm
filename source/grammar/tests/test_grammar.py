import unittest
import io
from contextlib import redirect_stderr

from antlr4 import *
from antlr4.tree.Trees import Trees

from source.grammar.qasm3Lexer import qasm3Lexer
from source.grammar.qasm3Parser import qasm3Parser


def get_pretty_tree(
    tree: "ParseTree", rule_names: list = None, parser: Parser = None, level: int = 0
) -> str:
    """Take antlr ``ParseTree`` and return indented tree format for test comparison.

    Adapted from ``antrl4.tree.Trees.toStringTree()`` method.

    Args:
        tree: The antlr parse tree.
        rule_names: Names of parser rules.
        parser: The parser used to generated the tree.
        level: Level of tree (used for indentation).

    Returns:
        Pretty tree format (indents of one space at each level).
    """
    indent_value = " "  # indent using single space

    if parser is not None:
        rule_names = parser.ruleNames

    node_text = Trees.getNodeText(tree, rule_names)
    pretty_tree = level * indent_value + node_text + "\n"

    if tree.getChildCount() > 0:
        for i in range(0, tree.getChildCount()):
            pretty_tree += get_pretty_tree(tree.getChild(i), rule_names=rule_names, level=level + 1)

    return pretty_tree


def build_parse_tree(input_str: str, using_file: bool = False) -> str:
    """Build indented parse tree in string format.

    Args:
        input_str: Input program or file path.
        using_file: Whether input string is source program or file path.

    Raises:
        Exception: If build fails (at any stage: lexing or parsing).

    Returns:
        Parse tree string in indented format.
    """
    input = FileStream(input_str) if using_file else InputStream(input_str)
    pretty_tree = ""
    # antlr errors (lexing and parsing) sent to stdout -> redirect to variable err
    with io.StringIO() as err, redirect_stderr(err):
        lexer = qasm3Lexer(input)
        stream = CommonTokenStream(lexer)
        parser = qasm3Parser(stream)
        tree = parser.program()

        pretty_tree = get_pretty_tree(tree, None, parser)

        error = err.getvalue()
        if error:
            raise Exception("Parse tree build failed. Error:\n" + error)

    return pretty_tree


class TestGrammar(unittest.TestCase):
    def setUp(self):
        self.examples_path = "examples/"
        self.test_path = "source/grammar/tests/outputs/"

    def test_binary_expression(self):
        add_tree = build_parse_tree("2+2;")
        with open(self.test_path + "add.tree", "r") as test_file:
            add_test_tree = test_file.read()
        self.assertEqual(add_tree, add_test_tree)

        bshift_tree = build_parse_tree("x << y;")
        with open(self.test_path + "bshift.tree", "r") as test_file:
            bshift_test_tree = test_file.read()
        self.assertEqual(bshift_tree, bshift_test_tree)

    def test_unary_expression(self):
        not_tree = build_parse_tree("! my_var;")
        with open(self.test_path + "not.tree", "r") as test_file:
            not_test_tree = test_file.read()
        self.assertEqual(not_tree, not_test_tree)

    def test_empty_gate(self):
        empty_gate_tree = build_parse_tree("gate g q { }")
        with open(self.test_path + "empty_gate.tree", "r") as test_file:
            empty_gate_test_tree = test_file.read()

        self.assertEqual(empty_gate_tree, empty_gate_test_tree)

    def test_adder(self):
        """Verify that no error is raised for adder example."""
        tree = build_parse_tree(self.examples_path + "adder.qasm", using_file=True)


if __name__ == "__main__":
    unittest.main()
