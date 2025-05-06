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

	def parseGenericArgument(self) -> bool:
		return self.parseType() or self.parseInfixExpression(0)

	def parseGenericArguments(self) -> bool:
		self.beginNode("generic arguments")
		if not self.consumeTokenText("generic <"): return self.backtrack()
		while self.parseGenericArgument():
			if not self.consumeTokenText(","): break
		if not self.consumeTokenText(">"): return self.emitError("Unclosed angle bracket.")
		return self.endNode()

	def parseBasicType(self) -> bool:
		self.beginNode("basic type")
		if not self.consumeTokenType("identifier"): return self.backtrack()
		while self.consumeTokenText("."):
			if not self.consumeTokenType("identifier"): return self.emitError("Expected an identifier.")
		self.parseGenericArguments()
		return self.endNode()
	
	def parseMutableType(self) -> bool:
		self.beginNode("mutable type")
		if not self.consumeTokenText("mut"): return self.backtrack()
		self.parseType()
		return self.endNode()

	def parseFunctionParameter(self) -> bool:
		self.beginNode("function parameter")
		if not self.consumeTokenType("identifier"): return self.backtrack()
		self.parseType()
		return self.endNode()
	
	def parseFunctionParameters(self) -> bool:
		self.beginNode("function parameters")
		if not self.consumeTokenText("("): return self.backtrack()
		while self.parseFunctionParameter():
			if not self.consumeTokenText(","): break
		if not self.consumeTokenText(")"): return self.emitError("Unclosed parenthesis.")
		return self.endNode()

	def parseFunctionType(self) -> bool:
		self.beginNode("function type")
		if not self.consumeTokenText("func"): return self.backtrack()
		# TODO: Accept function types without parameters?
		if not self.parseFunctionParameters(): return self.emitError("Expected function parameters")
		self.parseType()
		return self.endNode()
	
	def parsePointerType(self) -> bool:
		self.beginNode("pointer type")
		if not self.consumeTokenText("&"): return self.backtrack()
		self.parseType()
		return self.endNode()
	
	def parseArrayType(self) -> bool:
		self.beginNode("array type")
		if not self.consumeTokenText("["): return self.backtrack()
		self.parseInfixExpression(0)
		if not self.consumeTokenText("]"): return self.emitError("Unclosed square bracket.")
		self.parseType()
		return self.endNode()

	def parseTupleType(self) -> bool:
		self.beginNode("tuple type")
		if not self.consumeTokenText("("): return self.backtrack()
		while self.parseType():
			if not self.consumeTokenText(","): break
		if not self.consumeTokenText(")"): return self.emitError("Unclosed parenthesis.")
		return self.endNode()

	def parseType(self) -> bool:
		if self.parseTupleType(): return True
		if self.parseArrayType(): return True
		if self.parsePointerType(): return True
		if self.parseFunctionType(): return True
		if self.parseMutableType(): return True
		if self.parseBasicType(): return True
		return False
	
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
	
	def parseQualifiedName(self) -> bool:
		self.beginNode("qualified name")
		if not self.consumeTokenType("identifier"): return self.backtrack()
		while self.consumeTokenText("."):
			if self.consumeTokenText("*"): break
			if not self.consumeTokenType("identifier"): return self.emitError("Expected an identifier.")
		return self.endNode()
	
	def parseExpressionOrAssignment(self) -> bool:
		self.beginNode("expression or assignment")
		if not self.parseInfixExpression(0): return self.backtrack()
		self.parseAssignment()
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()
	
	def parseReturnStatement(self) -> bool:
		self.beginNode("return statement")
		if not self.consumeTokenText("return"): return self.backtrack()
		self.parseInfixExpression(0)
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()

	def parseContinueStatement(self) -> bool:
		self.beginNode("continue statement")
		if not self.consumeTokenText("continue"): return self.backtrack()
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()

	def parseBreakStatement(self) -> bool:
		self.beginNode("break statement")
		if not self.consumeTokenText("break"): return self.backtrack()
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()

	def parseForLoop(self) -> bool:
		self.beginNode("for loop")
		if not self.consumeTokenText("for"): return self.backtrack()
		if not self.consumeTokenType("identifier"): return self.emitError("Expected a variable name.")
		self.parseType()
		if not self.consumeTokenText("in"): return self.emitError("Expected `in` statement.")
		if not self.parseInfixExpression(0): return self.emitError("Expected an expression.")
		if not self.parseBlock(): return self.emitError("Expected a block.")
		return self.endNode()
	
	def parseWhileLoop(self) -> bool:
		self.beginNode("while loop")
		self.consumeTokenText("do")
		if not self.consumeTokenText("while"): return self.backtrack()
		if not self.parseInfixExpression(0): return self.emitError("Expected an expression.")
		if not self.parseBlock(): return self.emitError("Expected a block.")
		return self.endNode()
	
	def parseElse(self) -> bool:
		self.beginNode("else block")
		if not self.consumeTokenText("else"): return self.backtrack()
		if not self.parseBlock(): return self.emitError("Expected a block.")
		return self.endNode()
	
	def parseElseIf(self) -> bool:
		self.beginNode("else-if block")
		if not self.consumeTokenText("else"): return self.backtrack()
		if not self.consumeTokenText("if"): return self.backtrack()
		if not self.parseInfixExpression(0): return self.emitError("Expected an expression.")
		if not self.parseBlock(): return self.emitError("Expected a block.")
		return self.endNode()
	
	def parseIfStatement(self) -> bool:
		self.beginNode("if statement")
		if not self.consumeTokenText("if"): return self.backtrack()
		if not self.parseInfixExpression(0): return self.emitError("Expected an expression.")
		if not self.parseBlock(): return self.emitError("Expected a block.")
		while self.parseElseIf(): pass
		self.parseElse()
		return self.endNode()

	def parseBlockStatement(self) -> bool:
		if self.parseUsingStatement(): return True
		if self.parseVariableDefinition(False): return True
		if self.parseFunctionDefinition(False): return True
		if self.parseMethodDefinition(False): return True
		if self.parseStructDefinition(False): return True
		if self.parseTraitDefinition(False): return True
		if self.parseBlock(): return True
		if self.parseIfStatement(): return True
		if self.parseWhileLoop(): return True
		if self.parseForLoop(): return True
		if self.parseBreakStatement(): return True
		if self.parseContinueStatement(): return True
		if self.parseReturnStatement(): return True
		if self.parseExpressionOrAssignment(): return True
		return False
	
	def parseBlock(self) -> bool:
		self.beginNode("block")
		if not self.consumeTokenText("{"): return self.backtrack()
		while self.parseBlockStatement(): pass
		if not self.consumeTokenText("}"): return self.emitError("Unclosed curly brace.")
		return self.endNode()
	
	def parseEnumCase(self) -> bool:
		self.beginNode("enum case")
		if not self.consumeTokenType("identifier"): return self.backtrack()
		self.parseAssignment()
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()

	def parseTypeCase(self) -> bool:
		if self.parseUsingStatement(): return True
		if self.parseStructDefinition(False): return True
		if self.parseTraitDefinition(False): return True
		return self.parseEnumCase()
	
	def parseTypeCases(self) -> bool:
		self.beginNode("type cases")
		if not self.consumeTokenText("cases"): return self.backtrack()
		if not self.consumeTokenText("{"): return self.emitError("Expected type cases.")
		if self.consumeTokenText("default") and not self.parseTypeCase(): return self.emitError("Expected a type case.")
		while self.parseTypeCase(): pass
		if not self.consumeTokenText("}"): return self.emitError("Unclosed curly brace.")
		return self.endNode()
	
	def parseUsingType(self) -> bool:
		self.beginNode("using type")
		if not self.consumeTokenText("using"): return self.backtrack()
		if not self.parseType(): return self.emitError("Expected a type.")
		while self.consumeTokenText(","):
			if not self.parseType(): return self.emitError("Expected a type.")
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()

	def parseStructField(self) -> bool:
		self.beginNode("struct field")
		self.consumeTokenText("pub")
		if not self.consumeTokenType("identifier"): return self.backtrack()
		if not self.parseType(): return self.emitError("Expected a type.")
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()

	def parseStructBody(self) -> bool:
		self.beginNode("struct body")
		if not self.consumeTokenText("{"): return self.backtrack()
		while self.parseStructField() or self.parseUsingType(): pass
		if not self.consumeTokenText("}"): return self.emitError("Unclosed curly brace.")
		return self.endNode()
	
	def parseGenericTypeParameter(self) -> bool:
		self.beginNode("type parameter")
		if not self.consumeTokenText("type", "struct", "trait"): return self.backtrack()
		if not self.consumeTokenType("identifier"): return self.emitError("Expected an identifier.")
		return self.endNode()

	def parseGenericParameter(self) -> bool:
		if self.parseGenericTypeParameter(): return True
		return self.parseType()
	
	def parseGenericParameters(self) -> bool:
		self.beginNode("generic parameters")
		if not self.consumeTokenText("generic <"): return self.backtrack()
		while self.parseGenericParameter():
			if not self.consumeTokenText(","): break
		if not self.consumeTokenText(">"): return self.emitError("Unclosed angle bracket.")
		return self.endNode()
	
	def parseTraitDefinition(self, allowPub: bool=True) -> bool:
		self.beginNode("trait definintion")
		if not allowPub and self.consumeTokenText("pub"): return self.emitError("Access modifier not allowed here.")
		if not self.consumeTokenText("trait"): return self.backtrack()
		if not self.consumeTokenType("identifier"): return self.emitError("Expected a struct name.")
		self.parseGenericParameters()
		self.parseStructBody()
		self.parseTypeCases()
		self.consumeTokenText(";")
		return self.endNode()
	
	def parseStructDefinition(self, allowPub: bool=True) -> bool:
		self.beginNode("struct definintion")
		if not allowPub and self.consumeTokenText("pub"): return self.emitError("Access modifier not allowed here.")
		if not self.consumeTokenText("struct"): return self.backtrack()
		if not self.consumeTokenType("identifier"): return self.emitError("Expected a struct name.")
		self.parseGenericParameters()
		self.parseStructBody()
		self.parseTypeCases()
		self.consumeTokenText(";")
		return self.endNode()

	def parseMethodDefinition(self, allowPub: bool=True) -> bool:
		self.beginNode("method definition")
		if not allowPub and self.consumeTokenText("pub"): return self.emitError("Access modifier not allowed here.")
		if not self.consumeTokenText("method"): return self.backtrack()
		if not self.consumeTokenType("identifier"): return self.emitError("Expected a method name.")
		self.parseGenericParameters()
		if not self.parseFunctionParameters(): return self.emitError("Expected method parameters.")
		self.parseType()
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()
	
	def parseFunctionDefinition(self, allowPub: bool=True) -> bool:
		self.beginNode("function definition")
		if not allowPub and self.consumeTokenText("pub"): return self.emitError("Access modifier not allowed here.")
		if not self.consumeTokenText("func"): return self.backtrack()
		if not self.consumeTokenType("identifier"): return self.emitError("Expected a function name.")
		self.parseGenericParameters()
		if not self.parseFunctionParameters(): return self.emitError("Expected function parameters.")
		self.parseType()
		if not self.parseBlock(): return self.emitError("Expected a function body.")
		return self.endNode()
	
	def parseAssignment(self) -> bool:
		self.beginNode("assignment")
		if not self.consumeTokenText("="): return self.backtrack()
		if not self.parseInfixExpression(0): return self.emitError("Expected an expression.")
		return self.endNode()
	
	def parseVariableDefinition(self, allowPub: bool=True) -> bool:
		self.beginNode("variable definition")
		if not allowPub and self.consumeTokenText("pub"): return self.emitError("Access modifier not allowed here.")
		if not self.consumeTokenText("var"): return self.backtrack()
		if not self.consumeTokenType("identifier"): return self.emitError("Expected a variable name.")
		if not self.parseType():
			if not self.parseAssignment(): return self.emitError("Expected a type or an assignment.")
		else:
			self.parseAssignment()
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()
	
	def parseUsingStatement(self) -> bool:
		self.beginNode("using statement")
		if not self.consumeTokenText("using"): return self.backtrack()
		if not self.parseQualifiedName(): return self.emitError("Expected a qualified name.")
		while self.consumeTokenText(","):
			if not self.parseQualifiedName(): return self.emitError("Expected a qualified name.")
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()

	def parseProgramStatement(self) -> bool:
		if self.parseUsingStatement(): return True
		if self.parseVariableDefinition(): return True
		if self.parseFunctionDefinition(): return True
		if self.parseMethodDefinition(): return True
		if self.parseStructDefinition(): return True
		if self.parseTraitDefinition(): return True
		return False

	def parseNamespaceStatement(self) -> bool:
		self.beginNode("namespace statement")
		self.consumeTokenText("pub")
		if not self.consumeTokenText("namespace"): return self.backtrack()
		if not self.parseQualifiedName(): return self.emitError("Expected a namespace name.")
		if self.currentNode.children[-1].children[-1].text == "*": return self.emitError("Namespace name cannot contain `*`.")
		if not self.consumeTokenText(";"): return self.emitError("Expected a semicolon.")
		return self.endNode()
	
	def parseProgram(self):
		self.beginNode("program")
		self.parseNamespaceStatement()
		while self.parseProgramStatement(): pass
		if self.currentTokenIndex < len(self.tokens): return self.emitError("Tokens left after parsing.")
		self.endNode()

def parse(tokens: list[Token]) -> tuple[Node, list[ParsingError]]:
	parser: _Parser = _Parser(tokens)
	parser.parseProgram()
	return (parser.tree, parser.errors)
