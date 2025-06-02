from typing import Any
from lexer import *
from parser import *

class CompilerError:
	def __init__(self, message):
		self.message = message

	def __repr__(self):
		return self.message

class Symbol:
	def __init__(self, name, visibility, type, value):
		self.name = name
		self.visibility = visibility
		self.type = type
		self.value = value

	def __repr__(self):
		return self.name
	
	def __eq__(self, other):
		return self.visibility == other.visibility and self.name == other.name and self.type == other.type 

class Object:
	def __init__(self):
		self.publicSymbols = {}
		self.privateSymbols = {}

	def getPublicSymbol(self, name):
		identifiers = name.split(".")
		namespace = self.publicSymbols
		for identifier in identifiers:
			if identifier not in namespace:
				return None
			namespace = namespace[identifier]
		return namespace

	def getPrivateSymbol(self, name):
		identifiers = name.split(".")
		namespace = self.privateSymbols
		for identifier in identifiers:
			if identifier not in namespace:
				return None
			namespace = namespace[identifier]
		return namespace
	
	def getSymbol(self, name):
		symbol = self.getPublicSymbol(name)
		if symbol is not None:
			return symbol
		return self.getPrivateSymbol(name)
	
	def addPublicSymbol(self, name, value):
		if self.getPublicSymbol(name) is not None:
			return True
		identifiers = name.split(".")
		namespace = self.publicSymbols
		for identifier in identifiers[:-1]:
			namespace[identifier] = {}
			namespace = namespace[identifier]
		namespace[identifiers[-1]] = value
		return False
	
	def addPrivateSymbol(self, name, value):
		if self.getPrivateSymbol(name) is not None:
			return True
		identifiers = name.split(".")
		namespace = self.privateSymbols
		for identifier in identifiers[:-1]:
			namespace[identifier] = {}
			namespace = namespace[identifier]
		namespace[identifiers[-1]] = value
		return False

class Scope:
	def __init__(self):
		self.symbols = {}

	def getSymbol(self, name):
		return self.symbols.get(name)

	def addSymbol(self, symbol):
		if self.getSymbol(symbol.name) is not None:
			return True
		self.symbols[symbol.name] = symbol

class Environment:
	def __init__(self):
		self.scopes = []

	def pushScope(self):
		self.scopes.append(Scope())
	
	def popScope(self):
		self.scopes.pop()

	def getSymbol(self, name):
		for i in range(len(self.scopes) - 1, -1, -1):
			symbol = self.scopes[i].getSymbol(name)
			if symbol is not None:
				return symbol
		return None
	
	def addSymbol(self, symbol):
		if self.getSymbol(symbol.name) is not None:
			return True
		self.scopes[-1].addSymbol(symbol)
		return False

class Visitor:
	def __init__(self):
		self.object = None
		self.environment = None
		self.errors = []
		self.currentNamespace = ""

	def resolveSymbol(self, name):
		value = self.environment.getSymbol(name)
		if value is not None:
			return value
		value = self.object.getPrivateSymbol(name)
		if value is not None:
			return value
		return self.object.getPublicSymbol(name)

	def validateProgramStatement(self, tree):
		match tree.type:
			case "namespace statement":
				self.currentNamespace = qualifiedNameToStr(tree.children[-2])
				if self.object.getSymbol(self.currentNamespace) is not None:
					self.errors.append(CompilerError(f"Redefinition of namespace `{self.currentNamespace}`."))
					return True
				if tree.children[0].text == "pub":
					self.object.addPublicSymbol(self.currentNamespace, {})
				else:
					self.object.addPrivateSymbol(self.currentNamespace, {})
			case "using statement":
				pass
			case "variable definition":
				# pub var name type = value ;
				if tree.children[0].text == "pub":
					qualifiedName = self.currentNamespace + "." + tree.children[2].text
					type = tree.children[3]
					value = None
					if len(tree.children) >= 7:
						value = tree.children[5]
					if self.object.getSymbol(qualifiedName):
						self.errors.append(CompilerError(f"Redefinition of symbol `{qualifiedName}`."))
						return True
					self.object.addPublicSymbol(qualifiedName, Symbol(qualifiedName, "pub", type, value))
				# var name type = value ;
				else:
					qualifiedName = self.currentNamespace + "." + tree.children[1].text
					type = tree.children[2]
					value = None
					if len(tree.children) >= 6:
						value = tree.children[4]
					if self.object.getSymbol(qualifiedName):
						self.errors.append(CompilerError(f"Redefinition of symbol `{qualifiedName}`."))
						return True
					self.object.addPrivateSymbol(qualifiedName, Symbol(qualifiedName, "priv", type, value))
			case "function definition":
				# pub func name(arg type) type {body}
				# 0   1    2   3          4    5
				if tree.children[0].text == "pub":
					qualifiedName = self.currentNamespace + "." + tree.children[2].text
					arguments = tree.children[3]
					returnType = tree.children[4]
					body = tree.children[5]
					if self.object.getSymbol(qualifiedName):
						self.errors.append(CompilerError(f"Redefinition of symbol `{qualifiedName}`."))
						return True
				# func name(arg type) type {body}
				# 0    1   2          3    4 
				else:
					qualifiedName = self.currentNamespace + "." + tree.children[1].text
					arguments = tree.children[2]
					returnType = tree.children[3]
					body = tree.children[4]
					if self.object.getSymbol(qualifiedName):
						self.errors.append(CompilerError(f"Redefinition of symbol `{qualifiedName}`."))
						return True
		return False

	def validate(self, tree):
		self.object = Object()
		self.environment = Environment()
		self.environment.pushScope()
		self.errors = []
		self.currentNamespace = ""
		if isinstance(tree, Node):
			match tree.type:
				case "program":
					for child in tree.children:
						if self.validateProgramStatement(child):
							return True
		return False

def qualifiedNameToStr(name):
	return ".".join(child.text for child in name.children)

def validate(tree):
	visitor = Visitor()
	visitor.validate(tree)
	return (visitor.object, visitor.errors)
