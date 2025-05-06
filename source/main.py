from lexer import *
from parser import *

if __name__ == "__main__":
	text = """
	struct List<type T, int32> {
		x T;
	}
	func generic<type T>(x T) T {}
	"""
	(tokens, lexingErrors) = lex(text)
	print("---- TOKENS ----")
	print("\n".join(map(str, tokens)))
	print("\n---- LEXING ERRORS ----")
	print("\n".join(map(str, lexingErrors)))
	(tree, parsingErrors) = parse(tokens)
	print("\n---- SYNTAX TREE ----")
	tree.prettyPrint()
	print("\n---- PARSING ERRORS ----")
	print("\n".join(map(str, parsingErrors)))
