#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
from R import *
from DF import *
import Utils as utils
import Controller as cont
import traceback
from random import randint
import time


r = R()
listDF = []
matrizControlDF = []
listDFtoValidate = []

root = Tk()
frame = Frame(root)

frameDF = Frame(frame)
frameDF.grid(row = 6, column = 0, padx = 5, pady = 5)

frameRes = Frame(frame)
frameRes.grid(row = 6, column = 1, padx = 5, pady = 5, columnspan = 5)
frameRes.grid_columnconfigure(0, weight = 1)

tableDependencias = ttk.Treeview(frameDF)
textRes = Text(frameRes, width = 50, height = 22)

textFont = ("Arial", 10)

pathFile = StringVar()
dataT = StringVar()
dfImplicante = StringVar()
dfImplicado = StringVar()
resultado = ""


def fillData():
	dataT.set(",".join(r.dataT.copy()))
	cleanDependencias()
	#listDFtoValidate = r.dfToValidate.copy()
	for df in r.dependencias:
		itemId = str(randint(1, 999999999) + (time.time() * randint(1, 9999)))
		matrizControlDF.append([itemId, df])
		tableDependencias.insert("", END, text = (",".join(df.implicante) + " -> " + ",".join(df.implicado)), iid = itemId)
		listDF.append(df)


def loadFile():
	try:
		root.filename =  filedialog.askopenfilename(initialdir = "",title = "Select file",filetypes = (("JSON files","*.json"),("all files","*.*")))
		#root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("JSON files","*.json"),("all files","*.*"))) # Disco C
		if not messagebox.askyesno(title = "Mensaje de Confirmación", message = "Al cargar este archivo, se sobreescribirán las\nvariables de entrada del conjunto R(T, L)\n¿Está seguro de continuar?"):
			return
		pathFile.set(root.filename)
		dataLoad = utils.cargarDatosAndReturnR(root.filename);
		r.dataT = dataLoad.dataT.copy()
		r.dependencias = dataLoad.dependencias
		r.dfToValidate = dataLoad.dfToValidate
		fillData()
	except Exception as e:
		traceback.print_exc()
		messagebox.showerror("Error", str(sys.exc_info()))
		#raise e
	

def addDependencia():
	if len(dfImplicante.get().strip()) == 0 or len(dfImplicado.get().strip()) == 0:
		messagebox.showerror("Mensaje de Error", "Debe ingresar el implicante y el implicado\npara poder agregar la Dependencia Funcional")
		return

	df = DF(utils.trimData(dfImplicante.get()), utils.trimData(dfImplicado.get()))
	if utils.containsAny(df.implicante, df.implicado):
		messagebox.showerror("Mensaje de Error", "La dependencia que está intentando ingresar es Trivial (Puede\nser simplificada usando reflexividad) y sólo puede ingresar dependencias No Triviales")
		return

	if df in listDF:
		messagebox.showerror("Mensaje de Error", "La dependencia que está intentando ingresar\nya ha sido ingresada previamente")
		return

	itemId = str(randint(1, 999999999) + (time.time() * randint(1, 9999)))
	matrizControlDF.append([itemId, df])
	tableDependencias.insert("", END, text = (",".join(df.implicante) + " -> " + ",".join(df.implicado)), iid = itemId)
	dfImplicante.set("")
	dfImplicado.set("")
	listDF.append(df)


def modifyDependencia():
	itemId = tableDependencias.focus()
	for i in range(len(matrizControlDF)):
		if matrizControlDF[i][0] == itemId:
			newImplicante = simpledialog.askstring("Implicante", "Ingrese el nuevo implicante", initialvalue = ",".join(matrizControlDF[i][1].implicante), parent = root)
			newImplicado = simpledialog.askstring("Implicado", "Ingrese el nuevo implicado", initialvalue = ",".join(matrizControlDF[i][1].implicado), parent = root)

			index = listDF.index(matrizControlDF[i][1])

			if newImplicante is not None and len(newImplicante.strip()) > 0:
				listDF[index].implicante = utils.trimData(newImplicado)
				matrizControlDF[i][1].implicante = utils.trimData(newImplicante)

			if newImplicado is not None and len(newImplicado.strip()) > 0:
				listDF[index].implicado = utils.trimData(newImplicado)
				matrizControlDF[i][1].implicado = utils.trimData(newImplicado)

			tableDependencias.item(itemId, text = (",".join(listDF[index].implicante) + " -> " + ",".join(listDF[index].implicado)))
			break


def deleteDependencia():
	itemId = tableDependencias.focus()
	for i in range(len(matrizControlDF)):
		if matrizControlDF[i][0] == itemId:
			element = matrizControlDF[i]
			listDF.remove(element[1])
			tableDependencias.delete(itemId)
			matrizControlDF.remove(element)
			break


def cleanDependencias():
	listDF.clear()
	for i in tableDependencias.get_children():
		tableDependencias.delete(i)
	matrizControlDF.clear()
	#listDFtoValidate.clear()
	#r.dfToValidate = []


