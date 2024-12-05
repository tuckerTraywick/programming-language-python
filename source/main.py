from lexer import *
from parser import *

if __name__ == "__main__":
	text = """
	x = 1
	f(x) = x + 1
	"""
	
	tokens = lex(text)
	print("---- TOKENS ----")
	print("\n".join(map(str, lex(text))))

	tree = parse(tokens)
	print("\n---- SYNTAX TREE ----")
	print(Node("program", Token("identifier", "a")))
