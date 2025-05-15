from lexer import *
from parser import *
from object import *

if __name__ == "__main__":
	text = """ pub namespace hello; pub var a Int32; """
	(tokens, lexerErrors) = lex(text)
	print("---- TOKENS ----")
	print("\n".join(map(str, tokens)))
	print("\n---- LEXER ERRORS ----")
	print("\n".join(map(str, lexerErrors)))
	(tree, parserErrors) = parse(tokens)
	print("\n---- SYNTAX TREE ----")
	tree.prettyPrint()
	print("\n---- PARSER ERRORS ----")
	print("\n".join(map(str, parserErrors)))

	print("\n---- SYMBOLS ----")
	(object, compilerErrors) = validate(tree)
	for name in object.publicSymbols.keys():
		print(f"{name}: {str(object.getPublicSymbol(name))}")
	for name in object.privateSymbols.keys():
		print(f"{name}: {str(object.getPrivateSymbol(name))}")
	print("\n---- COMPILER ERRORS ----")
	for error in compilerErrors:
		print(error)	
