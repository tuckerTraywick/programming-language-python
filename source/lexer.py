class LexerError:
	def __init__(self, message, text):
		self.message = message
		self.text = text

	def __repr__(self) :
		return f"{self.message} `{self.text}`"

class Token:
	def __init__(self, type, text):
		self.type = type
		self.text = text

	def __repr__(self):
		return f"{self.type} `{self.text}`"

def lex(text):
	whitespace = " \t\r\n"
	keywords = [
		"namespace",
		"using",
		"pub",
		# "inline",
		# "static",
		"var",
		"func",
		"method",
		"struct",
		"trait",
		"cases",
		"mut",
		# "owned",
		# "weak",
		# "raw",
		"if",
		"else",
		"do",
		"while",
		"for",
		"in",
		"thru",
		"until",
		"by",
		# "switch",
		# "case",
		"default",
		# "next",
		"break",
		"continue",
		"return",
		# "yield",
		"is",
		"isnot",
		"isa",
		"isnota",
		"as",
		"and",
		"or",
		"xor",
		"not",
		# "new",
		# "drop",
		# "move",
	]
	operators = [
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
		":",
		";",
	]
	lineComment = "//"

	tokens = []
	errors = []
	currentToken = ""
	i = 0
	while i < len(text):
		# Skip whitespace.
		if text[i] in whitespace:
			i += 1
			continue
		# Skip comments.
		if text.startswith(lineComment, i):
			while i < len(text) and text[i] != "\n":
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
				errors.append(LexerError("Unclosed single quote.", currentToken))
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
				errors.append(LexerError("Unclosed double quote.", currentToken))
			currentToken = ""
		# Lex an identifier or keyword.
		elif text[i].isalpha() or text[i] == "_":
			while i < len(text) and (text[i].isalnum() or text[i] == "_"):
				currentToken += text[i]
				i += 1
			tokens.append(Token("keyword" if currentToken in keywords else "identifier", currentToken))
			currentToken = ""
		# Lex an operator.
		else:
			for operator in operators:
				if text.startswith(operator, i):
					if operator == "<" and i > 0 and text[i-1] not in whitespace:
						tokens.append(Token("operator", "generic <"))
					else:
						tokens.append(Token("operator", operator))
					i += len(operator)
					break
			else:
				while i < len(text) and text[i] != "\n":
					currentToken += text[i]
					i += 1
				errors.append(LexerError("Invalid token.", currentToken))
				currentToken = ""
	return (tokens, errors)
