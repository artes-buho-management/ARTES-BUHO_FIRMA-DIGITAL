#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-manual-v2.py
Manual de usuario PDF v1.0 — ARTES BUHO Firma Digital
Actualizado tras auditoria completa. Abril 2026.
Desarrollado por RUBEN COTON.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

COLOR_RED    = colors.HexColor("#E63027")
COLOR_YELLOW = colors.HexColor("#F4C20D")
COLOR_WHITE  = colors.white
COLOR_DARK   = colors.HexColor("#1A1A1A")
COLOR_GRAY   = colors.HexColor("#555555")
COLOR_MUTED  = colors.HexColor("#888888")
COLOR_LIGHT  = colors.HexColor("#FAFAFA")
COLOR_BORDER = colors.HexColor("#E0E0E0")
COLOR_GREEN  = colors.HexColor("#2E9D4A")

OUTPUT_PATH  = r"C:\Users\elrub\Desktop\Manual_FirmaDigital_ArtesBuho.pdf"

PAGE_W, PAGE_H = A4
MARGIN_L = 22 * mm
MARGIN_R = 22 * mm
MARGIN_T = 22 * mm
MARGIN_B = 22 * mm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


def latin1(s):
    """Sanitiza texto a Latin-1 para evitar errores de renderizado."""
    return str(s).encode("latin-1", "replace").decode("latin-1")


def header(c, title, page, total):
    h = 14 * mm
    c.setFillColor(COLOR_RED)
    c.rect(0, PAGE_H - h, PAGE_W, h, fill=1, stroke=0)
    c.setFillColor(COLOR_WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_L, PAGE_H - h + 4.5 * mm, latin1(title))
    c.setFont("Helvetica", 9)
    c.drawRightString(PAGE_W - MARGIN_R, PAGE_H - h + 4.5 * mm,
                      f"Pagina {page} de {total}")


def footer(c):
    h = 9 * mm
    c.setFillColor(COLOR_YELLOW)
    c.rect(0, 0, PAGE_W, h, fill=1, stroke=0)
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN_L, 3 * mm,
                 "ARTES BUHO MANAGEMENT  |  Firma Digital v1.0  |  RUBEN COTON  |  Abril 2026")
    c.setFont("Helvetica", 7.5)
    c.drawRightString(PAGE_W - MARGIN_R, 3 * mm, "booking@artesbuhomanagement.com")


def section(c, text, y):
    c.setFillColor(COLOR_RED)
    c.rect(MARGIN_L, y - 1 * mm, 4, 7 * mm, fill=1, stroke=0)
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(MARGIN_L + 8, y + 1.8 * mm, latin1(text))
    return y - 10 * mm


def paragraph(c, text, y, size=10, font="Helvetica", color=COLOR_DARK, leading=14):
    c.setFillColor(color)
    c.setFont(font, size)
    # Simple word wrap
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if c.stringWidth(test, font, size) > CONTENT_W:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    for line in lines:
        c.drawString(MARGIN_L, y, latin1(line))
        y -= leading
    return y


def bullet(c, text, y, size=10, color=COLOR_DARK):
    c.setFillColor(COLOR_RED)
    c.circle(MARGIN_L + 3, y + 3, 1.5, fill=1, stroke=0)
    return paragraph(c, text, y, size, color=color) - 3


def numbered(c, num, text, y, size=10):
    c.setFillColor(COLOR_RED)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN_L, y, f"{num}.")
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica", size)
    words = text.split()
    lines = []
    current = ""
    indent = 8 * mm
    avail_w = CONTENT_W - indent
    for w in words:
        test = (current + " " + w).strip()
        if c.stringWidth(test, "Helvetica", size) > avail_w:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    for i, line in enumerate(lines):
        c.drawString(MARGIN_L + indent, y, latin1(line))
        y -= 14
    return y - 4


