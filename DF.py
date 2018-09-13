class DF:
	
	# x ==> list
	# y ==> list
	def __init__(self, x, y):
		self.__implicante = x
		self.__implicado = y
	
	# Getter y Setter usando decorators (anotaciones)
	@property
	def implicante(self):
		return self.__implicante
	
	@implicante.setter
	def implicante(self, value):
		self.__implicante = value
	
	# Getter y Setter usando redefinicion de la variable
	def getImplicado(self):
		return self.__implicado
	
	def setImplicado(self, value):
		self.__implicado = value
	
	implicado = property(getImplicado, setImplicado)


	def __hash__(self):
		return hash((frozenset(self.implicante), frozenset(self.implicado)))

	def __eq__(self, otro):
		if not isinstance(otro, DF):
			return False
		if otro == None:
			return False
		return not (set(self.implicante) != set(otro.implicante) or set(self.implicado) != set(otro.implicado))
	