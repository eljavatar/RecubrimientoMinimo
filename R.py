class R:
	
	# t ==> list
	# l ==> list
	# lx ==> list
	def __init__(self, t = None, l = None, lx = None):
		self.__dataT = t
		self.__dependencias = l
		self.__dfToValidate = lx
	
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
