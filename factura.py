from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import pandas as pd
import datetime as dt

class Factura():
    def __init__(self, fondo: str):
        self.fondo = fondo
        self.datos = {}
        self.tabla: pd.DataFrame
        
    def nombre(self) -> str:
        nombre_cliente: str = self.datos.get('Cuadro')
        if nombre_cliente:
            fecha = dt.datetime.strptime(self.datos.get('Fecha'), '%d.%m.%Y')
            nombre_cliente = nombre_cliente.partition('\n')[0].replace(' ', '-')
            return f'{nombre_cliente}-{fecha.month}-{fecha.year}'
        else:
            return ''

    def insertar_datos(self, input: dict):
        input['Cuadro'] = input['Cliente'] + '\n' + input['Dirección']
        input.pop('Cliente')
        input.pop('Dirección')
        self.datos = input # {'CIF': '2123', 'Cliente': 'Empresa 1', ...}
                         
    def añadir_tabla(self, tabla: pd.DataFrame):
        self.tabla = tabla
    
    def generar_pagina(self, tabla: pd.DataFrame, imprimir = False):
        ancho, alto = A4
        
        if not imprimir:
            self.canvas.drawImage(ImageReader(self.fondo), 0, 0, width=ancho, height=alto)
        else:
            for campo in self.campos.keys():
                self.campos[campo]['x'] += 1
                if campo in ['Bruto', 'Iva', 'Desc', 'Neto']:
                    self.campos[campo]['y'] -= 20
        
        for campo, texto in self.datos.items():
            self.campo(texto, campo)
                
        if not tabla.empty:
            self.mostrar_tabla(tabla)
            
        self.canvas.showPage()
            
    def campo(self, texto, campo):
        if campo in self.campos:
            atr_campo = self.campos[campo]
            self.canvas.setFont(atr_campo['fuente'], atr_campo['tamaño'])
            if campo == 'Cuadro':
                for i, s in enumerate(self.partir_str(str(texto))):
                    self.canvas.drawString(atr_campo['x'], atr_campo['y'] - i*16, s)
            elif campo != 'Iva' and campo != 'Número factura': 
                try:
                    texto = float(texto)
                    texto = f'{texto:.2f}'.replace('.',',') + '.-'
                except:
                    pass
                self.canvas.drawString(atr_campo['x'], atr_campo['y'], str(texto))
            else:
                self.canvas.drawString(atr_campo['x'], atr_campo['y'], str(texto))
            
    def partir_str(self, string: str) -> list[str]:
        part = string.partition('\n')
        if part[2]:
            return [part[0]] + self.partir_str(part[2])      
        else:
            return [part[0]]      
       
    def mostrar_tabla(self, tabla: pd.DataFrame):
        props = self.campos['Tabla']
        self.canvas.setFont(props['fuente'], props['tamaño'])
        for fila, row in tabla.iterrows():
            for col, valor in enumerate(row):
                try:
                    valor = float(valor)
                    valor = f'{valor:.2f}'.replace('.',',') + '.-'
                except:
                    pass
                self.canvas.drawCentredString(
                    col * props['ancho'] + props['x'], 
                    - fila * props['alto'] + props['y'], 
                    str(valor),
                )
        
    def generar_pdf(self, salida: str, campos_guardados: dict, imprimir = False):
        self.canvas = canvas.Canvas(salida, pagesize=A4)
        self.campos = campos_guardados
        
        tabla = self.tabla.copy()
        while len(tabla) > 26:
            self.generar_pagina(tabla.loc[:26,:], imprimir)
            tabla = tabla.loc[26:,:].reset_index(drop=True)
        self.generar_pagina(tabla, imprimir)
        
        self.canvas.save()