from lexer import *
from parser import *

if __name__ == "__main__":
	text = "1 + 2 + 4"
	print("---- TOKENS ----")
	(tokens, lexingErrors) = lex(text)
	print("\n".join(map(str, tokens)))
	print("\n---- LEXING ERRORS ----")
	print("\n".join(map(str, lexingErrors)))
	print("\n---- SYNTAX TREE ----")
	(tree, errors) = parse(tokens)
	tree.prettyPrint()
