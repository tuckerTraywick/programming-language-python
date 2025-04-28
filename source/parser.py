from lexer import *

# A node in the parse tree.
class Node:
	def __init__(self, type: str, *children: "Node"):
		self.type = type
		self.children = list(children)

	def __repr__(self):
		# If the node is an error, don't print its children.
		if self.type == "error":
			return f"Parsing error: {self.children[0]}"
		return f"{self.type}({', '.join(map(str, self.children))})"

	# Prints a readable multi-line representation of the node and its children.
	def prettyPrint(self, indentation: int=0):
		if self.type == "error":
			print(indentation*"| " + self.children[0])
			return
		
		print(indentation*"| " + self.type)
		for child in self.children:
			child.prettyPrint(indentation + 1)

class _Parser:
	prefixPrecedences = {}
	infixPrecedences = {}

	def __init__(self, tokens: list[Token]):
		self.tokens = tokens

def parse(tokens: list[Token]) -> tuple[Node, list[Node]]:
	parser: _Parser = _Parser(tokens)
