from lexer import *
from parser import *

parser = Sequence(Match(type="identifier"), Maybe(Match(type="identifier")))

if __name__ == "__main__":
	text = "a 1 c"
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))

	print("\n---- SYNTAX TREE ----")
	tree = parse(tokens, parser)
	print(tree)