def info_box(c, title, text, y, accent=COLOR_YELLOW, h=26 * mm):
    c.setFillColor(COLOR_LIGHT)
    c.setStrokeColor(COLOR_BORDER)
    c.rect(MARGIN_L, y - h, CONTENT_W, h, fill=1, stroke=1)
    c.setFillColor(accent)
    c.rect(MARGIN_L, y - h, 4, h, fill=1, stroke=0)
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_L + 8, y - 6 * mm, latin1(title))
    c.setFont("Helvetica", 9)
    # wrap text inside
    words = text.split()
    lines = []
    current = ""
    max_w = CONTENT_W - 12 * mm
    for w in words:
        test = (current + " " + w).strip()
        if c.stringWidth(test, "Helvetica", 9) > max_w:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    cy = y - 11 * mm
    for line in lines[:5]:
        c.drawString(MARGIN_L + 8, cy, latin1(line))
        cy -= 12
    return y - h - 5 * mm


def new_page(c, title, page, total):
    c.showPage()
    header(c, title, page, total)
    footer(c)
    return PAGE_H - 20 * mm - 14 * mm


# ============================================================
#  GENERACION
# ============================================================

TOTAL = 10
c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
c.setTitle("Manual ARTES BUHO Firma Digital")
c.setAuthor("RUBEN COTON")
c.setSubject("Manual de usuario")

# ------------------------- PAGINA 1: PORTADA -------------------------
c.setFillColor(COLOR_RED)
c.rect(0, PAGE_H - 90 * mm, PAGE_W, 90 * mm, fill=1, stroke=0)
c.setFillColor(COLOR_YELLOW)
c.rect(0, PAGE_H - 96 * mm, PAGE_W, 6 * mm, fill=1, stroke=0)

c.setFillColor(COLOR_WHITE)
c.setFont("Helvetica-Bold", 34)
c.drawCentredString(PAGE_W / 2, PAGE_H - 45 * mm, "ARTES BUHO")
c.setFont("Helvetica-Bold", 20)
c.drawCentredString(PAGE_W / 2, PAGE_H - 58 * mm, "Firma Digital")

c.setFillColor(COLOR_YELLOW)
c.setFont("Helvetica", 12)
c.drawCentredString(PAGE_W / 2, PAGE_H - 72 * mm,
                    "Manual de usuario  |  Version 1.0")

c.setFillColor(COLOR_DARK)
c.setFont("Helvetica-Bold", 14)
c.drawCentredString(PAGE_W / 2, PAGE_H - 125 * mm,
                    "Firma digital PAdES de documentos PDF")
c.setFont("Helvetica", 11)
c.setFillColor(COLOR_GRAY)
c.drawCentredString(PAGE_W / 2, PAGE_H - 135 * mm,
                    "Compatible con certificados FNMT, DNIe y representante")

c.setFont("Helvetica-Bold", 11)
c.setFillColor(COLOR_DARK)
c.drawCentredString(PAGE_W / 2, 70 * mm, "Desarrollado por RUBEN COTON")
c.setFont("Helvetica", 10)
c.setFillColor(COLOR_GRAY)
c.drawCentredString(PAGE_W / 2, 62 * mm, "Abril 2026  -  Madrid, Espana")

c.setFont("Helvetica", 9)
c.setFillColor(COLOR_MUTED)
c.drawCentredString(PAGE_W / 2, 45 * mm,
                    "ARTES BUHO MANAGEMENT  -  booking@artesbuhomanagement.com")
c.drawCentredString(PAGE_W / 2, 39 * mm, "100% portatil  -  Sin instalaciones")

footer(c)

# ------------------------- PAGINA 2: INTRODUCCION -------------------------
y = new_page(c, "1. Introduccion", 2, TOTAL)

y = section(c, "Que es ARTES BUHO Firma Digital", y)
y = paragraph(c,
    "Aplicacion portable para firmar documentos PDF con tu certificado digital "
    "instalado en Windows. Formato PAdES (PDF Advanced Electronic Signatures), "
    "compatible con la normativa eIDAS europea. No requiere Autofirma, ni "
    "instalacion, ni conexion a internet.", y)

y -= 4 * mm
y = section(c, "Caracteristicas principales", y)
y = bullet(c, "Firma digital legal (PAdES-B-B, SHA-256).", y)
y = bullet(c, "Interfaz web local — accesible desde cualquier navegador.", y)
y = bullet(c, "Sello visible en la ultima pagina con datos del firmante.", y)
y = bullet(c, "Historial de documentos firmados dentro de la misma carpeta.", y)
y = bullet(c, "Compatible con FNMT, DNIe y certificados de representante.", y)
y = bullet(c, "Servidor solo en localhost — no expuesto a la red.", y)

