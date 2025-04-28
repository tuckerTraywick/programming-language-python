class Token:
	def __init__(self, type: str, text: str):
		self.type = type
		self.text = text

	def __repr__(self):
		return f"{self.type} `{self.text}`"

def lex(text: str) -> tuple[list[Token], list[Token]] | None:
	whitespace: str = " \t\r\n"
	keywords: set[str] = {
		"namespace",
		"using",
		"pub",
		"inline",
		"static",
		"var",
		"func",
		"struct",
		"trait",
		"cases",
		"mut",
		"owned",
		"weak",
		"raw",
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
		"is",
		"as",
		"and",
		"or",
		"xor",
		"not",
	}
	operators: set[str] = {
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
		"=",
		"!=",
		">>=",
		">>"
		">=",
		">",
		"<<=",
		"<<",
		"<=",
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

	tokens: list[Token] = []
	errors: list[Token] = []
	currentToken: str = ""
	i: int = 0
	while i < len(text):
		if text[i] in whitespace:
			i += 1
			continue
		
		# Lex a number.
		if text[i].isdigit():
			while i < len(text) and text[i].isdigit():
				currentToken += text[i]
				i += 1
			tokens.append(Token("number", currentToken))
			currentToken = ""
		# Lex a character.
		elif text[i] == "'":
			currentToken += text[i]
			i += 1
			while i < len(text) and text[i] != "'" and text[i] != "\n":
				if text.startswith("\\'", i):
					currentToken += "\\'"
					i += 2
				else:
					currentToken += text[i]
					i += 1

			if i < len(text) and text[i] == "'":
				currentToken += "'"
				i += 1
				tokens.append(Token("character", currentToken))
			else:
				tokens.append(Token("Unclosed single quote.", currentToken))
				errors.append(tokens[-1])
			currentToken = ""
		# Lex a string.
		elif text[i] == '"':
			currentToken += text[i]
			i += 1
			while i < len(text) and text[i] != '"' and text[i] != "\n":
				if text.startswith('\\"', i):
					currentToken += '\\"'
					i += 2
				else:
					currentToken += text[i]
					i += 1

			if i < len(text) and text[i] == '"':
				currentToken += '"'
				i += 1
				tokens.append(Token("string", currentToken))
			else:
				tokens.append(Token("Unclosed double quote.", currentToken))
				errors.append(tokens[-1])
			currentToken = ""
		# Lex an identifier or keyword.
		elif text[i].isalpha() or text[i] == "_":
			while i < len(text) and (text[i].isalnum() or text[i] == "_"):
				currentToken += text[i]
				i += 1
			tokens.append(Token(currentToken if currentToken in keywords else "identifier", currentToken))
			currentToken = ""
		# Lex an operator.
		else:
			for operator in operators:
				if text.startswith(operator, i):
					tokens.append(Token(operator, operator))
					i += len(operator)
					break
			else:
				while i < len(tokens) and text[i] != "\n":
					currentToken += text[i]
					i += 1
				tokens.append(Token("Invalid token.", currentToken))
				errors.append(tokens[-1])
				currentToken = ""
	return (tokens, errors)
