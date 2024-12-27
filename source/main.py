from lexer import *
from parser import *

parser = Parser("expression", {
	"expression": Expression(
		basicParser=Nonterminal("basic"),
		prefixOperators={
			"-": 30,
		},
		infixOperators={
			"+": 10,
			"*": 20,
			"^": 40,
		},
	),

	"basic": Choice(
		Match("number"),
		Sequence(Match(text="("), Nonterminal("expression"), Match(text=")")),
	),
})

if __name__ == "__main__":
	text = "4+4*(1 + 2)*3"
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))

	print("\n---- SYNTAX TREE ----")
	tree = parser.parse(tokens)
	print(tree)
