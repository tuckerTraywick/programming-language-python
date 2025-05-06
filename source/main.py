from lexer import *
from parser import *

if __name__ == "__main__":
	text = """
	func main() {
		if 1 {x = 1;} else if 1 {x = 2;}
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