def calcularRecubrimientoMinimo():
	if len(dataT.get().strip()) == 0:
		messagebox.showerror("Mensaje de Error", "Debe ingresar el conjunto de datos (T)")
		return
	
	if len(listDF) == 0:
		messagebox.showerror("Mensaje de Error", "Debe ingresar un conjunto de dependencias (L)")
		return

	r.dataT = utils.trimData(dataT.get().upper())
	r.dependencias = listDF.copy()

	resultado = cont.ejecutarProceso(r)
	r.dfToValidate = []

	textRes.delete('1.0', END)
	textRes.insert(END, resultado)


def initForm():
	root.title("Recubrimiento Mínimo")
	root.resizable(False, False)
	root.iconbitmap("logo.ico")

	
	frame.pack(fill = "x", expand = 1)
	#frame.config(width = "850", height = "400")

	labelTitle = Label(frame, text = "Aplicación para calcular el Recubrimiento Mínimo de R(T, L)", font = "Arial 11 bold")
	labelTitle.grid(row = 0, column = 0,  padx = 5, pady = 5, columnspan = 5)

	separator1 = ttk.Separator(frame, orient = "horizontal")
	separator1.grid(row = 1, column = 0, sticky="we", padx = 5, pady = 5, columnspan = 5)


	entryFile = Entry(frame, font = textFont, textvariable = pathFile)
	entryFile.grid(row = 2, column = 0, padx = 5, pady = 5, columnspan = 4, sticky = W + E)

	buttonLoadFile = Button(frame, text = "Cargar Archivo", font = textFont, command = loadFile)
	buttonLoadFile.grid(row = 2, column = 4, padx = 5, pady = 5)

	separator2 = ttk.Separator(frame, orient = "horizontal")
	separator2.grid(row = 3, column = 0, sticky="we", padx = 5, pady = 5, columnspan = 5)


	labelT = Label(frame, text = "Conjunto de datos (T):", font = textFont)
	labelT.grid(row = 4, column = 0, sticky = "e", padx = 5, pady = 5)

	entryT = Entry(frame, font = textFont, textvariable = dataT)
	entryT.grid(row = 4, column = 1, padx = 5, pady = 5, columnspan = 4, sticky='we')


	labelL = Label(frame, text = "Dependencia Funcional (L):", font = textFont)
	labelL.grid(row = 5, column = 0, sticky = "e", padx = 5, pady = 5)

	entryDFx = Entry(frame, font = textFont, textvariable = dfImplicante)
	entryDFx.grid(row = 5, column = 1, padx = 5, pady = 5)

	labelL = Label(frame, text = "->")
	labelL.grid(row = 5, column = 2, padx = 5, pady = 5)

	entryDFy = Entry(frame, font = textFont, textvariable = dfImplicado)
	entryDFy.grid(row = 5, column = 3, padx = 5, pady = 5)


	buttonAddDF = Button(frame, text = "Agregar DF", font = textFont, command = addDependencia)
	buttonAddDF.grid(row = 5, column = 4, padx = 5, pady = 5)

	
	tableDependencias.grid(row = 0, column = 0, padx = 5, pady = 5)
	tableDependencias.heading("#0", text = "Lista Dependencias")

	scrollbar_vertical = ttk.Scrollbar(frameDF, orient = 'vertical', command = tableDependencias.yview)
	scrollbar_vertical.grid(row = 0, column = 1, sticky = (E, N, S))

	tableDependencias.configure(yscrollcommand = scrollbar_vertical.set)

	buttonModifyDF = Button(frameDF, text = "Modificar Dependencia Seleccionada", font = textFont, command = modifyDependencia)
	buttonModifyDF.grid(row = 1, column = 0, padx = 5, pady = 5, columnspan = 2)

	buttonDeleteDF = Button(frameDF, text = "Eliminar Dependencia Seleccionada", font = textFont, command = deleteDependencia)
	buttonDeleteDF.grid(row = 2, column = 0, padx = 5, pady = 5, columnspan = 2)

	buttonCleanDF = Button(frameDF, text = "Limpiar Dependencias", font = textFont, command = cleanDependencias)
	buttonCleanDF.grid(row = 3, column = 0, padx = 5, pady = 5, columnspan = 2)

	
	textRes.grid(row = 0, column = 0, padx = 5, pady = 5)

	scrollVertRes = Scrollbar(frameRes, command = textRes.yview)
	scrollVertRes.grid(row = 0, column = 1, sticky = (E, N, S))

	textRes.config(yscrollcommand = scrollVertRes.set)


	buttonCalcular = Button(root, text = "Calcular Recubrimiento Mínimo", font = textFont, command = calcularRecubrimientoMinimo)
	buttonCalcular.pack(padx = 5, pady = 5)

	root.mainloop()
	# Con extension pyw no abre consola por detras



initForm()