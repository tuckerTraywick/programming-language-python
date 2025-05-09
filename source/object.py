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

	def __str__(self) -> str:
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
