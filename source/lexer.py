class Token:
	def __init__(self, type, text):
		self.type = type
		self.text = text

	def __repr__(self):
		# If the token is an error, print the error message.
		if self.type.endswith("."):
			return f"Lexing error: {self.type} `{self.text}`"
		return f"{self.type} `{self.text}`"

def lex(text):
	whitespace = " \t\r\n"
	keywords = {
		"module",
		"import",
		"export",
		"pub",
		"inline",
		"static",
		"var",
		"func",
		"struct",
		"trait",
		"type",
		"alias",
		"mut",
		"owned",
		"weak",
		"if",
		"else",
		"do",
		"while",
		"for",
		"in",
		"thru",
		"until",
		"by",
		"switch",
		"case",
		"default",
		"next",
		"break",
		"continue",
		"return",
		"yield",
		"match",
		"is",
		"as",
		"and",
		"or",
		"xor",
		"not",
	}
	operators = {
		"+=",
		"+",
		"-=",
		"->",
		"-",
		"*=",
		"*",
		"/=",
		"/",
		"%=",
		"%",
		"&=",
		"&",
		"|=",
		"|",
		"^=",
		"^",
		"~=",
		"~",
		"==",
		"=>",
		"=",
		"!=",
		">=",
		">>",
		">",
		"<=",
		"<<",
		"<",
		"(",
		")",
		"[",
		"]",
		"{",
		"}",
		".",
		",",
		";",
	}

	tokens = []
	currentToken = ""
	i = 0
	while i < len(text):
		
	return tokens
