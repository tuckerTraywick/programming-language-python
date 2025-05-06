from lexer import *

# An error encountered during parsing.
class ParsingError:
	def __init__(self, message: str):
		self.message = message

	def __repr__(self) -> str:
		return self.message

# A node in the parse tree.
class Node:
	def __init__(self, type: str, parent: "Node | None", *children: "Node"):
		self.type = type
		self.parent = parent
		self.children = list(children)

	def __repr__(self) -> str:
		return f"{self.type}({', '.join(map(str, self.children))})"

	# Prints a readable multi-line representation of the node and its children.
	def prettyPrint(self, indentation: int=0):
		print(indentation*"| " + self.type)
		for child in self.children:
			if isinstance(child, Node):
				child.prettyPrint(indentation + 1)
			else:
				print((indentation + 1)*"| " + str(child))

class _Parser:
	prefixPrecedences = {
		"(": 2000,
		"[": 2000,
		"*": 1300,
		"&": 1300,
		# "new",
		# "drop",
		# "move",
		"+": 1300,
		"-": 1300,
		"~": 1300,
		"not": 400,
	}
	infixPrecedences = {
		".": 1500,
		"(": 1500,
		")": 0,
		"[": 1500,
		"]": 0,
		"->": 1400,
		"as": 1200,
		"*": 1100,
		"/": 1100,
		"%": 1100,
		"+": 1000,
		"-": 1000,
		"<<": 900,
		">>": 900,
		"&": 800,
		"^": 700,
		"|": 600,
		"==": 500,
		"!=": 500,
		">=": 500,
		">": 500,
		"<=": 500,
		"<": 500,
		"is": 500,
		"isnot": 500,
		"isa": 500,
		"isnota": 500,
		"and": 300,
		"xor": 200,
		"or": 100,
	}

	def __init__(self, tokens: list[Token]):
		self.tokens = tokens
		self.currentTokenIndex: int = 0
		self.tree: Node = None
		self.currentNode: Node = self.tree
		self.errors: list[ParsingError] = []

	@property
	def currentToken(self) -> Token:
		return self.tokens[self.currentTokenIndex]

	def peekTokenType(self, *types: str) -> bool:
		return self.currentTokenIndex < len(self.tokens) and self.currentToken.type in types
	
	def peekTokenText(self, *texts: str) -> bool:
		return self.currentTokenIndex < len(self.tokens) and self.currentToken.text in texts

	def consumeTokenType(self, *types: str) -> bool:
		if self.peekTokenType(*types):
			self.currentNode.children.append(self.currentToken)
			self.currentTokenIndex += 1
			return True
		return False
	
	def consumeTokenText(self, *texts: str) -> bool:
		if self.peekTokenText(*texts):
			self.currentNode.children.append(self.currentToken)
			self.currentTokenIndex += 1
			return True
		return False

	def consumePrefixOperator(self, precedence: int) -> int:
		if self.peekTokenType("operator", "keyword", "bracket") and self.currentToken.text in self.prefixPrecedences and (newPrecedence := self.prefixPrecedences[self.currentToken.text]):
			self.consumeTokenType("operator", "keyword", "bracket")
			return newPrecedence
		return 0
	
	def consumeInfixOperator(self, precedence: int) -> int:
		if self.peekTokenType("operator", "keyword", "bracket") and self.currentToken.text in self.infixPrecedences and (newPrecedence := self.infixPrecedences[self.currentToken.text]) > precedence:
			self.consumeTokenType("operator", "keyword", "bracket")
			return newPrecedence
		return 0
	
	def beginNode(self, type: str) -> bool:
		if self.tree is None:
			self.tree = Node(type, None)
			self.currentNode = self.tree
			return True
		self.currentNode.children.append(Node(type, self.currentNode))
		self.currentNode = self.currentNode.children[-1]
		return True
	
	def endNode(self) -> bool:
		self.currentNode = self.currentNode.parent
		return True
	
	def backtrack(self) -> bool:
		self.endNode()
		if self.currentNode:
			self.currentNode.children.pop()
		return False
	
	def emitError(self, type: str) -> bool:
		self.errors.append(ParsingError(type))

	def parseType(self) -> bool:
		self.beginNode("type")
		if not self.consumeTokenType("identifier"): return self.backtrack()
		return self.endNode()

	def parseBasicExpression(self) -> bool:
		return self.consumeTokenType("number", "character", "string", "identifier")

	def parseCommaList(self) -> bool:
		# TODO: parse assignments here.
		if not self.parseInfixExpression(0):
			return False
		while self.consumeTokenText(","):
			self.parseInfixExpression(0)
		return True

	def parsePrefixExpression(self, precedence: int) -> bool:
		self.beginNode("prefix expression")
		# Parse a prefix expression or list.
		if (newPrecedence := self.consumePrefixOperator(precedence)):
			if self.currentNode.children[0].text == "(":
				self.parseCommaList()
				if not self.consumeTokenText(")"): return self.emitError("Unclosed parenthesis.")
			elif self.currentNode.children[0].text == "[":
				self.parseCommaList()
				if not self.consumeTokenText("]"): return self.emitError("Unclosed square bracket.")
			elif not self.parseInfixExpression(newPrecedence):
				return self.emitError("Expected an expression.")
			return self.endNode()

		# Parse a basic expression.
		if not self.parseBasicExpression(): return self.backtrack()
		
		if len(self.currentNode.children) == 1:
			child = self.currentNode.children[0]
			self.endNode()
			self.currentNode.children[-1] = child
			return True
		return self.endNode()

	def parseInfixExpression(self, precedence: int) -> bool:
		self.beginNode("infix expression")
		if not self.parsePrefixExpression(precedence): return self.backtrack()
		while (newPrecedence := self.consumeInfixOperator(precedence)):
			if self.currentNode.children[-1].text == "(":
				self.parseCommaList()
				if not self.consumeTokenText(")"): return self.emitError("Unclosed parenthesis.")
			elif self.currentNode.children[-1].text == "[":
				self.parseCommaList()
				if not self.consumeTokenText("]"): return self.emitError("Unclosed square bracket.")
			elif self.currentNode.children[-1].text == "as":
				if not self.parseType(): return self.emitError("Expected a type.")
			elif not self.parseInfixExpression(newPrecedence):
				return self.emitError("Expected an expression.")

		if len(self.currentNode.children) == 1:
			child = self.currentNode.children[0]
			self.endNode()
			self.currentNode.children[-1] = child
			return True
		return self.endNode()
	
	def parseProgram(self):
		self.beginNode("program")
		self.parseInfixExpression(0)
		self.endNode()

def parse(tokens: list[Token]) -> tuple[Node, list[ParsingError]]:
	parser: _Parser = _Parser(tokens)
	parser.parseProgram()
	return (parser.tree, parser.errors)
