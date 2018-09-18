#!/usr/bin/env python
# -*- coding: utf-8 -*-

from R import *
from DF import *
import Reglas as reglas
import json
import time

r = R()

# Funcion para eliminar espacios en blanco de los datos recibidos
def trimData(dfStr):
	array = dfStr.split(',')
	for i in range(0, len(array)):
		array[i] = array[i].strip()
	array.sort()
	return array


# Funcion para cargar la ruta de un archivo json
def cargar_datos(ruta):
	# Convertimos el contenido del .json a un objeto Python
	with open(ruta) as contenido:
		datos = json.load(contenido)
	
	# Convertimos las tuplas impX, impY de L, en objetos DF para insertarlos en una lista de DF
	listDF = []
	for dependencia in datos["R"]["L"]:
		df = DF(trimData(dependencia["impX"]), trimData(dependencia["impY"]))
		listDF.append(df)

	listDFToValidate = []
	for dependencia in datos["Lx"]:
		df = DF(trimData(dependencia["impX"]), trimData(dependencia["impY"]))
		listDFToValidate.append(df)
	
	r.dataT = datos["R"]["T"]
	r.dependencias = listDF
	r.dfToValidate = listDFToValidate


def save_result(listDF):
	listaDependencias = []
	for df in listDF:
		dependencia = {"impX" : ",".join(df.implicante), "impY" : ",".join(df.implicado)}
		listaDependencias.append(dependencia)

	datos = {"Lx" : listaDependencias}

	with open('result.json', 'w') as outfile:
		json.dump(datos, outfile, indent = 4)



def ejecutarProceso(ruta, changeListRecubrimiento = False, forceFNBC = False):
	#ruta = 'datos2.json'
	cargar_datos(ruta)
	print("T = ", r.dataT)
	print()

	i = time.time()
	l1 = reglas.dependenciasElementales(r.dependencias)
	time_option1 = time.time() - i
	print("Dependencias Elementales. Tiempo de ejecución: ", time_option1)
	for df in l1:
		print(df.implicante, ' -> ', df.implicado)
	print()

	i = time.time()
	l2 = reglas.eliminarAtributosExtranos(l1)
	time_option2 = time.time() - i
	print("Eliminamos Atributos extraños. Tiempo de ejecución: ", time_option2)
	for df in l2:
		print(df.implicante, ' -> ', df.implicado)
	print()

	i = time.time()
	l3 = reglas.eliminarDependenciasRedundantes(l2)
	time_option3 = time.time() - i
	print("Eliminamos Dependencias redundantes. Tiempo de ejecución: ", time_option3)
	for df in l3:
		print(df.implicante, ' -> ', df.implicado)
	print()
	r.recubrimientoMinimo = l3

	print("Tiempo total de ejecución: ", (time_option1 + time_option2 + time_option3))
	print()

	print("¿Son equivalentes L3 y Lx?: ", reglas.validarConjuntosEquivalentes(l3, r.dfToValidate))
	print()

	save_result(l3)

	i = time.time()
	resultThread = reglas.clavesCandidatas(r, l3)
	clavesCandidatas = resultThread.result()
	time_option4 = time.time() - i

	print("Claves Candidatas Algoritmo 1. Tiempo de ejecución: ", time_option4)
	print("Claves Obtenidas = ", clavesCandidatas)
	clavesCandidatas = reglas.matrizSinDuplicados(clavesCandidatas)
	clavesCandidatas = reglas.matrizSinReflexividad(clavesCandidatas)
	print("Claves sin Redun = ", clavesCandidatas)
	print()
	'''
	i = time.time()
	resultThread = reglas.algoritmoClavesCandidatas2(r, l3)
	clavesCandidatas = resultThread.result()
	time_option5 = time.time() - i

	print("Claves Candidatas Algoritmo 2: ", time_option5)
	print("Claves Obtenidas = ", clavesCandidatas)
	clavesCandidatas = reglas.matrizSinDuplicados(clavesCandidatas)
	clavesCandidatas = reglas.matrizSinReflexividad(clavesCandidatas)
	print("Claves sin Redun = ", clavesCandidatas)
	'''
	r.clavesCandidatas = clavesCandidatas

	estaEn2FN = reglas.estaEn2FN(r)
	print("¿Está en 2FN?: ", estaEn2FN)

	if changeListRecubrimiento:
		listTemp = []
		if not forceFNBC:
			listTemp.append(DF(["c"], ["e"]))
			listTemp.append(DF(["d"], ["e"]))
			listTemp.append(DF(["a"], ["e"]))
		listTemp.append(DF(["a", "b", "d"], ["c"]))
		listTemp.append(DF(["a", "c", "d"], ["e"]))

		r.recubrimientoMinimo = listTemp

		print("Cambiamos el recubrimiento minimo para forzar a que pase la validación de la 3FN y/o FNBC")
		for df in r.recubrimientoMinimo:
			print(df.implicante, ' -> ', df.implicado)

		print()


	estaEn3FN = reglas.estaEn3FN(r, estaEn2FN)
	print("¿Está en 3FN?: ", estaEn3FN)

	estaEnFNBC = reglas.estaEnFNBC(r, estaEn3FN)
	print("¿Está en FNBC?: ", estaEnFNBC)



print("Caso de prueba 1\n")
ejecutarProceso("datos.json")
print("\n\n")

print("Caso de prueba 2\n")
ejecutarProceso("datos2.json")
print("\n\n")

print("Caso de prueba 3\n")
ejecutarProceso("datos3.json")
print("\n\n")

print("Caso de prueba 4\n")
ejecutarProceso("datos2.json", True)
print("\n\n")

print("Caso de prueba 5\n")
ejecutarProceso("datos2.json", True, True)
