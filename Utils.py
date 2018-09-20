from R import *
from DF import *
#import Reglas as reglas
import json
import time


# Funcion para eliminar espacios en blanco de los datos recibidos
def trimData(dfStr):
	array = dfStr.split(',')
	for i in range(0, len(array)):
		array[i] = array[i].strip()
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
		listDF.append(df)

	listDFToValidate = []
	for dependencia in datos["Lx"]:
		df = DF(trimData(dependencia["impX"]), trimData(dependencia["impY"]))
		listDFToValidate.append(df)
	
	r.dataT = datos["R"]["T"]
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
