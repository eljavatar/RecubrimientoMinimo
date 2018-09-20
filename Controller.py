from R import *
from DF import *
import Reglas as reglas
import Utils as utils
import time


def ejecutarProceso(r, changeListRecubrimiento = False, forceFNBC = False):
	#r = utils.cargarDatosAndReturnR(ruta)
	resultado = "Resultado\n"
	resultado += "T = " + str(r.dataT) + "\n\n"

	i = time.time()
	l1 = reglas.dependenciasElementales(r.dependencias)
	time_option1 = time.time() - i
	resultado += "Dependencias Elementales y se obtiene L1. Tiempo de ejecución: " + str(time_option1) + "\n"
	for df in l1:
		resultado += str(df.implicante) + " -> " + str(df.implicado) + "\n"
	resultado += "\n"

	i = time.time()
	l2 = reglas.eliminarAtributosExtranos(l1)
	time_option2 = time.time() - i
	resultado += "Eliminamos Atributos extraños y se obtiene L2. Tiempo de ejecución: " + str(time_option2) + "\n"
	for df in l2:
		resultado += str(df.implicante) + " -> " + str(df.implicado) + "\n"
	resultado += "\n"

	i = time.time()
	l3 = reglas.eliminarDependenciasRedundantes(l2)
	time_option3 = time.time() - i
	resultado += "Eliminamos Dependencias redundantes y se obtiene L3. Tiempo de ejecución: " + str(time_option3) + "\n"
	for df in l3:
		resultado += str(df.implicante) + " -> " + str(df.implicado) + "\n"
	resultado += "\n"
	r.recubrimientoMinimo = l3

	resultado += "Tiempo total de ejecución: " + str(time_option1 + time_option2 + time_option3) + "\n"
	resultado += "\n"

	if (r.dfToValidate):
		resultado += "¿Son equivalentes L3 y Lx?: " + str(reglas.validarConjuntosEquivalentes(l3, r.dfToValidate)) + "\n"
		resultado += "\n"

	utils.saveResult(l3)

	i = time.time()
	resultThread = reglas.clavesCandidatas(r, l3)
	clavesCandidatas = resultThread.result()
	time_option4 = time.time() - i

	resultado += "Claves Candidatas. Tiempo de ejecución: " + str(time_option4) + "\n"
	#print("Claves Obtenidas = ", clavesCandidatas)
	clavesCandidatas = reglas.matrizSinDuplicados(clavesCandidatas)
	clavesCandidatas = reglas.matrizSinReflexividad(clavesCandidatas)
	resultado += "Claves = " + str(clavesCandidatas) + "\n"
	resultado += "\n"

	r.clavesCandidatas = clavesCandidatas

	estaEn2FN = reglas.estaEn2FN(r)
	resultado += "¿Está en 2FN?: " + str(estaEn2FN) + "\n"

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
	resultado += "¿Está en 3FN?: " + str(estaEn3FN) + "\n"

	estaEnFNBC = reglas.estaEnFNBC(r, estaEn3FN)
	resultado += "¿Está en FNBC?: " + str(estaEnFNBC) + "\n"

	return resultado