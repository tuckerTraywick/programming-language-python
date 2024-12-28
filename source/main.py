from lexer import *
from parser import *

def type(name):
	return Match(type=name)

def text(string):
	return Match(text=string)

def node(*choices):
	return Wrap("", Choice(*choices) if len(choices) > 1 else choices[0])

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

	"basic": node(
		rep1(call("arrayIndex")) + maybe(call("literal")) + rep0(call("functionArguments") | call("arrayIndex") | call("fieldAccess")),
		call("literal") + rep0(call("functionArguments") | call("arrayIndex") | call("fieldAccess")),
		rep1(call("functionArguments") | call("arrayIndex") | call("fieldAccess")),
	),

	"arrayIndex": node(
		text("[") + maybe(call("expression")) + text("]"),
	),

	"functionArguments": node(
		text("(") + maybe(call("functionArgument")) + rep0(text(",") + call("functionArgument")) + text(")"),
	),

	"functionArgument": node(
		maybe(type("identifier") + text("=")) + call("expression"),
	),

	"fieldAccess": node(
		text(".") + type("identifier"),
	),

	"literal": any(
		type("number"),
		type("identifier"),
	),
})

if __name__ == "__main__":
	text = "(List)[](1, 2, 3)()"
	
	print("---- TOKENS ----")
	tokens = lex(text)
	print("\n".join(map(str, lex(text))))

	print("\n---- SYNTAX TREE ----")
	tree = parser.parse(tokens)
	print(tree)
