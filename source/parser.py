from lexer import *

# A node in the parse tree.
@dataclass
class Node:
	type: str
	children: "list[Token | Node]"

	def __init__(self, type: str, *children: "Node | Token"):
		self.type = type
		self.children = children

	def __str__(self) -> str:
		# If the node is an error, don't print its children.
		if self.type.endswith("."):
			return f"Parsing error: {self.type}"
		return f"{self.type}({', '.join(map(str, self.children))})"
	
	# Prints a readable multi-line representation of the node and its children.
	def prettyPrint(self, indentation=0) -> str:
		print(indentation*"| " + self.type)
		if self.type.endswith("."):
			return

		for child in self.children:
			if isinstance(child, Token):
				print((indentation + 1)*"| " + str(child))
			else:
				child.prettyPrint(indentation + 1)


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
			"^": 40,
			"*": 30,
			"/": 30,
			"+": 20,
			"-": 20,
			"=": 10,
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
			expression = self.parseInfix(0)
			if self.accept(text=")"):
				return expression
			# TODO: Do better error handling here.
			return Node("Expected `)`.")
		return None

# Turns a list of tokens into a syntax tree.
def parse(tokens: list[Token]) -> Node:
	return Parser().parse(tokens)
