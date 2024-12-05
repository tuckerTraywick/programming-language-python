from lexer import *

# A node in the parse tree.
@dataclass
class Node:
	type: str
	children: "list[Token | Node]"

	def __init__(self, type: str, *children: "Token | Node"):
		self.type = type
		self.children = children

	def __str__(self) -> str:
		return f"{self.type}({', '.join(map(str, self.children))})"

# Contains the state of the parser.
class Parser:
	tokens: list[Token] = []
	i: int = 0

	# Returns the next token if there are any left and None if there aren't.
	@property
	def nextToken(self) -> Token:
		if self.hasToken():
			return self.tokens[self.i]
		return None
	
	# Returns true if the parser still has a token to parse.
	def hasToken(self) -> bool:
		return self.i < len(self.tokens)
	
	# Returns true if the next token matches the type and/or text. If you pass None for a parameter,
	# it won't be matched.
	def peek(self, type: str=None, text: str=None):
		next = self.nextToken
		# TODO: Maybe make this multiple if statements.
		return next and (not type or next.type == type) or (not text or next.text == text)
	
	# Initializes the parser and parses a list of tokens.
	def parse(self, tokens: list[Token]) -> Node:
		self.tokens = tokens
		self.i = 0

# Turns a list of tokens into a syntax tree.
def parse(tokens: list[Token]) -> Node:
	return Parser().parse(tokens)
