import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import tkinter as tk
import datetime as dt
import pandas as pd
from utils import AutoText

class Tabla:
    def __init__(self, frame: ttk.Frame, columnas: tuple):
        self.frame = frame
        self.columnas = columnas
        self.mostrar_tabla()

    def mostrar_tabla(self):
        
        frame_tabla = ttk.Frame(self.frame)
        frame_tabla.pack(side='top', fill='both', expand=True, padx=10)
        
        self.tabla = ttk.Treeview(
            frame_tabla,
            columns=self.columnas,
            show='headings',
            height=12,
        )

        for col in self.columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, anchor=CENTER)

        scrollbar = ttk.Scrollbar(frame_tabla, orient=VERTICAL, command=self.tabla.yview, bootstyle=PROJECTING)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        self.tabla.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='left', fill='y')
        
        self.mostrar_entrada()

    def mostrar_entrada(self):
        self.frame_entrada = ttk.Labelframe(self.frame, text='Nuevo registro', height=10)
        self.frame_entrada.pack(pady=10, padx=5, fill='x', ipady=5, side='bottom')
        self.frame_entrada.grid_anchor('center')
        
        self.entradas: dict[str, tk.StringVar] = {}
        for i,col in enumerate(self.columnas):
            ttk.Label(self.frame_entrada, text=col).grid(row=0, column=i+1, padx=5)
            self.entradas[col] = tk.StringVar()
            ttk.Entry(self.frame_entrada, width=15, textvariable=self.entradas[col], font=('Segoe UI', 11)).grid(row=1, column=i+1, padx=3, pady=3) 
            
        ttk.Button(
            self.frame_entrada,
            text='➕',
            bootstyle=SUCCESS,
            command=self.añadir,
        ).grid(column=4, row=1, pady=8, padx=4)

        ttk.Button(
            self.frame_entrada,
            text='➖',
            bootstyle=DANGER,
            command=self.eliminar
        ).grid(column=0, row=1, pady=8, padx=8)

    def añadir(self, valido: dict[str, type] = {}):
        
        añadir = True
        valores = []
        i = 0
        while añadir and i < len(self.columnas):
            c = self.columnas[i]
            valores.append(self.entradas[c].get())
            if c in valido:
                try:
                    valido[c](valores[-1])
                except:
                    Messagebox.show_error(message='El importe debe ser numérico', title='Error')
                    añadir = False
            i += 1
        
        if añadir and len(valores) > 0:
            self.tabla.insert('', 'end', values=valores)
            for c in self.columnas:
                self.entradas[c].set('')
        
    def eliminar(self):
        seleccionado = self.tabla.selection()
        if seleccionado:
            self.tabla.delete(seleccionado)
            
    def df(self):
        columnas = self.tabla['columns']
        filas = [self.tabla.item(item)['values'] for item in self.tabla.get_children()]
        return pd.DataFrame(filas, columns=columnas)
    
    def limpiar(self):
        self.tabla.delete(*self.tabla.get_children())
        
    def cargar_df(self, df: pd.DataFrame):
        df = df.fillna('')
        for i,fila in df.iterrows():
            self.tabla.insert('', 'end', values=list(fila.values))


class InputDatos:
    def __init__(self, frame: ttk.Frame, campos_texto: list, multilinea: list):
        self.campos_texto = campos_texto
        self.multilinea = multilinea
        
        self.frame_datos = ttk.Labelframe(frame, text='Datos del Cliente')
        self.frame_datos.pack(side='top', pady=20, padx=20, fill='x', ipady=10)
        
        self.frame_inp = ttk.Frame(self.frame_datos)
        self.frame_inp.pack(side='left')

        self.entradas_u = {campo['nombre']: tk.StringVar() for campo in self.campos_texto if campo['nombre'] not in multilinea}
        self.entradas_m = {campo['nombre']: AutoText(self.frame_inp) for campo in self.campos_texto if campo['nombre'] in multilinea}
        
        self.mostrar()

    def mostrar(self):
        for i, campo in enumerate(self.campos_texto):
            ttk.Label(self.frame_inp, text=campo['nombre'], width=18, anchor='e').grid(
                column=0, row=i, pady=5, padx=6, sticky='e'
            )
            if campo['nombre'] in self.multilinea:
                self.entradas_m[campo['nombre']].grid(column=1, row=i, pady=5)
            else:  
                ttk.Entry(self.frame_inp, textvariable=self.entradas_u[campo['nombre']], width=45, font=('Segoe UI', 11)).grid(
                    column=1, row=i, pady=5
                )
                
                if 'default' in campo:
                    self.entradas_u[campo['nombre']].set(campo['default'])
   
    def limpiar_entradas(self):
        for campo in self.campos_texto:
            if not 'default' in campo and not campo['nombre'] in self.multilinea:
                self.entradas_u[campo['nombre']].set('')
            elif not 'default' in campo:
                self.entradas_m[campo['nombre']].delete(1.0, tk.END)

    def guardar(self, campo_id: str) -> dict:
        modelo = {}
        id = self.entradas_m[campo_id].get(1.0, "end-1c")
        id = id.partition('\n')[0]

        if id:
            entradas = {campo: entrada.get() for campo, entrada in self.entradas_u.items()}
            entradas.update({campo: entrada.get(1.0, "end-1c").replace('\\n', '\n') for campo, entrada in self.entradas_m.items()})
            modelo[id] = entradas
        else:
            Messagebox.show_error(f'Debes rellenar el campo "{campo_id}"', title='Error')

        return modelo

    def cargar(self, inp: dict, mantener: list = None):
        if inp:
            for k, v in inp.items():
                if k in self.entradas_u and not k in mantener:
                    self.entradas_u[k].set(v)
                elif k in self.entradas_m and not k in mantener:
                    self.entradas_m[k].delete(1.0, tk.END)
                    self.entradas_m[k].insert(1.0, v)

    def campos(self) -> dict:
        campos = {campo: entrada.get() for campo, entrada in self.entradas_u.items()}
        campos.update({campo: entrada.get(1.0, "end-1c") for campo, entrada in self.entradas_m.items()})
        return campos

