#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DF import *
from R import *
import threading
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor


_DEFAULT_POOL = ThreadPoolExecutor()

def threadpool(f, executor = None):
    @wraps(f)
    def wrap(*args, **kwargs):
    	return (executor or _DEFAULT_POOL).submit(f, *args, **kwargs)

    return wrap


def threadpool2(f, executor = None):
    @wraps(f)
    def wrap(*args, **kwargs):
        return asyncio.wrap_future((executor or _DEFAULT_POOL).submit(f, *args, **kwargs))

    return wrap


def matrizSinReflexividad(listMatrices):
	listFinal = listMatrices.copy()
	for m in listFinal.copy():
		for n in listFinal.copy():
			if m != n and containsAll(m, n):
				listFinal.remove(m)

	return listFinal


def matrizSinDuplicados(listMatrices):
	listToReturn = []
	for m in listMatrices:
		if m not in listToReturn:
			listToReturn.append(m)

	return listToReturn


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





@threadpool
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
	
	#print("z = ", z)
	#print("z+ = ", cierreZ)
	if all(atr in cierreZ for atr in r.dataT):
		return z

	# Conservamos cada impX en t, si no está en la lista de implicantes
	w = [impX for impX in r.dataT if impX not in implicantes]
	#print("w = ", w)

	zw = cierreZ.copy()
	for atr in w:
		if atr not in zw:
			zw.append(atr)
	zw.sort()
	# Conservamos cada posible clave en t, si no está en la lista de implicantes e implicados (z + w)
	v = [posible for posible in r.dataT if posible not in zw]
	#print("v = ", v)

	z.sort()
	v.sort()

	m2 = []

	algoritmoClavesCandidatas(r, listDFL3, z.copy(), v.copy(), m2)

	return m2


def algoritmoClavesCandidatas(r, listDFL3, z, v, m2):
	for pos in v:
		data = z.copy()

		yaEsta = any(containsAll((data + [pos]), atr) for atr in m2)

		if pos not in z and not yaEsta:
			data.append(pos)
			#print(data)
			data.sort()
			
			cierrePos = cierreTransitivo(data, listDFL3)
			
			if all(atr in cierrePos for atr in r.dataT):
				m2.append(data)
				#print("Es Llave candidata: ", m2)
			else:
				t = threading.Thread(target = algoritmoClavesCandidatas, args = (r, listDFL3, data, v, m2))
				t.start()
				#algoritmoClavesCandidatas(r, listDFL3, data, v,  m2)




@threadpool
def algoritmoClavesCandidatas2(r, listDFL3):
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
	
	#print("z = ", z)
	#print("z+ = ", cierreZ)
	if all(atr in cierreZ for atr in r.dataT):
		return z

	# Conservamos cada impX en t, si no está en la lista de implicantes
	w = [impX for impX in r.dataT if impX not in implicantes]
	#print("w = ", w)

	zw = cierreZ.copy()
	for atr in w:
		if atr not in zw:
			zw.append(atr)
	zw.sort()
	# Conservamos cada posible clave en t, si no está en la lista de implicantes e implicados (z + w)
	v = [posible for posible in r.dataT if posible not in zw]
	#print("v = ", v)

	z.sort()
	v.sort()

	m1 = []
	m2 = []

	if len(z) == 0:
		z = v.copy()

	for atr in z:
		m1.append([atr])
	
	recorrido(r, listDFL3, v, m1, m2)

	return m2


def validate(r, listDFL3, m1, m2, pos):
	cierrePos = cierreTransitivo(pos, listDFL3)
	if all(atr in cierrePos for atr in r.dataT):
		m2.append(pos)
		m1.remove(pos)


def recorrido(r, listDFL3, v, m1, m2):
	for pos in m1.copy():
		#validate(r, listDFL3, m1, m2, pos);
		cierrePos = cierreTransitivo(pos, listDFL3)
		if all(atr in cierrePos for atr in r.dataT):
			m2.append(pos)
			m1.remove(pos)

	#print(m1)
	if len(m1) > 0:
		poblarM1(v, m1, m2)
		recorrido(r, listDFL3, v, m1, m2)


def poblarM1(v, m1, m2):
	for m in m1.copy():
		data = m
		for pos in v:
			newData = data + [pos]
			newData.sort()
			yaEsta = any(containsAll((data + [pos]), atr) for atr in m2)
			if pos not in data and not yaEsta and newData not in m1:
				m1.append(newData)
				
		m1.remove(data)


