# TODO: Make a separate ParsingError type to encode errors instead of representing them as nodes.
from lexer import *

# A node in the parse tree.
@dataclass
class Node:
	type: str
	children: "list[Token | Node]"

	def __init__(self, type: str, *children: "Node | Token"):
		self.type = type
		self.children = list(children)

	def __repr__(self) -> str:
		# If the node is an error, don't print its children.
		if self.type == "error":
			return f"Parsing error: {self.children[0]}"
		return f"{self.type}({', '.join(map(str, self.children))})"

	# Prints a readable multi-line representation of the node and its children.
	def prettyPrint(self, indentation: int=0) -> str:
		print(indentation*"| " + self.type)
		if self.type.endswith("."):
			return

		for child in self.children:
			child.prettyPrint(indentation + 1)

	# Returns true if the node contains something.
	def hasData(self) -> bool:
		return bool(self.type or self.children)

# Matches the type or text of a single token.
class Match:
	def __init__(self, type="", text=""):
		self.type = type
		self.text = text

	def parse(self, tokens, index, parser):
		if index >= len(tokens):
			return (None, index)
		
		token = tokens[index]
		if self.type and token.type != self.type:
			return (None, index)
		if self.text and token.text != self.text:
			return (None, index)
		return (token, index + 1)

# Matches a sequence of items.
class Sequence:
	def __init__(self, *parsers):
		assert parsers, "You can't have an empty sequence."
		self.parsers = parsers

	def parse(self, tokens, index, parser):
		result = []
		for parser in self.parsers:
			node, index = parser.parse(tokens, index, parser)
			if node is None:
				return (None, index)
			
			if isinstance(node, list):
				result += node
			elif isinstance(node, (Token, Error)) or node.hasData():
				result.append(node)
		return (result, index)

# Matches one of many cases. Tries each case in order and backtracks when a case fails.
class Choice:
	def __init__(self, *parsers):
		assert parsers, "You can't have an empty choice."
		self.parsers = parsers

	def parse(self, tokens, index, parser):
		for parser in self.parsers:
			result, newIndex = parser.parse(tokens, index, parser)
			if result:
				return (result, newIndex)
		return (None, index)

# Matches 0 or 1 occurrence of an item. Returns an empty node if it doesn't find a match.
class Maybe:
	def __init__(self, parser):
		self.parser = parser

	def parse(self, tokens, index, parser):
		result, index = self.parser.parse(tokens, index, parser)
		if result is None:
			return (Node(""), index)
		return (result, index)

# Matches 0 or more occurrences of an item. Returns an empty list if no matches were found.
class Repeat0:
	def __init__(self, parser):
		self.parser = parser

	def parse(self, tokens, index, parser):
		result = []
		node, index = self.parser.parse(tokens, index, parser)
		while node is not None:
			if isinstance(node, list):
				result += node
			elif isinstance(node, (Token, Error)) or node.hasData():
				result.append(node)
			node, index = self.parser.parse(tokens, index, parser)
		return (result, index)

# Matches 1 or more occurrences of an item.
class Repeat1:
	def __init__(self, parser):
		self.parser = parser

	def parse(self, tokens, index, parser):
		result = []
		node, newIndex = self.parser.parse(tokens, index, parser)
		while node is not None:
			if isinstance(node, list):
				result += node
			elif isinstance(node, (Token, Error)) or node.hasData():
				result.append(node)
			node, newIndex = self.parser.parse(tokens, newIndex, parser)
		
		# Backtrack if no matches were found.
		if result:
			return (result, newIndex)
		else:
			return (None, index)

# Returns a node with a parsing error.
class Error:
	def __init__(self, message):
		self.message = message

	def parse(self, tokens, index, parser):
		return (Node("error", self.message), index)

# Returns a node with a parsing error and eats advances until it sees the given token.
class Recover:
	def __init__(self, message, type="", text="", consumeMatch=True):
		self.message = message
		self.type = type
		self.text = text
		self.consumeMatch = consumeMatch

	def parse(self, tokens, index, parser):
		while index < len(tokens) and tokens[index].type != self.type and tokens[index].text != self.text:
			index += 1

		# Skip the last token if it matches.
		if self.consumeMatch and index < len(tokens) and tokens[index].match(self.type, self.text):
			index += 1
		return (Node("error", self.message), index)

# Parses an expression with the given operator precedences.
class Expression:
	def __init__(self, basicParser, prefixOperators, infixOperators):
		self.basicParser = basicParser
		self.prefixOperators = prefixOperators
		self.infixOperators = infixOperators

	def parse(self, tokens, index, parser):
		result, index = self.basicParser(tokens, index, parser)

