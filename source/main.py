from lexer import *
from parser import *

parser = Parser()

if __name__ == "__main__":
	text = "[b[a]; 1 3"
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))
	print("\n---- SYNTAX TREE ----")
	tree = parser.parse(tokens)
	tree.prettyPrint()
	print()
	print(parser.currentNodeStack)
	print(parser.tokenIndexStack)
