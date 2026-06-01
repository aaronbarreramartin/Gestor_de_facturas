# Gestor de Facturas

Aplicación de escritorio desarrollada en Python para la gestión de facturas.

## Funcionalidades

- Generación de facturas en PDF a partir de una plantilla
- Envío automático por email
- Gestión de clientes con historial de servicios
- Impresión directa
- Exportación de registros en CSV para potencial análisis posterior

## Tecnologías

- Python 3.13
- tkinter + ttkbootstrap
- ReportLab
- Pandas
- PyInstaller (empaquetado como .exe)

## Uso

Requiere un archivo `datos/email.json` con las credenciales del remitente:
```json
{
    "email": "tu@email.com",
    "contrasena": "tu_contraseña"
}
```