y -= 4 * mm
y = info_box(c, "Seguridad",
    "La aplicacion solo escucha en 127.0.0.1 (tu propio equipo). Ningun otro "
    "dispositivo de la red puede acceder. Los documentos nunca se suben a "
    "internet — todo se procesa localmente.", y, h=24 * mm)

# ------------------------- PAGINA 3: REQUISITOS -------------------------
y = new_page(c, "2. Requisitos", 3, TOTAL)

y = section(c, "Sistema operativo", y)
y = bullet(c, "Windows 10 o Windows 11 (64 bits).", y)
y = bullet(c, "PowerShell 5.1 o superior (incluido por defecto en Windows).", y)

y -= 3 * mm
y = section(c, "Certificado digital", y)
y = paragraph(c,
    "Necesitas uno de los siguientes certificados instalado en el almacen "
    "\"Personal\" de Windows (la aplicacion lo detecta automaticamente):", y)
y -= 2
y = bullet(c, "Certificado FNMT de persona fisica (gratuito).", y)
y = bullet(c, "DNI electronico (DNIe) con lector de tarjetas.", y)
y = bullet(c, "Certificado de representante de empresa.", y)
y = bullet(c, "Cualquier certificado X.509 con clave privada exportable o no.", y)

y -= 3 * mm
y = section(c, "Espacio y rendimiento", y)
y = bullet(c, "Aproximadamente 70 MB en disco (ejecutable portable).", y)
y = bullet(c, "2 GB de RAM libres (basta con 100 MB mientras se firma).", y)
y = bullet(c, "Puerto 3000 TCP libre (solo en localhost).", y)

y -= 3 * mm
y = info_box(c, "No necesitas",
    "No hace falta Autofirma, ni Adobe Acrobat, ni tener internet, ni ser "
    "administrador del equipo. Solo un certificado instalado y tu PDF.",
    y, h=20 * mm)

# ------------------------- PAGINA 4: INSTALACION CERTIFICADO -------------------------
y = new_page(c, "3. Como conseguir un certificado digital", 4, TOTAL)

y = section(c, "Opcion A - Certificado FNMT (gratuito)", y)
y = numbered(c, 1,
    "Entra en sede.fnmt.gob.es y solicita un certificado de persona fisica.", y)
y = numbered(c, 2,
    "Apunta el codigo de solicitud que te envian.", y)
y = numbered(c, 3,
    "Acude a una oficina de registro (Hacienda, Seguridad Social, "
    "Ayuntamiento) con tu DNI y el codigo.", y)
y = numbered(c, 4,
    "Vuelve a sede.fnmt.gob.es y descarga el certificado desde el mismo "
    "navegador y equipo con los que hiciste la solicitud.", y)
y = numbered(c, 5,
    "El certificado se instala automaticamente en Windows.", y)

y -= 3 * mm
y = section(c, "Opcion B - DNI electronico (DNIe)", y)
y = numbered(c, 1, "Conecta un lector de tarjetas al PC.", y)
y = numbered(c, 2, "Inserta el DNIe en el lector.", y)
y = numbered(c, 3,
    "Windows detecta los certificados del DNIe automaticamente.", y)
y = numbered(c, 4,
    "Necesitaras saber el PIN que te dieron al renovar el DNI.", y)

y -= 3 * mm
y = section(c, "Opcion C - Certificado de representante", y)
y = paragraph(c,
    "Si tu empresa ya tiene un certificado de representante, pidelo al "
    "departamento de administracion. Haz doble clic sobre el archivo .pfx "
    "o .p12 para instalarlo en el almacen personal de Windows.", y)

# ------------------------- PAGINA 5: INSTALACION APP -------------------------
y = new_page(c, "4. Instalacion de la aplicacion", 5, TOTAL)

y = section(c, "Opcion 1 - Descarga desde Google Drive", y)
y = numbered(c, 1,
    "Abre la carpeta compartida \"FIRMA DIGITAL\" en Google Drive (acceso "
    "desde la cuenta booking@artesbuhomanagement.com).", y)
