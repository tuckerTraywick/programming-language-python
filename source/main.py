from lexer import *

if __name__ == "__main__":
	text = "123@  asdf \n123"
	print("---- TOKENS ----")
	(tokens, lexingErrors) = lex(text)
	print("\n".join(map(str, tokens)))
	print("\n---- LEXING ERRORS ----")
	print("\n".join(map(str, lexingErrors)))
	# print("\n---- SYNTAX TREE ----")
	# tree = parser.parse(tokens)
	# tree.prettyPrint()
	# print()
	# print(parser.currentNodeStack)
	# print(parser.tokenIndexStack)