class Lista:
    def __init__(self, frame: tk.Frame, seleccionado, titulo: str, lista: list):
        self.frame: ttk.Frame = frame
        self.seleccionado = seleccionado
        self.titulo = titulo
        self.mostrar_lista()
        self.actualizar_lista(lista)
        
    def mostrar_lista(self):
        if self.titulo:
            ttk.Label(self.frame, text=self.titulo, style='Titulo.TLabel').pack(side='top', pady=(5, 3))

        frame_lista = ttk.Frame(self.frame)
        frame_lista.pack(side='top', fill='y', expand=True, padx=10)

        scrollbar = ttk.Scrollbar(frame_lista, orient=VERTICAL, bootstyle=ROUND)
        self.listado = tk.Listbox(
            frame_lista,
            borderwidth=2,
            width=40,
            relief='flat',
            selectbackground='#40434B',
            selectforeground='white',
            font=('Segoe UI', 12),
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.listado.yview)

        self.listado.pack(side='left', fill='y', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.listado.bind('<<ListboxSelect>>', self.seleccionar)

    def seleccionar(self, event):
        seleccion = self.listado.curselection()
        if seleccion:
            indice = seleccion[0]
            sel = self.listado.get(indice)
            self.seleccionado(sel)

    def actualizar_lista(self, lista: list):
        self.listado.delete(0, tk.END)
        for k in lista:
            self.listado.insert(tk.END, k)

    def eliminar_seleccion(self) -> str:
        seleccion = self.listado.curselection()
        if seleccion:
            s = self.listado.get(seleccion)
            respuesta = Messagebox.yesno('¿Eliminar este registro?', title='Confirmar')
            if respuesta == 'Yes':
                return s
                
class EmailPreview:
    def __init__(self, frame: ttk.Frame):
        self.frame = ttk.Labelframe(frame, text='Email')
        self.frame.pack(side='top', expand=True, fill='both')
        self.destinatario = tk.StringVar()
        self.asunto = tk.StringVar()
        self.cuerpo = ''
        
        self.mostrar()

    
    def mostrar(self):
        ttk.Label(self.frame, text='Destinatario:').pack(side='top')
        ttk.Entry(self.frame, textvariable=self.destinatario).pack(side='top', pady=10, padx=10, fill='x')
        ttk.Label(self.frame, text='Asunto:').pack(side='top')
        ttk.Entry(self.frame, textvariable=self.asunto).pack(side='top', pady=10, padx=10, fill='x')
        ttk.Label(self.frame, text='Cuerpo:').pack(side='top')
        self.in_cuerpo = tk.Text(
            self.frame,
            width=40,
            height=5,
            wrap="word",
            bg="#2b3e50",       
            fg="white",
            insertbackground="white", 
            relief="flat",
            font=("Segoe UI", 10),
            padx=6,
            pady=6
        )
        self.in_cuerpo.insert(1.0, self.cuerpo)
        self.in_cuerpo.pack(side='top', pady=10, padx=10, fill='both', expand=True)
        
    def campos(self) -> dict:
        return {
            'destinatario': self.destinatario.get(),
            'asunto': self.asunto.get(),
            'cuerpo': self.in_cuerpo.get(1.0, tk.END)
        }
        
    def actualizar(self, destinatario: str, asunto: str, cuerpo: str):
        self.destinatario.set(destinatario)
        self.asunto.set(asunto)
        self.in_cuerpo.delete(1.0, tk.END)
        self.in_cuerpo.insert(1.0, cuerpo)
        