y = numbered(c, 2,
    "Descarga el archivo ArtesBuho-FirmaDigital.exe (unos 66 MB).", y)
y = numbered(c, 3,
    "Guardalo donde prefieras (Escritorio, Descargas, etc.). No requiere "
    "carpeta especial.", y)

y -= 3 * mm
y = section(c, "Opcion 2 - Red corporativa", y)
y = paragraph(c,
    "Si la empresa te ha dado acceso a una carpeta de red, copia el ejecutable "
    "desde ahi a tu equipo local. Siempre ejecutalo desde disco local, nunca "
    "desde la red (seria mas lento).", y)

y -= 3 * mm
y = section(c, "Ejecutar la aplicacion", y)
y = numbered(c, 1,
    "Haz doble clic sobre ArtesBuho-FirmaDigital.exe.", y)
y = numbered(c, 2,
    "Se abrira una ventana negra de consola con el banner ARTES BUHO.", y)
y = numbered(c, 3,
    "El navegador se abrira solo apuntando a http://127.0.0.1:3000.", y)
y = numbered(c, 4,
    "Si Windows Defender SmartScreen avisa, pulsa \"Mas informacion\" y "
    "\"Ejecutar de todos modos\" (el ejecutable no esta firmado por un "
    "certificado de codigo comercial).", y)

y = info_box(c, "Importante",
    "La ventana negra de consola debe quedar abierta mientras usas la "
    "aplicacion. Si la cierras, el servicio se detiene.", y, h=18 * mm)

# ------------------------- PAGINA 6: FIRMAR UN PDF -------------------------
y = new_page(c, "5. Como firmar un PDF", 6, TOTAL)

y = section(c, "Paso a paso", y)

y = numbered(c, 1,
    "Lanza ArtesBuho-FirmaDigital.exe y espera a que se abra el navegador.", y)
y = numbered(c, 2,
    "Comprueba que el indicador inferior izquierdo muestra el nombre de tu "
    "certificado (punto amarillo). Si muestra \"Sin certificado\" aparecera "
    "un aviso con instrucciones de instalacion.", y)
y = numbered(c, 3,
    "Arrastra el PDF al area central, o haz clic para seleccionarlo. "
    "Maximo 15 MB.", y)
y = numbered(c, 4,
    "Pulsa \"Firmar con certificado digital\".", y)
y = numbered(c, 5,
    "Aparecera el selector de certificados de Windows. Elige el que quieras "
    "usar y pulsa Aceptar. Puedes pedir contrasena si el certificado la exige.", y)
y = numbered(c, 6,
    "Espera mientras se aplica el sello visible y la firma digital "
    "(proceso en 4 pasos: seleccion - sello - PAdES - firma).", y)
y = numbered(c, 7,
    "Cuando termine veras \"Documento firmado\" con el nombre del firmante "
    "y la fecha. Pulsa \"Descargar PDF firmado\".", y)
y = numbered(c, 8,
    "Si quieres firmar otro, pulsa \"Firmar otro documento\".", y)

y -= 2 * mm
y = info_box(c, "Donde aparece el sello",
    "En la ultima pagina, esquina inferior derecha. Incluye nombre del "
    "firmante, emisor del certificado, numero de serie, fecha, hora y "
    "validez del certificado.", y, h=22 * mm, accent=COLOR_GREEN)

# ------------------------- PAGINA 7: CARACTERISTICAS AVANZADAS -------------------------
y = new_page(c, "6. Caracteristicas avanzadas", 7, TOTAL)

y = section(c, "Historial de firmas", y)
y = paragraph(c,
    "En el menu lateral, la opcion \"Historial\" muestra todos los documentos "
    "que has firmado en la sesion actual. Puedes volver a descargar "
    "cualquiera o eliminarlo del historial con el boton \"X\".", y)
y = paragraph(c,
    "Los documentos se guardan en la carpeta \"output\" junto al ejecutable. "
    "Si mueves el .exe a otra carpeta, lleva tambien \"output\" si quieres "
    "conservar los firmados.", y)

