from dataclasses import dataclass

# A token or error given by the lexer.
@dataclass
class Token:
	type: str = ""
	text: str = ""

	def __repr__(self) -> str:
		# If the token is an error, print the error message.
		if self.type.endswith("."):
			return f"Lexing error: {self.type} `{self.text}`"
		return f"{self.type} `{self.text}`"
	
	def prettyPrint(self, indentation: int=0) -> str:
		print(indentation*"| " + str(self))

	def match(self, type: str, text: str) -> bool:
		if type and self.type != type:
			return False
		if text and self.text != text:
			return False
		return True
 
# Splits text into tokens.
def lex(text: str) -> list[Token]:
	skip = " \t\r\n"
	keywords = {
		"package",
	}
	operators = {
		"+",
		"-",
		"*",
		"/",
		"%",
		"&",
		"|",
		"^",
		"~",
		"==",
		"!=",
		">=",
		"<=",
		">",
		"<",
		"=",
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
	currentToken = Token()
	i = 0
	while i < len(text):
		# Skip whitespace.
		if text[i] in skip:
			i += 1
			continue
		# Lex numbers.
		elif text[i].isdigit():
			currentToken.type = "number"
			while i < len(text) and (text[i].isdigit() or text[i] == "_"):
				currentToken.text += text[i]
				i += 1
			tokens.append(currentToken)
		# Lex keywords/identifiers.
		elif text[i].isalpha() or text[i] == "_":
			while i < len(text) and (text[i].isalnum() or text[i] == "_"):
				currentToken.text += text[i]
				i += 1
			
			# Decide if the token is a keyword.
			if currentToken.text in keywords:
				currentToken.type = "keyword"
			else:
				currentToken.type = "identifier"
			tokens.append(currentToken)
		# Lex operators and reject invalid tokens.
		else:
			# Check if the token is an operator.
			for operator in operators:
				if text.startswith(operator, i):
					i += len(operator)
					tokens.append(Token("operator", operator))
					break
			# Consume invalid tokens.
			else:
				currentToken.type = "Invalid token."
				while i < len(text) and text[i] != "\n":
					currentToken.text += text[i]
					i += 1
				tokens.append(currentToken)

		# Prepare to lext the next token.
		currentToken = Token()
	return tokens
