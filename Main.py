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



ruta = 'datos3.json'
cargar_datos(ruta)
print(r.dataT)
print()

i = time.time()
l1 = reglas.dependenciasElementales(r.dependencias)
time_option1 = time.time() - i
print("Dependencias Elementales: ", time_option1)
for df in l1:
	print(df.implicante, ' -> ', df.implicado)
print()

i = time.time()
l2 = reglas.eliminarAtributosExtranos(l1)
time_option2 = time.time() - i
print("Eliminamos Atributos extraños: ", time_option2)
for df in l2:
	print(df.implicante, ' -> ', df.implicado)
print()

i = time.time()
l3 = reglas.eliminarDependenciasRedundantes(l2)
time_option3 = time.time() - i
print("Eliminamos Dependencias redundantes: ", time_option3)
for df in l3:
	print(df.implicante, ' -> ', df.implicado)
print()

print("Tiempo total: ", (time_option1 + time_option2 + time_option3))
print()

print("¿Son equivalentes L3 y Lx?: ", reglas.validarConjuntosEquivalentes(l3, r.dfToValidate))

i = time.time()
reglas.clavesCandidatas(r, l3)
time_option4 = time.time() - i
print("Calculo finalizado: ", time_option4)
#save_result(l3)
