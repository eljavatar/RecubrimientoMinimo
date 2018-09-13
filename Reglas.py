#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DF import *
from R import *
import threading

# Funcion para validar si todos los elementos de listB estan en listA
def containsAll(listA, listB):
	for b in listB:
		if b not in listA:
			return False
	return True


# Función para calcular el cierre transitivo de un conjunto de atributos
def cierreTransitivo(x, listDF):
	cierreX = x.copy()
	hasCambios = True
	while hasCambios:
		hasCambios = False
		for df in listDF:
			if containsAll(cierreX, df.implicante):
				for impY in df.implicado:
					if impY not in cierreX:
						hasCambios = True
						cierreX .append(impY)

				#if not containsAll(cierreX, df.implicado):
				#	hasCambios = True
				#cierreX += df.implicado
				
	#cierreX = list(set(cierreX))
	cierreX.sort()
	return cierreX


def dependenciasElementales(listDF, aleatorio = False):
	newListDF = []
	for df in listDF:
		if len(df.implicado) > 1:
			for impY in df.implicado:
				if impY not in df.implicante:
					listY = [impY]
					newListDF.append(DF(df.implicante, listY))
		else:
			# Simplificamos por reflexividad (a,b,c)->a  ==> (b,c)->a
			newImplicante = df.implicante.copy()
			if df.implicado[0] in newImplicante:
				newImplicante.remove(df.implicado[0])
			newListDF.append(DF(newImplicante, df.implicado))

	if aleatorio:
		newListDF = list(set(newListDF))
	return newListDF


def eliminarAtributosExtranos(listDF, aleatorio = False):
	newListDF = listDF.copy()
	
	#for i in range((len(newListDF) - 1), -1, -1):
	for i in range(0, len(newListDF)):
		hasAtributoExtrano = True

		while len(newListDF[i].implicante) > 1 and hasAtributoExtrano:
			df = newListDF[i]
			hasAtributoExtrano = False

			# a,b,c -> d
			# d esta en cierre de a,b?
			# a,b -> d
			for j in range((len(df.implicante) - 1), -1, -1):
			#for j in range(0, len(df.implicante)):
				implicanteTemp = df.implicante.copy()
				implicanteTemp.remove(df.implicante[j])

				cierreX = cierreTransitivo(implicanteTemp, newListDF)
				
				if df.implicado[0] in cierreX:
					#print("Hay atributo extraño en: ", df.implicante, " -> ", df.implicado)
					#print("Nuevo implicante: ", implicanteTemp)
					newListDF[i].implicante = implicanteTemp
					hasAtributoExtrano = True
					break
	
	if aleatorio:
		newListDF = list(set(newListDF))
	return newListDF


def eliminarDependenciasRedundantes(listDF):
	newListDF = listDF.copy()

	#for i in range((len(listDF) - 1), -1, -1):
	for i in range(0, len(listDF)):
		df = listDF[i]
		listDFTemp = newListDF.copy()
		listDFTemp.remove(df)

		cierreX = cierreTransitivo(df.implicante, listDFTemp)

		if df.implicado[0] in cierreX:
			#print("Es dependencia redundante: ", df.implicante, " -> ", df.implicado)
			newListDF.remove(df)

	return newListDF


def validarConjuntosEquivalentes(listDFL3, listDFLx):
	for dfL3 in listDFL3:
		cierre = cierreTransitivo(dfL3.implicante, listDFLx)
		if not containsAll(cierre, dfL3.implicado):
			return False

	for dfLx in listDFLx:
		cierre = cierreTransitivo(dfLx.implicante, listDFL3)
		if not containsAll(cierre, dfLx.implicado):
			return False

	return True



def clavesCandidatas(r, listDFL3):
	implicados = []
	implicantes = []
	for df in listDFL3:
		for y in df.implicado:
			if y not in implicados:
				implicados.append(y)
		for x in df.implicante:
			if x not in implicantes:
				implicantes.append(x)

	# Conservamos cada impY en t, si no está en la lista de implicados
	z = [impY for impY in r.dataT if impY not in implicados]
	cierreZ = cierreTransitivo(z, listDFL3)
	
	print("z = ", z)
	print(cierreZ)
	if all(atr in cierreZ for atr in r.dataT):
		return z

	# Conservamos cada impX en t, si no está en la lista de implicantes
	w = [impX for impX in r.dataT if impX not in implicantes]
	print("w = ", w)

	zw = z + w
	# Conservamos cada posible clave en t, si no está en la lista de implicantes e implicados (z + w)
	v = [posible for posible in r.dataT if posible not in zw]
	print("v = ", v)

	z.sort()
	v.sort()

	m1 = []
	m2 = []

	metodo(r, listDFL3, z.copy(), v.copy(), m1, m2)

	print("Resultados")
	#print(m1)
	#m2 = list(set(m2))
	print(m2)
	


def metodo(r, listDFL3, z, v, m1, m2):
	for pos in v:
		data = z.copy()
		#print("Data antes: ", data)

		esta = any(containsAll((data + [pos]), atr) for atr in m2)

		if pos not in z and not esta:
			#data = z.copy()
			data.append(pos)
			#print(data)
			data.sort()
			
			cierrePos = cierreTransitivo(data, listDFL3)
			#print(cierrePos)
			
			if all(atr in cierrePos for atr in r.dataT):
				m2.append(data)
				#print("Es Llave candidata")
			else:
				t = threading.Thread(target = metodo, args = (r, listDFL3, data, v, m1, m2))
				t.start()
				#m1.append(data)
				#metodo(r, listDFL3, data, v, m1, m2)
				#m1.remove(data)
	



