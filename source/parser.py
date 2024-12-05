from lexer import *

@dataclass
class Node:
	type: str
	children: "list[Token | Node]"

	def __init__(self, type: str, *children: "Token | Node"):
		self.type = type
		self.children = children

	def __str__(self) -> str:
		return f"{self.type}({', '.join(map(str, self.children))})"

def parse(tokens: list[Token]) -> Node:
	pass
