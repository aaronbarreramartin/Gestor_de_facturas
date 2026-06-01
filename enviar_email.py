import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from utils import nombre_archivo

def enviar_email(datos_rem: dict[str], destinatario: str, asunto: str, cuerpo: str, archivo: str = None):
    remitente = datos_rem['email']
    contraseña = datos_rem['contrasena']

    msg = MIMEMultipart()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain"))

    if archivo:
        with open(archivo, "rb") as f:
            adjunto = MIMEBase("application", "octet-stream")
            adjunto.set_payload(f.read())
            encoders.encode_base64(adjunto)
            adjunto.add_header("Content-Disposition", f"attachment; filename={nombre_archivo(archivo)}")
            msg.attach(adjunto)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(remitente, contraseña)
        servidor.sendmail(remitente, destinatario, msg.as_string())