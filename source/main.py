from lexer import *

if __name__ == "__main__":
	text = """
	12 + 3=+ 45
	"""
	print(lex(text))
