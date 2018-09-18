class R:
	
	# t ==> list
	# l ==> list
	# lx ==> list
	def __init__(self, t = None, l = None, lx = None, recubrimiento = None, claves = None):
		self.__dataT = t
		self.__dependencias = l
		self.__dfToValidate = lx
		self.__recubrimientoMinimo = recubrimiento
		self.__clavesCandidatas = claves
	
	@property
	def dataT(self):
		return self.__dataT
	
	@dataT.setter
	def dataT(self, value):
		self.__dataT = value
	
	@property
	def dependencias(self):
		return self.__dependencias
	
	@dependencias.setter
	def dependencias(self, value):
		self.__dependencias = value

	@property
	def dfToValidate(self):
		return self.__dfToValidate
	
	@dfToValidate.setter
	def dfToValidate(self, value):
		self.__dfToValidate = value

	@property
	def recubrimientoMinimo(self):
		return self.__recubrimientoMinimo
	
	@recubrimientoMinimo.setter
	def recubrimientoMinimo(self, value):
		self.__recubrimientoMinimo = value

	@property
	def clavesCandidatas(self):
		return self.__clavesCandidatas

	@clavesCandidatas.setter
	def clavesCandidatas(self, value):
		self.__clavesCandidatas = value
