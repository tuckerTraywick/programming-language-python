class Symbol:
	pass

class Object:
	def __init__(self):
		self.symbolTable: dict[str, Symbol] = {}
