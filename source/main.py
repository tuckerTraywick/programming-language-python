from lexer import *
from parser import *

if __name__ == "__main__":
	text = """
	trait Color {
		r uint8;
		g uint8;
		b uint8;
	} cases {
		red; green; blue;
		struct Rgb
	}
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
