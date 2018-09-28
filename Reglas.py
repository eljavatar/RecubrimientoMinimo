#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DF import *
from R import *
import Utils as utils
import threading
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor


_DEFAULT_POOL = ThreadPoolExecutor(5)

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


# Función para calcular el cierre transitivo de un conjunto de atributos
def cierreTransitivo(x, listDF):
	cierreX = x.copy()
	hasCambios = True
	while hasCambios:
		hasCambios = False
		for df in listDF:
			if utils.containsAll(cierreX, df.implicante):
				for impY in df.implicado:
					if impY not in cierreX:
						hasCambios = True
						cierreX .append(impY)

				#if not utils.containsAll(cierreX, df.implicado):
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
		if not utils.containsAll(cierre, dfL3.implicado):
			return False

	for dfLx in listDFLx:
		cierre = cierreTransitivo(dfLx.implicante, listDFL3)
		if not utils.containsAll(cierre, dfLx.implicado):
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
	# Conservamos cada posible clave en t, si no está en la lista del
	# cierre de implicantes e implicados (z* + w)
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

		yaEsta = any(utils.containsAll((data + [pos]), atr) for atr in m2)

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


def estaEn2FN(r):
	listAtrClaves = []
	clavesConMasDeDosAtr = []
	for key in r.clavesCandidatas:
		if len(key) > 1:
			clavesConMasDeDosAtr.append(key)
		for atr in key:
			if atr not in listAtrClaves:
				listAtrClaves.append(atr)
	listAtrClaves.sort()
	#print(listAtrClaves)

	# Atributos que no estan en ninguna clave candidata
	listNoPrimos = [atr for atr in r.dataT if atr not in listAtrClaves]
	#listNoprimos.sort()
	#print(listNoPrimos)

	for noPrimo in listNoPrimos:
		for key in clavesConMasDeDosAtr:
			for j in range((len(key) - 1), -1, -1):
				keyTemp = key.copy()
				keyTemp.remove(key[j])

				cierre = cierreTransitivo(keyTemp, r.recubrimientoMinimo)
				
				if noPrimo not in cierre:
					return False

	return True


def estaEn3FN(r, estaEn2FN):
	if not estaEn2FN:
		return False

	listAtrClaves = []
	for key in r.clavesCandidatas:
		for atr in key:
			if atr not in listAtrClaves:
				listAtrClaves.append(atr)
	listAtrClaves.sort()
	#print(listAtrClaves)

	# Atributos que no estan en ninguna clave candidata
	listNoPrimos = [atr for atr in r.dataT if atr not in listAtrClaves]

	for df in r.recubrimientoMinimo:
		if df.implicante not in r.clavesCandidatas and df.implicado[0] not in listNoPrimos:
			return False

	return True


def estaEnFNBC(r, estaEn3FN):
	if not estaEn3FN:
		return False

	for df in r.recubrimientoMinimo:
		if df.implicante not in r.clavesCandidatas:
			return False

	return True
