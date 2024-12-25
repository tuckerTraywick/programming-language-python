from lexer import *
from parser import *

parser = Sequence(Recover("error", text=";"), Match(type="identifier"))

if __name__ == "__main__":
	text = "1 ; a"
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))

	print("\n---- SYNTAX TREE ----")
	tree = parse(tokens, parser)
	print(tree)
