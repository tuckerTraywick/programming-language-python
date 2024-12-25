from lexer import *
from parser import *

parser = Sequence(Match(type="identifier"), Choice(Match(type="identifier"), Error("Expected an identifier.")))

if __name__ == "__main__":
	text = "a a"
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))

	print("\n---- SYNTAX TREE ----")
	tree = parse(tokens, parser)
	print(tree)
