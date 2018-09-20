#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from R import *
from DF import *
import Utils as utils
import Controller as cont
import traceback


r = R()
listDF = []

root = Tk()
frame = Frame(root)

frameDF = Frame(frame)
frameDF.grid(row = 6, column = 0, padx = 5, pady = 5)

frameRes = Frame(frame)
frameRes.grid(row = 6, column = 1, padx = 5, pady = 5, columnspan = 5)
frameRes.grid_columnconfigure(0, weight = 1)

tableDependencias = ttk.Treeview(frameDF)
textRes = Text(frameRes, width = 50, height = 16)

textFont = ("Arial", 10)

pathFile = StringVar()
dataT = StringVar()
dfImplicante = StringVar()
dfImplicado = StringVar()
resultado = ""


def fillData():
	dataT.set(",".join(r.dataT.copy()))
	cleanDependencias()
	for df in r.dependencias:
		tableDependencias.insert("", END, text = (",".join(df.implicante) + " -> " + ",".join(df.implicado)))
		listDF.append(df)


def loadFile():
	try:
		root.filename =  filedialog.askopenfilename(initialdir = "",title = "Select file",filetypes = (("JSON files","*.json"),("all files","*.*")))
		if not messagebox.askyesno(title = "Mensaje de Confirmación", message = "Al cargar este archivo, se sobreescribirán las\nvariables de entrada del conjunto R(T, L)\n¿Está seguro de continuar?"):
			return
		#root.filename =  filedialog.askopenfilename(initialdir = "",title = "Select file",filetypes = (("JSON files","*.json"),("all files","*.*"))) # Disco C
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
	tableDependencias.insert("", END, text = (",".join(df.implicante) + " -> " + ",".join(df.implicado)))
	dfImplicante.set("")
	dfImplicado.set("")
	listDF.append(df)


def cleanDependencias():
	listDF.clear()
	for i in tableDependencias.get_children():
		tableDependencias.delete(i)


def calcularRecubrimientoMinimo():
	if len(dataT.get().strip()) == 0:
		messagebox.showerror("Mensaje de Error", "Debe ingresar el conjunto de datos (T)")
		return
	
	if len(listDF) == 0:
		messagebox.showerror("Mensaje de Error", "Debe ingresar un conjunto de dependencias (L)")
		return

	r.dataT = utils.trimData(dataT.get())
	r.dependencias = listDF

	resultado = cont.ejecutarProceso(r)

	textRes.delete('1.0', END)
	textRes.insert(END, resultado)


def initForm():
	root.title("Recubrimiento Mínimo")
	root.resizable(True, True)
	#root.iconbitmap("ruta.ico")

	
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

	buttonCleanDF = Button(frameDF, text = "Limpir Dependencias", font = textFont, command = cleanDependencias)
	buttonCleanDF.grid(row = 1, column = 0, padx = 5, pady = 5)

	
	textRes.grid(row = 0, column = 0, padx = 5, pady = 5)

	scrollVertRes = Scrollbar(frameRes, command = textRes.yview)
	scrollVertRes.grid(row = 0, column = 1, sticky = (E, N, S))

	textRes.config(yscrollcommand = scrollVertRes.set)


	buttonCalcular = Button(root, text = "Calcular Recubrimiento Mínimo", font = textFont, command = calcularRecubrimientoMinimo)
	buttonCalcular.pack(padx = 5, pady = 5)

	root.mainloop()
	# Con extension pyw no abre consola por detras



initForm()