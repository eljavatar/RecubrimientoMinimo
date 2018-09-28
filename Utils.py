from R import *
from DF import *
import Reglas as reglas
import json
import time


# Funcion para validar si todos los elementos de listB estan en listA
def containsAll(listA, listB):
	for b in listB:
		if b not in listA:
			return False
	return True


# Función para validar si al menos un elemento de listB está en listA
def containsAny(listA, listB):
	for b in listB:
		if b in listA:
			return True
	return False


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

# Funcion para eliminar espacios en blanco de los datos recibidos
def trimData(dfStr):
	array = dfStr.split(',')
	for i in range(0, len(array)):
		array[i] = array[i].strip().upper()
	array.sort()
	return array


# Funcion para cargar la ruta de un archivo json
def cargarDatosAndReturnR(ruta):
	r = R()
	# Convertimos el contenido del .json a un objeto Python
	with open(ruta) as contenido:
		datos = json.load(contenido)
	
	# Convertimos las tuplas impX, impY de L, en objetos DF para insertarlos en una lista de DF
	listDF = []
	for dependencia in datos["R"]["L"]:
		df = DF(trimData(dependencia["impX"]), trimData(dependencia["impY"]))
		if containsAny(df.implicante, df.implicado) or df in listDF:
			continue
		listDF.append(df)

	listDFToValidate = []
	for dependencia in datos["Lx"]:
		df = DF(trimData(dependencia["impX"]), trimData(dependencia["impY"]))
		if containsAny(df.implicante, df.implicado) or df in listDFToValidate:
			continue
		listDFToValidate.append(df)
	
	r.dataT = datos["R"]["T"]
	for i in range(0, len(r.dataT)):
		r.dataT[i] = r.dataT[i].strip().upper()
	r.dataT.sort()

	r.dependencias = listDF
	r.dfToValidate = listDFToValidate

	return r;


def saveResult(listDF):
	listaDependencias = []
	for df in listDF:
		dependencia = {"impX" : ",".join(df.implicante), "impY" : ",".join(df.implicado)}
		listaDependencias.append(dependencia)

	datos = {"Lx" : listaDependencias}

	with open('result.json', 'w') as outfile:
		json.dump(datos, outfile, indent = 4)
