from lexer import *
from parser import *

parser = Parser()

if __name__ == "__main__":
	text = "1 ; a"
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))

	print("\n---- SYNTAX TREE ----")
	tree = parser.parse(tokens)
	print(tree)
	print(parser.currentNodeStack)
	print(parser.tokenIndexStack)
