import ttkbootstrap as ttk
import subprocess
from enviar_email import enviar_email
from gestion_datos import DatosAlmacenados
from factura import Factura
from gui import *
from utils import get_path

class GestorFacturas:
    def __init__(self, root: ttk.Window):
        self.root = root
        self.root.state('zoomed')
        self.estilo()
        self.icono()
        self.datos = DatosAlmacenados()
        self.factura = None
        self.crear_interfaz()    
       
    def icono(self):
        path = get_path()
        ico_path = path / 'datos' / 'icon.ico'
        if ico_path.exists():
            self.root.iconbitmap(str(ico_path))
    
    def estilo(self):
        style = ttk.Style()
        style.configure('TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('Grande.TButton', font=('Montserrat', 11, 'bold'))
        style.configure('TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('TLabelframe.Label', font=('Montserrat', 13, 'bold'))
        style.configure('Titulo.TLabel', font=('Montserrat', 13, 'bold'))
        style.configure('Treeview', font=('Montserrat', 11), rowheight=18)
        style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'), background='#414141')
    
    def crear_interfaz(self):
        frame_der = ttk.Frame(self.root)
        frame_der.pack(side='right', padx=10, pady=10, fill='both')

        frame_izq = ttk.Frame(self.root)
        frame_izq.pack(side='left', padx=10, pady=10, fill='y')

        self.frame_centro = ttk.Frame(self.root)
        self.frame_centro.pack(padx=10, pady=30, side='top',  fill='both', expand=True)
        self.frame_centro.grid_anchor('center')
        
        self.campos_imput = [
            {'nombre': 'Cliente'},
            {'nombre': 'Nombre'},
            {'nombre': 'Dirección'},
            {'nombre': 'CIF'},
            {'nombre': 'Fecha', 'default': dt.date.today().strftime('%d.%m.%Y')},
            {'nombre': 'Número factura'}            
        ]
        
        self.imput = InputDatos(frame_der, self.campos_imput, multilinea=['Cliente', 'Dirección'])
        
        columnas_tabla = ('Fecha', 'Concepto', 'Importe')
        self.tabla_servicios = Tabla(frame_der, columnas_tabla)
        
        clientes = self.datos.lista_clientes()
        self.lista_clientes = Lista(
            frame_izq, 
            seleccionado=self.cargar, 
            titulo='Clientes guardados', 
            lista=clientes
        ) 
        
        datos = self.imput.campos()
        
        self.email = EmailPreview(self.frame_centro)
        
        email, asunto, cuerpo = self.formato_email(datos)
        self.email.actualizar(email, asunto, cuerpo)
        
        self.mostrar_botones()
        
    def formato_email(self, datos: dict[str]):    
        try:
            fecha = dt.datetime.strptime(datos.get('Fecha'), '%d.%m.%Y')
        except:
            fecha = dt.datetime.today()
        email = datos.get('Email', '')
        mes = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        cuerpo = f'Buenas tardes {datos['Nombre']}, le envio la fatura de {mes[fecha.month]}.'
        asunto = f'Factura de {mes[fecha.month]}'
        return email, asunto, cuerpo
               
    def calc_bruto(self, tabla: pd.DataFrame) -> float:
        return float(pd.to_numeric(tabla['Importe'], errors='coerce').sum())
    
    def calc_neto(self, bruto: float, iva: float = 21) -> float:
        return bruto * (1 + iva/100)
        
    def mostrar_botones(self):
        ttk.Button(
            self.imput.frame_datos,
            text='Guardar',
            bootstyle=PRIMARY,
            command=self.guardar_cliente
        ).pack(side='right', pady=15, padx=20, fill='y', expand=True)

        ttk.Button(
            self.lista_clientes.frame,
            text='Nuevo cliente',
            bootstyle=PRIMARY,
            command=self.nuevo_cliente
        ).pack(pady=5, side='right', padx=4)

        ttk.Button(
            self.lista_clientes.frame,
            text='Eliminar cliente',
            bootstyle=DANGER,
            command=self.eliminar_cliente
        ).pack(pady=5, side='left', padx=4)
    
        ttk.Button(
            self.frame_centro,
            text='Guardar Factura',
            bootstyle=SUCCESS,
            padding=(30, 15),
            style='Grande.TButton',
            command=self.guardar_factura
        ).pack(side='bottom', pady=10)
    
    def nuevo_cliente(self):
        self.imput.limpiar_entradas()
        self.tabla_servicios.limpiar()
    
    def guardar_factura(self):
        if self.factura is not None and self.imput.guardar(campo_id='Cliente'):
            
            datos = self.calcular_datos()
            
            self.factura.insertar_datos(datos.copy())
            nombre_archivo = self.factura.nombre()
            carpeta = get_path() / 'Facturas'
            carpeta.mkdir(exist_ok=True)
            ruta_salida_pdf = str(carpeta / (str(nombre_archivo) + '.pdf'))
            
            resultado = Messagebox.show_question(
                message='¿Qué deseas hacer?',
                title='Confirmar acción',
                buttons=['Guardar PDF:primary', 'Enviar email:primary', 'Imprimir:primary']
            )
            
            if resultado == 'Enviar email':
                self.factura.generar_pdf(ruta_salida_pdf, self.datos.prop_guardadas())
                self.enviar_email(ruta_salida_pdf) 
                self.guardar_df(nombre_archivo)
            elif resultado == 'Imprimir':
                self.factura.generar_pdf(ruta_salida_pdf, self.datos.prop_guardadas(), imprimir=True)
                self.imprimir_pdf(ruta_salida_pdf)
                self.guardar_df(nombre_archivo)
                self.factura.generar_pdf(ruta_salida_pdf, self.datos.prop_guardadas())
            elif resultado == 'Guardar PDF':
                self.factura.generar_pdf(ruta_salida_pdf, self.datos.prop_guardadas())
                self.guardar_df(nombre_archivo)
            
    def guardar_df(self, nombre: str):
        carpeta = get_path() / 'csvs' 
        carpeta.mkdir(exist_ok=True)
        csv = carpeta / f'{nombre}.csv'
        df = self.tabla_servicios.df()
        if not df.empty:
            df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d.%m.%y')
            df = df.sort_values('Fecha')
            df.to_csv(csv, index=False)
            
    def imprimir_pdf(self, ruta_pdf: str):
        sumatra = get_path() / 'datos' / 'SumatraPDF.exe'
        subprocess.run([
            sumatra,
            "-print-to-default",
            "-print-settings", "noscale",
            "-silent",
            ruta_pdf
        ])

    def calcular_datos(self) -> dict:
        df = self.tabla_servicios.df()
        self.factura.añadir_tabla(df)
        datos = self.imput.campos()
        datos['CIF'] = 'C.I.F.  ' + datos.get('CIF')
        
        bruto = round(self.calc_bruto(df), 2)
        neto = round(self.calc_neto(bruto), 2)
        datos_compuestos = {
            'Bruto': bruto,
            'Iva': 21,
            'Desc': round(neto - bruto, 2),
            'Neto': neto 
        }
        
        datos.update(datos_compuestos)
        
        return datos
            
    def enviar_email(self, archivo_pdf):
        campos = self.email.campos()
        remitente = self.datos.remitente()
        enviar_email(remitente, campos['destinatario'], campos['asunto'], campos['cuerpo'], archivo_pdf)

    def cargar(self, cliente: str):
        datos_cliente = self.datos.obtener_cliente(cliente)
        self.imput.cargar(datos_cliente, mantener=['Número factura', 'Fecha'])
        datos = self.imput.campos()
        datos_cliente.update(datos)
        
        destinatario, asunto, cuerpo = self.formato_email(datos_cliente)
        self.email.actualizar(destinatario, asunto, cuerpo)
        
        plantilla = get_path() / 'datos' / 'plantilla.png'
        self.factura = Factura(plantilla)
        self.factura.insertar_datos(datos_cliente.copy())
        
        
        self.tabla_servicios.limpiar()
        try:
            path_df = get_path() / 'csvs' / (self.factura.nombre() + '.csv')
            df = pd.DataFrame()
            if path_df.exists():
                df = pd.read_csv(path_df, parse_dates=['Fecha'])
                df['Fecha'] = df['Fecha'].apply(lambda x: x.strftime('%d.%m.%y'))
                self.tabla_servicios.cargar_df(df)
            self.factura.añadir_tabla(df)
        except:
            Messagebox.show_error('Pon una fecha con el formato "DD-MM-AAAA" para cargar los servicios de ese mes.', title='Fecha')

    def guardar_cliente(self):
        cliente = self.imput.guardar(campo_id='Cliente')
        if self.factura is not None and cliente:
            email = self.email.campos()['destinatario']
            cliente[list(cliente.keys())[0]]['Email'] = email 
            self.datos.actualizar_datos(cliente)
            clientes = self.datos.lista_clientes() 
            self.lista_clientes.actualizar_lista(clientes)
            self.guardar_df(self.factura.nombre())

    def eliminar_cliente(self):
        nombre = self.lista_clientes.eliminar_seleccion()
        if nombre:
            self.datos.eliminar_cliente(nombre)
            self.imput.limpiar_entradas()  
            clientes = self.datos.lista_clientes() 
            self.lista_clientes.actualizar_lista(clientes)

if __name__ == '__main__':
    root = ttk.Window(themename='darkly')    
    root.tk.call('tk', 'scaling', 1.6)
    root.title('Gestor de Facturas')
    app = GestorFacturas(root)
    root.mainloop()
