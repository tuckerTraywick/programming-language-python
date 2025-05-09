from lexer import *
from parser import *

if __name__ == "__main__":
	text = """
	var a int32;
	func main() {
		var a uint32;
		var b uint32;
		for i uint32 in 0 {
			if a == b {
				break;
			}
			return x + 1;
		}
	}
	method f();
	func f() {}
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