# Matches another parsing rule.
class Nonterminal:
	def __init__(self, rule):
		self.rule = rule

	def parse(self, tokens, index, parser):
		return parser.rules[self.rule].parse(tokens, index, parser)

# Wraps the result of a parser in a node.
class Wrap:
	def __init__(self, head, parser):
		self.head = head
		self.parser = parser

	def parse(self, tokens, index, parser):
		result, index = self.parser.parse(tokens, index, parser)
		if result is None:
			return (result, index)
		if isinstance(result, list):
			return (Node(self.head, *result), index)
		if isinstance(result, Node) and not result.hasData():
			return (Node(self.head), index)
		return (Node(self.head, result), index)

# A parser with a set of mutually recursive rules.
class Parser:
	def __init__(self, startRule, rules):
		self.startRule = startRule
		self.rules = rules

	def parse(self, tokens, index=0):
		result, _ = self.rules[self.startRule].parse(tokens, index, self)
		return result


"""
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
	
	# Returns the previous token if there was one.
	@property
	def lastToken(self) -> Token:
		if self.i > 0:
			return self.tokens[self.i - 1]
		return None
	
	# Returns true if the parser still has a token to parse.
	def hasToken(self) -> bool:
		return self.i < len(self.tokens)
	
	# Returns true if the next token matches the type and/or text.
	def peek(self, type: str=None, text: str=None) -> bool:
		next = self.nextToken
		# TODO: Maybe make this multiple if statements.
		return next and (not type or next.type == type) and (not text or next.text == text)

	# Consumes the next token and returns it if it matches the type and/or text. Returns None if it
	# doesn't.
	def accept(self, type: str=None, text: str=None) -> Token:
		next = self.nextToken
		if self.peek(type, text):
			self.i += 1
			return next
		return None

	# Consumes the next token and returns it if it matches the type and/or text. Returns an error if
	# it doesn't.
	def expect(self, type: str=None, text: str=None) -> Node | Token:
		next = self.nextToken
		if self.peek(type, text):
			self.i += 1
			return next
		
		message = f"Expected {type}."
		if text:
			message = f"Expected `{type}`."
		return Node(message)
	
	# Initializes the parser and parses a list of tokens.
	def parse(self, tokens: list[Token]) -> Node:
		self.tokens = tokens
		self.i = 0
		return self.parseInfix(0)
	
	# Parses an infix expression.
	def parseInfix(self, precedence: int) -> Node:
		precedences = {
			"+",
			"-",
			"*",
			"/",
			"%",
			"&",
			"|",
			"^",
			"~",
			"==",
			"!=",
			">=",
			"<=",
			">",
			"<",
		}
		
		# Parse the first operand.
		left = self.parseBasic()
		if not left:
			return None
		
		# Keep parsing operands while the next operator is >= the minimum precedence.
		children = [left]
		while self.peek(type="operator") and self.nextToken.text in precedences and precedences[self.nextToken.text] >= precedence:
			children.append(self.accept())
			right = self.parseInfix(precedences[self.lastToken.text] + 1)
			if not right:
				children.append(Node("Expected operand for infix operator."))
				break
			children.append(right)

		if len(children) > 1:
			return Node("infix expression", *children)
		return children[0]
	
	# Parses an atom or a parenthesized expression.
	def parseBasic(self) -> Node:
		# Parse numbers.
		if self.peek(type="number"):
			return Node("atom", self.accept())
		
		# Parse identifiers.
		result = None
		if self.peek(type="identifier"):
			result = Node("atom", self.accept())

		# Parse tuples or function call arguments.
		while self.peek(text="("):
			parenthesized = self.parseParenthesizedExpression()
			if not parenthesized:
				return None
			
			if result:
				result = Node("function call", result, parenthesized)
			else:
				result = parenthesized
		return result

	# Parses a parenthesized expression.
	def parseParenthesizedExpression(self) -> Node:
		if self.accept(text="("):
			children = [self.parseInfix(0)]
			while self.accept(text=","):
				child = self.parseInfix(0)
				if not child:
					break
				children.append(child)

			if self.accept(text=")"):
				return Node("comma list", *children) if len(children) > 1 else children[0]
			# TODO: Do better error handling here.
			return Node("Expected `)`.")
		return None

# Turns a list of tokens into a syntax tree.
def parse(tokens: list[Token]) -> Node:
	return Parser().parse(tokens)
"""
