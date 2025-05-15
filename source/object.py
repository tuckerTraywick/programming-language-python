from typing import Any
from lexer import *
from parser import *

class CompilerError:
	def __init__(self, message: str):
		self.message = message

	def __repr__(self) -> str:
		return self.message

class Symbol:
	def __init__(self, name: str, visibility: str, type: str, value: Token | Node):
		self.name = name
		self.visibility = visibility
		self.type = type
		self.value = value

	def __repr__(self) -> str:
		return self.name
	
	def __eq__(self, other: "Symbol") -> bool:
		return self.visibility == other.visibility and self.name == other.name and self.type == other.type 

class Object:
	def __init__(self):
		self.publicSymbols: dict[str, Any] = {}
		self.privateSymbols: dict[str, Any] = {}

	def getPublicSymbol(self, name: str) -> Any | None:
		identifiers: list[str] = name.split(".")
		namespace = self.publicSymbols
		for identifier in identifiers:
			if identifier not in namespace:
				return None
			namespace = namespace[identifier]
		return namespace

	def getPrivateSymbol(self, name: str) -> Any | None:
		identifiers: list[str] = name.split(".")
		namespace = self.privateSymbols
		for identifier in identifiers:
			if identifier not in namespace:
				return None
			namespace = namespace[identifier]
		return namespace
	
	def getSymbol(self, name: str) -> Any | None:
		symbol = self.getPublicSymbol(name)
		if symbol is not None:
			return symbol
		return self.getPrivateSymbol(name)
	
	def addPublicSymbol(self, name: str, value: Any) -> bool:
		if self.getPublicSymbol(name) is not None:
			return True
		identifiers: list[str] = name.split(".")
		namespace = self.publicSymbols
		for identifier in identifiers[:-1]:
			namespace[identifier] = {}
			namespace = namespace[identifier]
		namespace[identifiers[-1]] = value
		return False
	
	def addPrivateSymbol(self, name: str, value: Any) -> bool:
		if self.getPrivateSymbol(name) is not None:
			return True
		identifiers: list[str] = name.split(".")
		namespace = self.privateSymbols
		for identifier in identifiers[:-1]:
			namespace[identifier] = {}
			namespace = namespace[identifier]
		namespace[identifiers[-1]] = value
		return False

class Scope:
	def __init__(self):
		self.symbols: map[str, Symbol] = {}

	def getSymbol(self, name: str) -> Symbol | None:
		return self.symbols.get(name)

	def addSymbol(self, symbol: Symbol) -> bool:
		if self.getSymbol(symbol.name) is not None:
			return True
		self.symbols[symbol.name] = symbol

class Environment:
	def __init__(self):
		self.scopes: list[Scope] = []

	def pushScope(self):
		self.scopes.append(Scope())
	
	def popScope(self):
		self.scopes.pop()

	def getSymbol(self, name: str) -> Any | None:
		for i in range(len(self.scopes) - 1, -1, -1):
			symbol = self.scopes[i].getSymbol(name)
			if symbol is not None:
				return symbol
		return None
	
	def addSymbol(self, symbol: Symbol) -> bool:
		if self.getSymbol(symbol.name) is not None:
			return True
		self.scopes[-1].addSymbol(symbol)
		return False

def resolveName(name: str, object: Object, environment: Environment) -> Any | None:
	pass

def qualifiedNameToStr(name: Node) -> str:
	return ".".join(child.text for child in name.children)

# Returns True on error.
def validateTree(tree: Node | Token,  object: Object, errors: list[CompilerError]) -> bool:
	if isinstance(tree, Node):
		match tree.type:
			case "program":
				for child in tree.children:
					if validateTree(child, object, errors):
						return True
			case "namespace statement":
				namespaceName = qualifiedNameToStr(tree.children[-2])
				if object.getSymbol(namespaceName) is not None:
					errors.append(CompilerError(f"Redefinition of namespace `{namespaceName}`."))
					return True
				if tree.children[0].text == "pub":
					object.addPublicSymbol(namespaceName, {})
				else:
					object.addPrivateSymbol(namespaceName, {})
	return False