y -= 3 * mm
y = section(c, "Estado del sistema", y)
y = paragraph(c,
    "La opcion \"Estado\" muestra informacion sobre el certificado detectado, "
    "el motor de firma y el servidor local. Util para verificar antes de "
    "firmar o para soporte tecnico.", y)

y -= 3 * mm
y = section(c, "Notificaciones", y)
y = paragraph(c,
    "La aplicacion muestra notificaciones en la esquina superior derecha "
    "para exitos, errores y avisos. Son temporales (se cierran solas) y "
    "puedes cerrarlas con la X.", y)

y -= 3 * mm
y = section(c, "Avisos automaticos", y)
y = paragraph(c,
    "La aplicacion te avisara si:", y)
y = bullet(c, "El PDF ya contenia firmas previas (anadir una nueva podria invalidarlas).", y)
y = bullet(c, "La pagina esta rotada (el sello se ajusta automaticamente).", y)
y = bullet(c, "La firma se aplico con cadena incompleta (modo EndCertOnly).", y)

# ------------------------- PAGINA 8: PROBLEMAS COMUNES -------------------------
y = new_page(c, "7. Problemas comunes", 8, TOTAL)

y = section(c, "\"No se ha detectado certificado digital\"", y)
y = paragraph(c,
    "Tu almacen de Windows no tiene certificados validos con clave privada. "
    "Revisa los pasos de la seccion 3 para instalar uno. Si crees que ya "
    "tienes uno, abre certmgr.msc y comprueba la carpeta \"Personal - "
    "Certificados\".", y)

y -= 2 * mm
y = section(c, "\"El puerto 3000 ya esta en uso\"", y)
y = paragraph(c,
    "Otra aplicacion o una instancia anterior esta usando el puerto. Cierra "
    "la ventana negra de consola de la otra instancia y vuelve a lanzar.", y)

y -= 2 * mm
y = section(c, "\"El archivo supera los 15 MB\"", y)
y = paragraph(c,
    "Limite de seguridad. Comprime el PDF con herramientas online gratuitas "
    "(ej. ilovepdf.com) o reduce la resolucion de las imagenes antes de firmar.", y)

y -= 2 * mm
y = section(c, "\"Firma cancelada por el usuario\"", y)
y = paragraph(c,
    "Pulsaste Cancelar en el selector de certificados. Vuelve a pulsar "
    "\"Firmar con certificado digital\" para reintentar.", y)

y -= 2 * mm
y = section(c, "El ejecutable no arranca", y)
y = paragraph(c,
    "Comprueba que Windows Defender no lo ha bloqueado. Haz clic derecho "
    "sobre el .exe, Propiedades, marca \"Desbloquear\" abajo y Aceptar. "
    "Vuelve a ejecutar.", y)

y -= 2 * mm
y = section(c, "Se abren dos pestanas del navegador", y)
y = paragraph(c,
    "Corregido en la version 1.0. Si te sigue pasando, asegurate de usar el "
    "ejecutable mas reciente de Drive.", y)

# ------------------------- PAGINA 9: SEGURIDAD Y AUDITORIA -------------------------
y = new_page(c, "8. Seguridad y validez legal", 9, TOTAL)

y = section(c, "Validez legal de la firma", y)
y = paragraph(c,
    "La firma que genera esta aplicacion es PAdES-B-B (nivel basico) con "
    "SHA-256. Tiene validez legal en toda la Union Europea segun el "
    "reglamento eIDAS (910/2014) siempre que el certificado utilizado este "
    "emitido por una autoridad certificadora cualificada (FNMT, DNIe, "
    "Camerfirma, etc.).", y)

y -= 2 * mm
y = section(c, "Sello de tiempo (timestamp)", y)
y = paragraph(c,
    "La firma NO incluye sello de tiempo de una TSA (Time Stamping Authority). "
    "La fecha/hora del sello visual proviene del reloj del equipo. Si "
    "necesitas una firma con nivel PAdES-B-T o PAdES-B-LT (con TSA), usa "
    "Adobe Acrobat Pro o consulta al desarrollador.", y)

y -= 2 * mm
y = section(c, "Privacidad", y)
y = paragraph(c,
    "Los PDFs nunca salen de tu equipo. El procesamiento es 100% local. El "
    "servidor web escucha solo en 127.0.0.1 (localhost) y rechaza conexiones "
    "externas. La aplicacion no envia telemetria.", y)

