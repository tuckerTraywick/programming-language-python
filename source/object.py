class Symbol:
	def __init__(self, name: str, type: str):
		pass

class Object:
	def __init__(self):
		self.symbolTable: dict[str, Symbol] = {}
