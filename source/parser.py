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

# Base class for all parser combinators. Overloads operators.
class Combinator:
	def __add__(self, other):
		return Sequence(self, other)
	
	def __or__(self, other):
		return Choice(self, other)

# Matches the type or text of a single token.
class Match(Combinator):
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
class Sequence(Combinator):
	def __init__(self, *parsers):
		assert parsers, "You can't have an empty sequence."
		self.parsers = []
		# Flatten nested sequences.
		for parser in parsers:
			if isinstance(parser, Sequence):
				self.parsers += parser.parsers
			else:
				self.parsers.append(parser)

	def parse(self, tokens, index, parser):
		result = []
		for element in self.parsers:
			node, index = element.parse(tokens, index, parser)
			if node is None:
				return (None, index)
			
			if isinstance(node, list):
				result += node
			elif isinstance(node, (Token, Error)) or node.hasData():
				result.append(node)
		return (result, index)

# Matches one of many cases. Tries each case in order and backtracks when a case fails.
class Choice(Combinator):
	def __init__(self, *parsers):
		assert parsers, "You can't have an empty choice."
		self.parsers = []
		# Flatten nested choices.
		for parser in parsers:
			if isinstance(parser, Choice):
				self.parsers += parser.parsers
			else:
				self.parsers.append(parser)

	def parse(self, tokens, index, parser):
		for choice in self.parsers:
			result, newIndex = choice.parse(tokens, index, parser)
			if result:
				return (result, newIndex)
		return (None, index)

# Matches 0 or 1 occurrence of an item. Returns an empty node if it doesn't find a match.
class Maybe(Combinator):
	def __init__(self, parser):
		self.parser = parser

	def parse(self, tokens, index, parser):
		result, index = self.parser.parse(tokens, index, parser)
		if result is None:
			return (Node(""), index)
		return (result, index)

# Matches 0 or more occurrences of an item. Returns an empty list if no matches were found.
class Repeat0(Combinator):
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
class Repeat1(Combinator):
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
class Error(Combinator):
	def __init__(self, message):
		self.message = message

	def parse(self, tokens, index, parser):
		return (Node("error", self.message), index)

# Returns a node with a parsing error and eats advances until it sees the given token.
class Recover(Combinator):
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
class Expression(Combinator):
	def __init__(self, basicParser, prefixOperators, infixOperators):
		self.basicParser = basicParser
		self.prefixOperators = prefixOperators
		self.infixOperators = infixOperators

	def parsePrefixExpression(self, tokens, index, parser):
		if index < len(tokens) and tokens[index].text in self.prefixOperators:
			precedence = self.prefixOperators[tokens[index].text] + 1
			children = [tokens[index]]
			index += 1
			result, index = self.parse(tokens, index, parser, precedence)
			if result is None:
				return (result, index)
			children.append(result)
			return (Node("prefix expression", *children), index)
		return self.basicParser.parse(tokens, index, parser)

	def parse(self, tokens, index, parser, precedence=0):
		result, index = self.parsePrefixExpression(tokens, index, parser)
		if result is None:
			return (result, index)
		
		children = [result]
		while index < len(tokens) and self.infixOperators.get(tokens[index].text, -1) >= precedence:
			nextPrecedence = self.infixOperators[tokens[index].text] + 1
			children.append(tokens[index])
			index += 1
			result, index = self.parse(tokens, index, parser, nextPrecedence)
			if result is None:
				return (Node("error", "Expected operand for infix operator."), index)
			children.append(result)

		if len(children) > 1:
			return (Node("infix expression", *children), index)
		return (children[0], index)

# Matches another parsing rule.
class Nonterminal(Combinator):
	def __init__(self, rule):
		self.rule = rule

	def parse(self, tokens, index, parser):
		return parser.rules[self.rule].parse(tokens, index, parser)

# Wraps the result of a parser in a node.
class Wrap(Combinator):
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
