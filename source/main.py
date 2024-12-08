from lexer import *
from parser import *

if __name__ == "__main__":
	text = """
	(a+b)(1*2+3)(2)
	"""
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))

	print("\n---- SYNTAX TREE ----")
	tree = parse(tokens)
	tree.prettyPrint()
