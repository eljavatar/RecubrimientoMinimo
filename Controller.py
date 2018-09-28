from R import *
from DF import *
import Reglas as reglas
import Utils as utils
import time


def ejecutarProceso(r):
	hasError = False
	mensajeError = ""
	for df in r.dependencias:
		if not utils.containsAll(r.dataT, df.implicante) or not utils.containsAll(r.dataT, df.implicado):
			mensajeError += ",".join(df.implicante) + " -> " + ",".join(df.implicado) + "\n"
			hasError = True

	if hasError:
		return "Las siguientes dependencias contienen errores ya que al menos uno de sus atributos no se encuentra en T:\n" + mensajeError

	resultado = "Resultado\n"
	resultado += "T = {" + ", ".join(r.dataT) + "}\n\n"

	i = time.time()
	l1 = reglas.dependenciasElementales(r.dependencias)
	time_option1 = time.time() - i
	resultado += "Dependencias Elementales y se obtiene L1. Tiempo de ejecución: " + str(time_option1) + " seg\n"
	for df in l1:
		resultado += ",".join(df.implicante) + " -> " + ",".join(df.implicado) + "\n"
	resultado += "\n"

	i = time.time()
	l2 = reglas.eliminarAtributosExtranos(l1)
	time_option2 = time.time() - i
	resultado += "Eliminamos Atributos extraños y se obtiene L2. Tiempo de ejecución: " + str(time_option2) + " seg\n"
	for df in l2:
		resultado += ",".join(df.implicante) + " -> " + ",".join(df.implicado) + "\n"
	resultado += "\n"

	i = time.time()
	l3 = reglas.eliminarDependenciasRedundantes(l2)
	time_option3 = time.time() - i
	resultado += "Eliminamos Dependencias redundantes y se obtiene L3. Tiempo de ejecución: " + str(time_option3) + " seg\n"
	for df in l3:
		resultado += ",".join(df.implicante) + " -> " + ",".join(df.implicado) + "\n"
	resultado += "\n"
	r.recubrimientoMinimo = l3

	resultado += "Tiempo total de ejecución: " + str(time_option1 + time_option2 + time_option3) + " seg\n\n"

	if (r.dfToValidate):
		resultado += "Se ha ingresado el siguiente conjunto de dependencias (Lx) para validar si es equivalente al L3 obtenido:\n"
		for df in r.dfToValidate:
			resultado += ",".join(df.implicante) + " -> " + ",".join(df.implicado) + "\n"
		resultado += "¿Son equivalentes L3 y Lx?: " + str(reglas.validarConjuntosEquivalentes(l3, r.dfToValidate)) + "\n\n"

	utils.saveResult(l3)

	i = time.time()
	resultThread = reglas.clavesCandidatas(r, l3)
	clavesCandidatas = resultThread.result()
	time_option4 = time.time() - i

	resultado += "Calculamos Claves Candidatas. Tiempo de ejecución: " + str(time_option4) + " seg\n"
	clavesCandidatas = utils.matrizSinDuplicados(clavesCandidatas)
	clavesCandidatas = utils.matrizSinReflexividad(clavesCandidatas)
	for key in clavesCandidatas:
		resultado += ",".join(key) + "\n"
	resultado += "\n"

	r.clavesCandidatas = clavesCandidatas

	estaEn2FN = reglas.estaEn2FN(r)
	resultado += "¿El Recubrimiento Mínimo obtenido está en 2FN?: " + str(estaEn2FN) + "\n"

	estaEn3FN = reglas.estaEn3FN(r, estaEn2FN)
	resultado += "¿El Recubrimiento Mínimo obtenido está en 3FN?: " + str(estaEn3FN) + "\n"

	estaEnFNBC = reglas.estaEnFNBC(r, estaEn3FN)
	resultado += "¿El Recubrimiento Mínimo obtenido está en FNBC?: " + str(estaEnFNBC) + "\n"

	return resultado