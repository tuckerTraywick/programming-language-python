from lexer import *

# A node in the parse tree.
class Node:
	def __init__(self, type, *children):
		self.type = type
		self.children = list(children)

	def __repr__(self):
		# If the node is an error, don't print its children.
		if self.type == "error":
			return f"Parsing error: {self.children[0]}"
		return f"{self.type}({', '.join(map(str, self.children))})"

	# Prints a readable multi-line representation of the node and its children.
	def prettyPrint(self, indentation=0):
		if self.type == "error":
			print(indentation*"| " + self.children[0])
			return
		
		print(indentation*"| " + self.type)
		for child in self.children:
			child.prettyPrint(indentation + 1)

	# Returns true if the node contains something.
	def hasData(self):
		return bool(self.type or self.children)

# A parser that turns tokens into a syntax tree.
class Parser:
	def reset(self, tokens):
		self.tokens = tokens
		self.tokenIndexStack = [0]
		self.tree = Node("program")
		self.currentNodeStack = [self.tree]

	@property
	def tokenIndex(self):
		return self.tokenIndexStack[-1]
	
	@tokenIndex.setter
	def tokenIndex(self, index):
		self.tokenIndexStack[-1] = index

	@property
	def currentToken(self):
		if self.hasTokens():
			return self.tokens[self.tokenIndex]
		return None
	
	@property
	def currentNode(self):
		return self.currentNodeStack[-1]

	def hasTokens(self):
		return self.tokenIndex < len(self.tokens)
	
	def beginNode(self, type):
		self.tokenIndexStack.append(self.tokenIndex)
		node = Node(type)
		self.currentNode.children.append(node)
		self.currentNodeStack.append(node)

	def endNode(self):
		top = self.tokenIndexStack.pop()
		self.tokenIndex = top
		return self.currentNodeStack.pop()

	def beginSequence(self):
		self.beginNode("sequence")

	def endSequence(self):
		self.tokenIndexStack.pop()
		node = self.currentNodeStack.pop()
		self.currentNode.children.pop()
		self.currentNode.children += node.children
		return node

	def addLeaf(self, leaf):
		self.currentNode.children.append(leaf)

	def backtrack(self, message=""):
		self.tokenIndexStack.pop()
		self.currentNodeStack.pop()
		self.currentNode.children.pop()
		if message:
			return self.emitError(message)
		return None
	
	def emitError(self, message):
		error = Node("error", message)
		self.currentNode.children.append(error)
		return Node("error", message)
	
	def recover(self, message="", type="", text=""):
		# Skip tokens.
		while self.hasTokens() and not self.peek(type, text):
			self.advance()
		return self.emitError(message)
	
	def recoverNode(self, message="", type="", text=""):
		self.recover(message, type, text)
		return self.endNode()

	def recoverSequence(self, message="", type="", text=""):
		self.recover(message, type, text)
		return self.endSequence()

	def advance(self):
		if self.hasTokens():
			self.tokenIndex += 1

	def peek(self, type="", text=""):
		if self.hasTokens() and self.currentToken.match(type, text):
			return self.currentToken
		return None
		
	def consume(self, type="", text=""):
		token = self.peek(type, text)
		if not token:
			return None
		self.advance()
		self.addLeaf(token)
		return token

	def parse(self, tokens):
		self.reset(tokens)
		self.parseBasic()
		return self.tree
	
	def parseBasic(self):
		self.beginNode("basic")
		while self.consume(text="["):
			if not self.parseBasic(): return self.recoverNode("Expected a basic expression.", text=";")
			if not self.consume(text="]"): return self.recoverNode("Expected a closing `]`.", text=";")
		self.parseLiteral()

		if not self.currentNode.children:
			return self.recoverNode("Expected a basic expression.", text=";")
		return self.endNode()

	def parseLiteral(self):
		return self.consume("number") or self.consume("identifier")