y -= 2 * mm
y = section(c, "Auditoria v1.0 - mejoras implementadas", y)
y = bullet(c, "Bind restringido a localhost (no accesible desde red).", y)
y = bullet(c, "Rate limiting (30 peticiones/minuto por IP).", y)
y = bullet(c, "Validacion estricta de nombres de archivo (anti path traversal).", y)
y = bullet(c, "Limpieza automatica de archivos temporales al arrancar.", y)
y = bullet(c, "Validacion de thumbprint de certificado (anti inyeccion PS).", y)
y = bullet(c, "Deteccion de firmas previas en el PDF.", y)
y = bullet(c, "Soporte de paginas rotadas.", y)
y = bullet(c, "Fallback de firma si falla WholeChain.", y)
y = bullet(c, "Notificaciones visuales en vez de alertas nativas.", y)
y = bullet(c, "Proceso por peticion (sin estado compartido).", y)

# ------------------------- PAGINA 10: SOPORTE Y CONTACTO -------------------------
y = new_page(c, "9. Soporte y contacto", 10, TOTAL)

y = section(c, "Contacto", y)
y = paragraph(c,
    "Para dudas, sugerencias o reportar problemas:", y)
y -= 2

y = bullet(c, "Email: booking@artesbuhomanagement.com", y)
y = bullet(c, "Desarrollador: RUBEN COTON", y)
y = bullet(c, "WhatsApp: +34 6XX XXX XXX", y)
y = bullet(c, "Videollamada: calendar.app.google (cuenta booking)", y)

y -= 4 * mm
y = section(c, "Datos de la aplicacion", y)
y = paragraph(c, "Nombre: ARTES BUHO Firma Digital", y, font="Helvetica-Bold")
y = paragraph(c, "Version: 1.0 (auditada - abril 2026)", y)
y = paragraph(c, "Licencia: interna ARTES BUHO MANAGEMENT", y)
y = paragraph(c, "Formato de firma: PAdES-B-B con SHA-256", y)
y = paragraph(c, "Plataforma: Windows 10/11 64 bits", y)
y = paragraph(c, "Puerto local: 3000 (TCP - solo 127.0.0.1)", y)

y -= 4 * mm
y = section(c, "Actualizaciones", y)
y = paragraph(c,
    "La version mas reciente siempre esta en la carpeta \"FIRMA DIGITAL\" "
    "de Google Drive (cuenta booking@artesbuhomanagement.com). Descargala "
    "y sustituye tu ejecutable antiguo. La carpeta \"output\" con tu "
    "historial no se ve afectada si la conservas.", y)

y -= 4 * mm
y = info_box(c, "Aviso legal",
    "Esta aplicacion es de uso interno de ARTES BUHO MANAGEMENT. El uso "
    "responsable es responsabilidad del firmante. Conserva una copia de "
    "seguridad de tu certificado digital y su contrasena - no se pueden "
    "recuperar si se pierden.", y, h=26 * mm, accent=COLOR_RED)

# ------------------------- CIERRE -------------------------
c.showPage()
# Pagina final minimalista de contraportada
c.setFillColor(COLOR_RED)
c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
c.setFillColor(COLOR_YELLOW)
c.rect(0, PAGE_H / 2 - 3, PAGE_W, 6, fill=1, stroke=0)
c.setFillColor(COLOR_WHITE)
c.setFont("Helvetica-Bold", 28)
c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 40, "ARTES BUHO")
c.setFont("Helvetica", 14)
c.drawCentredString(PAGE_W / 2, PAGE_H / 2 + 20, "MANAGEMENT")
c.setFillColor(COLOR_YELLOW)
c.setFont("Helvetica-Bold", 16)
c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 30, "Firma Digital")
c.setFillColor(COLOR_WHITE)
c.setFont("Helvetica", 10)
c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 50,
                    "Desarrollado por RUBEN COTON  |  Abril 2026")
c.drawCentredString(PAGE_W / 2, PAGE_H / 2 - 65,
                    "booking@artesbuhomanagement.com")

c.save()
print(f"Manual generado en: {OUTPUT_PATH}")
