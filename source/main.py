from lexer import *
from parser import *

def type(name):
	return Match(type=name)

def text(string):
	return Match(text=string)

def node(head, *choices):
	return Wrap(head, Choice(*choices) if len(choices) > 1 else choices[0])

def any(*choices):
	return Choice(*choices) if len(choices) > 1 else choices[0]

def call(rule):
	return Nonterminal(rule)

def maybe(parser):
	return Maybe(parser)

def rep0(parser):
	return Repeat0(parser)

def rep1(parser):
	return Repeat1(parser)

def error(message):
	return Error(message)

def recover(message, type="", text=""):
	return Recover(message, type, text, True)

parser = Parser("expression", {
	"expression": Expression(
		basicParser=call("basic"),
		prefixOperators={
			"+": 50,
			"-": 50,
		},
		infixOperators={
			"=": 10,
			"+": 20,
			"*": 40,
			"^": 60,
		},
	),

	"basic": node("basic",
		call("arrayDimensions") + maybe(type("identifier")) + rep0(call("parenthesizedExpressionList")),
		call("literal"),
	),

	"arrayDimensions": node("arrayDimensions",
		rep1(text("[") + call("expression") + text("]")),
	),

	"parenthesizedExpressionList": node("parenthesizedExpressionList",
		text("(") + maybe(call("expression")) + rep0(text(",") + call("expression")) + text(")"),
	),

	"literal": any(
		type("number"),
		type("identifier"),
	),
})

if __name__ == "__main__":
	text = "[a][b]a"
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))

	print("\n---- SYNTAX TREE ----")
	tree = parser.parse(tokens)
	print(tree)
