from pathlib import Path
import json
from utils import get_path

class DatosAlmacenados:    
    def __init__(self):
        self.path = get_path()
        self.ARCHIVO_CLIENTES = self.path / 'datos' / 'clientes.json'
        self.ARCHIVO_CAMPOS = self.path / 'datos' / 'campos.json'
        self.cargar_clientes()
        self.cargar_campos()
    
    def cargar_clientes(self):
        datos = {}
        if self.ARCHIVO_CLIENTES.exists():
            with open(self.ARCHIVO_CLIENTES, 'r', encoding='utf-8') as f:
                datos = json.load(f)
        self.datos_clientes = datos
    
    def actualizar_datos(self, datos: dict):
        for k, v in datos.items():
            self.datos_clientes[k] = v
        self.guardar_datos()
    
    def guardar_datos(self):
        with open(self.ARCHIVO_CLIENTES, 'w', encoding='utf-8') as f:
            json.dump(self.datos_clientes, f, indent=4)
            
    def obtener_cliente(self, nombre: str) -> dict:
        return self.datos_clientes.get(nombre)
    
    def clientes(self) -> dict:
        return self.datos_clientes
    
    def lista_clientes(self) -> list:
        return list(self.clientes().keys()) 
    
    def eliminar_cliente(self, cliente: str):
        self.datos_clientes.pop(cliente, None)
        self.guardar_datos()
        
    def cargar_campos(self):
        campos = {}
        if self.ARCHIVO_CAMPOS.exists():
            with open(self.ARCHIVO_CAMPOS, 'r', encoding='utf-8') as f:
                campos = json.load(f)
        self.campos_guardados = campos
    
    def guardar_campos(self):
        with open(self.ARCHIVO_CAMPOS, 'w', encoding='utf-8') as f:
            json.dump(self.campos_guardados, f, indent=4)
              
    def prop_guardadas(self) -> dict:
        return self.campos_guardados
    
    def remitente(self) -> dict:
        archivo = self.path / 'datos' / 'email.json'
        datos = {}
        if archivo.exists():
            with open(archivo, 'r') as f:
                datos = json.load(f)
        return datos