#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate-manual.py
Genera el manual de usuario PDF de ARTES BUHO Firma Digital.
Desarrollado por RUBEN COTON — Abril 2026
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ---------------------------------------------------------------------------
# Constantes de color corporativo
# ---------------------------------------------------------------------------
COLOR_RED    = colors.HexColor("#E63027")
COLOR_YELLOW = colors.HexColor("#F4C20D")
COLOR_WHITE  = colors.white
COLOR_BLACK  = colors.black
COLOR_DARK   = colors.HexColor("#1A1A1A")
COLOR_GRAY   = colors.HexColor("#555555")
COLOR_LIGHT  = colors.HexColor("#F5F5F5")
COLOR_BORDER = colors.HexColor("#DDDDDD")

OUTPUT_PATH = r"C:\Users\elrub\Desktop\Manual_FirmaDigital_ArtesBuho.pdf"

PAGE_W, PAGE_H = A4  # 595 x 842 pts
MARGIN_L = 22 * mm
MARGIN_R = 22 * mm
MARGIN_T = 22 * mm
MARGIN_B = 22 * mm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


# ---------------------------------------------------------------------------
# Helpers de dibujo
# ---------------------------------------------------------------------------

def draw_header_bar(c: canvas.Canvas, title: str, page_num: int, total: int):
    """Barra superior roja con titulo de pagina."""
    bar_h = 14 * mm
    c.setFillColor(COLOR_RED)
    c.rect(0, PAGE_H - bar_h, PAGE_W, bar_h, fill=1, stroke=0)

    c.setFillColor(COLOR_WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(MARGIN_L, PAGE_H - bar_h + 4 * mm, title)

    c.setFont("Helvetica", 9)
    c.drawRightString(PAGE_W - MARGIN_R, PAGE_H - bar_h + 4 * mm,
                      f"Pagina {page_num} de {total}")


def draw_footer(c: canvas.Canvas):
    """Pie de pagina amarillo con datos de empresa."""
    bar_h = 9 * mm
    c.setFillColor(COLOR_YELLOW)
    c.rect(0, 0, PAGE_W, bar_h, fill=1, stroke=0)

    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(MARGIN_L, 3 * mm,
                 "ARTES BUHO MANAGEMENT  |  Firma Digital  |  Desarrollado por RUBEN COTON  |  Abril 2026")
    c.setFont("Helvetica", 7.5)
    c.drawRightString(PAGE_W - MARGIN_R, 3 * mm, "booking@artesbuhomanagement.com")


def draw_section_title(c: canvas.Canvas, text: str, y: float) -> float:
    """Titulo de seccion con barra roja izquierda. Devuelve nueva y."""
    bar_w = 4
    c.setFillColor(COLOR_RED)
    c.rect(MARGIN_L, y - 1 * mm, bar_w, 7 * mm, fill=1, stroke=0)

    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN_L + bar_w + 4, y + 1 * mm, text)
    return y - 10 * mm


def draw_body_text(c: canvas.Canvas, text: str, y: float,
                   font="Helvetica", size=10, color=COLOR_DARK,
                   indent=0, line_h=5.5 * mm) -> float:
    """Dibuja texto con ajuste automatico de linea. Devuelve nueva y."""
    c.setFillColor(color)
    c.setFont(font, size)
    available_w = CONTENT_W - indent
    words = text.split()
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, font, size) <= available_w:
            line = test
        else:
            c.drawString(MARGIN_L + indent, y, line)
            y -= line_h
            line = word
    if line:
        c.drawString(MARGIN_L + indent, y, line)
        y -= line_h
    return y


def draw_bullet(c: canvas.Canvas, text: str, y: float,
                font="Helvetica", size=10, indent=6 * mm,
                color=COLOR_DARK) -> float:
    """Bullet point con circulo rojo. Devuelve nueva y."""
    bullet_x = MARGIN_L + indent - 4 * mm
    c.setFillColor(COLOR_RED)
    c.circle(bullet_x, y + 1.5, 2, fill=1, stroke=0)

    return draw_body_text(c, text, y, font=font, size=size,
                          color=color, indent=indent)


def draw_step_box(c: canvas.Canvas, number: int, text: str, y: float) -> float:
    """Caja numerada para pasos de uso. Devuelve nueva y."""
    box_h = 10 * mm
    # Fondo alterno
    bg = COLOR_LIGHT if number % 2 == 1 else COLOR_WHITE
    c.setFillColor(bg)
    c.roundRect(MARGIN_L, y - box_h + 3, CONTENT_W, box_h, 3, fill=1, stroke=0)

    # Borde izquierdo de color
    c.setFillColor(COLOR_YELLOW)
    c.rect(MARGIN_L, y - box_h + 3, 5, box_h, fill=1, stroke=0)

    # Numero
    c.setFillColor(COLOR_RED)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN_L + 10, y - 2 * mm, str(number))

    # Texto del paso
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica", 10)
    # truncar si es muy largo (para caber en una linea)
    max_w = CONTENT_W - 20 * mm
    while c.stringWidth(text, "Helvetica", 10) > max_w and len(text) > 10:
        text = text[:-4] + "..."
    c.drawString(MARGIN_L + 20 * mm, y - 2 * mm, text)

    return y - box_h - 1.5 * mm


def draw_info_box(c: canvas.Canvas, title: str, lines: list, y: float,
                  bg_color=None, border_color=None) -> float:
    """Cuadro de informacion con fondo. Devuelve nueva y."""
    bg = bg_color or COLOR_LIGHT
    border = border_color or COLOR_BORDER
    line_h = 5.5 * mm
    padding = 4 * mm
    box_h = padding * 2 + (len(lines) + (1 if title else 0)) * line_h

    c.setFillColor(bg)
    c.setStrokeColor(border)
    c.roundRect(MARGIN_L, y - box_h, CONTENT_W, box_h, 4, fill=1, stroke=1)

    cy = y - padding - line_h * 0.4
    if title:
        c.setFillColor(COLOR_RED)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN_L + padding, cy, title)
        cy -= line_h

    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica", 9.5)
    for line in lines:
        c.drawString(MARGIN_L + padding + 4, cy, line)
        cy -= line_h

    return y - box_h - 3 * mm


def draw_troubleshoot_row(c: canvas.Canvas, problem: str, solution: str,
                          y: float, alt: bool) -> float:
    """Fila de tabla de problemas. Devuelve nueva y."""
    row_h = 11 * mm
    col_split = MARGIN_L + CONTENT_W * 0.42

    bg = colors.HexColor("#FFF5F5") if alt else COLOR_WHITE
    c.setFillColor(bg)
    c.rect(MARGIN_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)

    # Linea divisoria vertical
    c.setStrokeColor(COLOR_BORDER)
    c.line(col_split, y, col_split, y - row_h)
    # Linea inferior
    c.line(MARGIN_L, y - row_h, MARGIN_L + CONTENT_W, y - row_h)

    # Texto problema
    c.setFillColor(COLOR_RED)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN_L + 3, y - 4 * mm, problem)

    # Texto solucion
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica", 9)
    max_w = MARGIN_L + CONTENT_W - col_split - 4
    sol = solution
    while c.stringWidth(sol, "Helvetica", 9) > max_w and len(sol) > 8:
        sol = sol[:-4] + "..."
    c.drawString(col_split + 4, y - 4 * mm, sol)

    # Segunda linea si solucion es larga
    if sol != solution:
        resto = solution[len(sol.rstrip("...")):]
        if resto:
            c.drawString(col_split + 4, y - 4 * mm - 4.5 * mm, resto)

    return y - row_h


# ---------------------------------------------------------------------------
# Paginas
# ---------------------------------------------------------------------------

def page_cover(c: canvas.Canvas):
    """Pagina 1: Portada."""
    # Fondo completo rojo en la mitad superior
    c.setFillColor(COLOR_RED)
    c.rect(0, PAGE_H * 0.42, PAGE_W, PAGE_H * 0.58, fill=1, stroke=0)

    # Logo/marca en bloque amarillo
    c.setFillColor(COLOR_YELLOW)
    c.roundRect(MARGIN_L, PAGE_H * 0.72, CONTENT_W, 18 * mm, 6, fill=1, stroke=0)
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.72 + 6 * mm, "ARTES BUHO MANAGEMENT")

    # Titulo principal
    c.setFillColor(COLOR_WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.60, "FIRMA DIGITAL")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.60 - 13 * mm, "MANUAL DE USO")

    # Linea separadora amarilla
    c.setStrokeColor(COLOR_YELLOW)
    c.setLineWidth(3)
    c.line(MARGIN_L + 20 * mm, PAGE_H * 0.44, PAGE_W - MARGIN_R - 20 * mm, PAGE_H * 0.44)
    c.setLineWidth(1)

    # Bloque inferior — descripcion
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica", 11)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.37,
                        "Aplicacion portatil para firma digital de documentos PDF")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(COLOR_RED)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.30, "Desarrollado por RUBEN COTON")

    c.setFillColor(COLOR_GRAY)
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W / 2, PAGE_H * 0.24, "Abril 2026")

    # Rectangulo decorativo inferior
    c.setFillColor(COLOR_YELLOW)
    c.rect(0, 0, PAGE_W, 9 * mm, fill=1, stroke=0)
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(PAGE_W / 2, 3 * mm,
                        "ARTES BUHO MANAGEMENT  |  booking@artesbuhomanagement.com")


def page_what_is(c: canvas.Canvas, page_num: int, total: int):
    """Pagina 2: Que es esta aplicacion."""
    draw_header_bar(c, "QUE ES ESTA APLICACION", page_num, total)
    draw_footer(c)

    y = PAGE_H - 22 * mm - 8 * mm
    y = draw_section_title(c, "Descripcion general", y)
    y -= 2 * mm

    intro = ("ARTES BUHO Firma Digital es una aplicacion portatil para Windows "
             "que permite firmar digitalmente documentos PDF de forma rapida, "
             "segura y sin instalacion adicional.")
    y = draw_body_text(c, intro, y)
    y -= 4 * mm

    bullets = [
        "Solo necesitas hacer doble clic en el archivo .exe para arrancarla.",
        "Abre automaticamente el navegador en localhost:3000.",
        "No requiere conexion a internet para firmar.",
        "Genera firmas PAdES (estandar europeo, conforme con eIDAS).",
        "Usa los certificados digitales ya instalados en Windows.",
        "No almacena ni envia tus documentos a ningun servidor externo.",
    ]
    for b in bullets:
        y = draw_bullet(c, b, y)
    y -= 6 * mm

    y = draw_section_title(c, "Formato de firma PAdES", y)
    y -= 2 * mm

    desc_pades = ("PAdES (PDF Advanced Electronic Signatures) es el formato de "
                  "firma electronica avanzada definido por la norma ETSI EN 319 122. "
                  "Es el estandar exigido en la Union Europea por el reglamento eIDAS "
                  "para documentos legalmente vinculantes.")
    y = draw_body_text(c, desc_pades, y)
    y -= 4 * mm

    features = [
        "Firma embebida directamente en el PDF — no es un archivo adjunto separado.",
        "Permite verificacion offline con Adobe Acrobat u otros validadores.",
        "Incluye sello de tiempo y datos del firmante visibles en el documento.",
        "Compatible con el estandar europeo eIDAS para firma electronica avanzada.",
    ]
    for f in features:
        y = draw_bullet(c, f, y)
    y -= 6 * mm

    y = draw_section_title(c, "Certificados de Windows", y)
    y -= 2 * mm

    cert_text = ("La aplicacion lee directamente el almacen de certificados de "
                 "Windows (certmgr). No necesita importar ni configurar "
                 "certificados adicionales. Si ya tienes instalado tu certificado "
                 "FNMT, DNIe u otro, la app lo detecta automaticamente.")
    y = draw_body_text(c, cert_text, y)


def page_prerequisites(c: canvas.Canvas, page_num: int, total: int):
    """Pagina 3: Requisitos previos."""
    draw_header_bar(c, "REQUISITOS PREVIOS", page_num, total)
    draw_footer(c)

    y = PAGE_H - 22 * mm - 8 * mm
    y = draw_section_title(c, "Sistema operativo", y)
    y -= 2 * mm

    reqs = [
        "Windows 10 (64 bits) — version 1903 o superior.",
        "Windows 11 (64 bits) — cualquier version.",
    ]
    for r in reqs:
        y = draw_bullet(c, r, y)
    y -= 6 * mm

    y = draw_section_title(c, "Certificado digital instalado en Windows", y)
    y -= 2 * mm

    cert_intro = ("Necesitas al menos un certificado digital valido instalado en "
                  "el almacen personal de Windows. Los mas comunes son:")
    y = draw_body_text(c, cert_intro, y)
    y -= 2 * mm

    certs = [
        "FNMT-RCM (Fabrica Nacional de Moneda y Timbre) — el mas usado en Espana.",
        "DNIe (DNI electronico) — requiere lector de tarjetas.",
        "ACCV (Autoritat de Certificacio de la Comunitat Valenciana).",
        "Camerfirma, ANCERT, ANF, IZENPE y otras CAs reconocidas.",
    ]
    for cert in certs:
        y = draw_bullet(c, cert, y)
    y -= 6 * mm

    y = draw_section_title(c, "Como comprobar si tienes un certificado", y)
    y -= 3 * mm

    steps = [
        "Pulsa Win + R en el teclado.",
        'Escribe certmgr.msc y pulsa Enter.',
        "En el panel izquierdo, ve a: Personal > Certificados.",
        "Si aparece al menos un certificado en la lista, estas listo.",
        "El certificado debe tener clave privada (icono de llave amarilla).",
    ]
    for i, s in enumerate(steps, 1):
        y = draw_step_box(c, i, s, y)
    y -= 6 * mm

    y = draw_section_title(c, "Si no tienes certificado", y)
    y -= 2 * mm

    y = draw_info_box(c, "Obtener certificado FNMT (gratuito)", [
        "1. Visita: www.sede.fnmt.gob.es",
        "2. Seccion: Certificados > Persona Fisica.",
        "3. Solicita el certificado con tu NIF.",
        "4. Acreditate presencialmente en una oficina de la AEAT.",
        "5. Descarga e instala el certificado desde la misma web.",
        "6. Tiempo estimado: 1-3 dias habiles.",
    ], y, bg_color=colors.HexColor("#FFFDE7"))


def page_how_to_use(c: canvas.Canvas, page_num: int, total: int):
    """Pagina 4: Como usar paso a paso."""
    draw_header_bar(c, "COMO USAR — PASO A PASO", page_num, total)
    draw_footer(c)

    y = PAGE_H - 22 * mm - 8 * mm
    y = draw_section_title(c, "Proceso completo de firma", y)
    y -= 4 * mm

    steps = [
        ("1", "Doble clic sobre ArtesBuho-FirmaDigital.exe"),
        ("2", "El navegador se abre automaticamente en localhost:3000"),
        ("3", "Arrastra el PDF al area indicada, o haz clic para seleccionarlo"),
        ("4", "Comprueba que el documento es el correcto (vista previa disponible)"),
        ("5", 'Haz clic en "Firmar con certificado digital"'),
        ("6", "Windows muestra el selector de certificados — elige el tuyo"),
        ("7", "Introduce el PIN de tu certificado si te lo solicita"),
        ("8", "Espera el proceso de firma (normalmente menos de 5 segundos)"),
        ("9", 'Haz clic en "Descargar PDF firmado"'),
    ]

    for num, text in steps:
        y = draw_step_box(c, int(num), text, y)
        y -= 1 * mm

    y -= 4 * mm
    y = draw_section_title(c, "Notas importantes", y)
    y -= 2 * mm

    notes = [
        "El PDF firmado es un archivo nuevo — el original no se modifica.",
        "El tamano maximo de PDF permitido es 15 MB.",
        "No cierres la ventana del exe mientras firmas.",
        "La aplicacion puede estar minimizada en la bandeja del sistema.",
        "Puedes firmar varios PDFs en la misma sesion sin reiniciar.",
    ]
    for n in notes:
        y = draw_bullet(c, n, y)


def page_signed_pdf(c: canvas.Canvas, page_num: int, total: int):
    """Pagina 5: Que contiene el PDF firmado."""
    draw_header_bar(c, "QUE CONTIENE EL PDF FIRMADO", page_num, total)
    draw_footer(c)

    y = PAGE_H - 22 * mm - 8 * mm
    y = draw_section_title(c, "Sello visible en el documento", y)
    y -= 2 * mm

    sello_desc = ("En la ultima pagina del PDF firmado aparece un sello visible "
                  "con toda la informacion de la firma. Este sello es parte del "
                  "documento y no puede eliminarse sin invalidar la firma.")
    y = draw_body_text(c, sello_desc, y)
    y -= 3 * mm

    sello_fields = [
        "Nombre del firmante (extraido del certificado).",
        "Entidad emisora del certificado (FNMT, ACCV, etc.).",
        "Fecha y hora exacta de la firma (en hora local de Madrid).",
        "Numero de serie del certificado.",
        "Estado de validez en el momento de la firma.",
    ]
    for f in sello_fields:
        y = draw_bullet(c, f, y)
    y -= 6 * mm

    y = draw_section_title(c, "Firma embebida en metadatos", y)
    y -= 2 * mm

    meta_desc = ("Ademas del sello visible, el PDF contiene una firma digital "
                 "criptografica incrustada en sus metadatos en formato PAdES. "
                 "Esta firma garantiza la integridad del documento: cualquier "
                 "modificacion posterior la invalida automaticamente.")
    y = draw_body_text(c, meta_desc, y)
    y -= 6 * mm

    y = draw_section_title(c, "Como verificar la firma", y)
    y -= 2 * mm

    verif = [
        "Adobe Acrobat Reader: panel 'Firmas' en la barra lateral.",
        "Adobe Acrobat Pro: herramienta 'Validar todas las firmas'.",
        "Validador eIDAS: servicio online de la Comision Europea.",
        "Autofirma (MINHAP): aplicacion gratuita del Gobierno de Espana.",
        "DSS Demonstration WebApp (EC): validador PAdES en linea.",
    ]
    for v in verif:
        y = draw_bullet(c, v, y)
    y -= 6 * mm

    y = draw_info_box(c, "Que garantiza la firma PAdES", [
        "  Autenticidad: el documento fue firmado por el titular del certificado.",
        "  Integridad: el contenido no ha sido modificado tras la firma.",
        "  No repudio: el firmante no puede negar haber firmado el documento.",
        "  Validez legal: reconocida en todos los paises de la Union Europea.",
    ], y, bg_color=colors.HexColor("#F1F8E9"), border_color=colors.HexColor("#AED581"))


def page_history_status(c: canvas.Canvas, page_num: int, total: int):
    """Pagina 6: Historial y Estado."""
    draw_header_bar(c, "HISTORIAL Y ESTADO", page_num, total)
    draw_footer(c)

    y = PAGE_H - 22 * mm - 8 * mm
    y = draw_section_title(c, "Pestana Historial", y)
    y -= 2 * mm

    hist_desc = ("La pestana Historial registra todos los documentos firmados "
                 "durante la sesion actual. Cada entrada muestra el nombre del "
                 "archivo, la fecha/hora de firma y el certificado utilizado.")
    y = draw_body_text(c, hist_desc, y)
    y -= 3 * mm

    hist_items = [
        "Nombre del archivo PDF firmado.",
        "Timestamp de la firma (fecha y hora local).",
        "Certificado usado (nombre del firmante e issuer).",
        "Enlace de descarga directa del PDF firmado.",
        "El historial se borra al cerrar la aplicacion.",
    ]
    for h in hist_items:
        y = draw_bullet(c, h, y)
    y -= 6 * mm

    y = draw_section_title(c, "Pestana Estado", y)
    y -= 2 * mm

    status_desc = ("La pestana Estado muestra informacion en tiempo real sobre "
                   "el motor de firma y los certificados disponibles en el sistema.")
    y = draw_body_text(c, status_desc, y)
    y -= 3 * mm

    status_items = [
        "Version del motor de firma activo.",
        "Lista de certificados detectados en el almacen de Windows.",
        "Fecha de caducidad de cada certificado.",
        "Estado de la conexion con el almacen PKCS#11 (si aplica).",
    ]
    for s in status_items:
        y = draw_bullet(c, s, y)
    y -= 6 * mm

    y = draw_section_title(c, "Indicador de estado en la barra lateral", y)
    y -= 3 * mm

    # Cuadro verde — certificado detectado
    c.setFillColor(colors.HexColor("#E8F5E9"))
    c.setStrokeColor(colors.HexColor("#66BB6A"))
    c.roundRect(MARGIN_L, y - 10 * mm, CONTENT_W, 10 * mm, 3, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#2E7D32"))
    c.circle(MARGIN_L + 8 * mm, y - 5 * mm, 4, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1B5E20"))
    c.drawString(MARGIN_L + 14 * mm, y - 6 * mm,
                 "Punto VERDE — Certificado detectado. Listo para firmar.")
    y -= 13 * mm

    # Cuadro rojo — sin certificado
    c.setFillColor(colors.HexColor("#FFEBEE"))
    c.setStrokeColor(colors.HexColor("#EF5350"))
    c.roundRect(MARGIN_L, y - 10 * mm, CONTENT_W, 10 * mm, 3, fill=1, stroke=1)
    c.setFillColor(COLOR_RED)
    c.circle(MARGIN_L + 8 * mm, y - 5 * mm, 4, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#B71C1C"))
    c.drawString(MARGIN_L + 14 * mm, y - 6 * mm,
                 "Punto ROJO — No hay certificados disponibles en el sistema.")
    y -= 13 * mm

    y -= 4 * mm
    y = draw_info_box(c, "Consejo", [
        "Mantener la pestana Estado visible durante la primera instalacion",
        "ayuda a confirmar que Windows ha reconocido correctamente",
        "el certificado antes de intentar firmar documentos.",
    ], y, bg_color=colors.HexColor("#FFFDE7"))


def page_troubleshooting(c: canvas.Canvas, page_num: int, total: int):
    """Pagina 7: Solucion de problemas."""
    draw_header_bar(c, "SOLUCION DE PROBLEMAS", page_num, total)
    draw_footer(c)

    y = PAGE_H - 22 * mm - 8 * mm
    y = draw_section_title(c, "Tabla de errores frecuentes", y)
    y -= 3 * mm

    # Cabecera de tabla
    c.setFillColor(COLOR_RED)
    c.rect(MARGIN_L, y - 8 * mm, CONTENT_W, 8 * mm, fill=1, stroke=0)
    c.setFillColor(COLOR_WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN_L + 3, y - 5.5 * mm, "MENSAJE DE ERROR")
    c.drawString(MARGIN_L + CONTENT_W * 0.42 + 4, y - 5.5 * mm, "SOLUCION")
    y -= 8 * mm

    rows = [
        ("No hay certificados", "Instala un certificado en certmgr.msc > Personal"),
        ("Puerto 3000 en uso", "Cierra otra instancia de la app y vuelve a abrir"),
        ("Tiempo de espera agotado", "El selector de Windows puede estar detras de otras ventanas"),
        ("PDF corrupto o invalido", "Prueba con otro PDF. El archivo puede estar danado"),
        ("Antivirus bloquea el exe", "Agrega excepcion en tu antivirus para ArtesBuho-FirmaDigital.exe"),
        ("PIN incorrecto", "Verifica el PIN de tu certificado. 3 intentos fallidos lo bloquea"),
        ("Certificado caducado", "Renueva o solicita un nuevo certificado en la CA correspondiente"),
    ]
    for i, (prob, sol) in enumerate(rows):
        y = draw_troubleshoot_row(c, prob, sol, y, alt=(i % 2 == 0))

    y -= 6 * mm
    y = draw_section_title(c, "Pasos de diagnostico general", y)
    y -= 2 * mm

    diag = [
        "Cierra la aplicacion completamente (clic derecho en bandeja > Salir).",
        "Vuelve a abrir el exe como Administrador (clic derecho > Ejecutar como administrador).",
        "Comprueba en certmgr.msc que el certificado tiene clave privada (icono llave).",
        "Desactiva temporalmente el antivirus para descartar bloqueos.",
        "Si el problema persiste, contacta en booking@artesbuhomanagement.com.",
    ]
    for d in diag:
        y = draw_bullet(c, d, y)


def page_technical(c: canvas.Canvas, page_num: int, total: int):
    """Pagina 8: Informacion tecnica y cierre."""
    draw_header_bar(c, "INFORMACION TECNICA", page_num, total)
    draw_footer(c)

    y = PAGE_H - 22 * mm - 8 * mm
    y = draw_section_title(c, "Especificaciones tecnicas", y)
    y -= 3 * mm

    specs = [
        ("Formato de firma", "PAdES (PDF Advanced Electronic Signatures)"),
        ("Algoritmo de hash", "SHA-256"),
        ("Algoritmo de cifrado", "RSA (segun el certificado del usuario)"),
        ("Estructura de firma", "CMS / PKCS#7 embebido en PDF"),
        ("Nivel de conformidad", "PAdES-B-B (baseline, eIDAS compatible)"),
        ("Tamano maximo de PDF", "15 MB por documento"),
        ("Puerto de escucha", "localhost:3000 (solo local, sin acceso red)"),
        ("Almacen de certificados", "Windows Certificate Store (CAPI / CNG)"),
    ]

    row_h = 8 * mm
    for i, (key, val) in enumerate(specs):
        bg = COLOR_LIGHT if i % 2 == 0 else COLOR_WHITE
        c.setFillColor(bg)
        c.rect(MARGIN_L, y - row_h, CONTENT_W, row_h, fill=1, stroke=0)
        c.setFillColor(COLOR_RED)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN_L + 3, y - 5.5 * mm, key)
        c.setFillColor(COLOR_DARK)
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN_L + CONTENT_W * 0.40, y - 5.5 * mm, val)
        y -= row_h

    y -= 6 * mm
    y = draw_section_title(c, "Privacidad y seguridad", y)
    y -= 2 * mm

    priv = [
        "Los documentos se procesan exclusivamente en tu equipo local.",
        "Ningun archivo se envia a servidores externos.",
        "La clave privada de tu certificado nunca abandona Windows.",
        "La aplicacion no guarda datos personales entre sesiones.",
    ]
    for p in priv:
        y = draw_bullet(c, p, y)
    y -= 6 * mm

    y = draw_section_title(c, "Contacto y soporte", y)
    y -= 3 * mm

    # Bloque de contacto con borde amarillo
    c.setFillColor(COLOR_YELLOW)
    c.roundRect(MARGIN_L, y - 22 * mm, CONTENT_W, 22 * mm, 5, fill=1, stroke=0)
    c.setFillColor(COLOR_DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, y - 7 * mm, "ARTES BUHO MANAGEMENT")
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W / 2, y - 12 * mm, "booking@artesbuhomanagement.com")
    c.setFont("Helvetica", 9)
    c.setFillColor(COLOR_GRAY)
    c.drawCentredString(PAGE_W / 2, y - 17 * mm,
                        "Desarrollado por RUBEN COTON  |  Abril 2026")
    y -= 25 * mm

    # Copyright final
    c.setFillColor(COLOR_RED)
    c.roundRect(MARGIN_L, y - 10 * mm, CONTENT_W, 10 * mm, 4, fill=1, stroke=0)
    c.setFillColor(COLOR_WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(PAGE_W / 2, y - 6.5 * mm,
                        u"\u00a9 2026 ARTES BUHO MANAGEMENT \u2014 Desarrollado por RUBEN COTON")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate():
    TOTAL_PAGES = 8

    c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
    c.setTitle("FIRMA DIGITAL - Manual de Uso - ARTES BUHO MANAGEMENT")
    c.setAuthor("RUBEN COTON")
    c.setSubject("Manual de usuario de la aplicacion ARTES BUHO Firma Digital")
    c.setCreator("ARTES BUHO MANAGEMENT - generate-manual.py")

    # --- Pagina 1: Portada ---
    page_cover(c)
    c.showPage()

    # --- Pagina 2: Que es ---
    page_what_is(c, 2, TOTAL_PAGES)
    c.showPage()

    # --- Pagina 3: Requisitos ---
    page_prerequisites(c, 3, TOTAL_PAGES)
    c.showPage()

    # --- Pagina 4: Como usar ---
    page_how_to_use(c, 4, TOTAL_PAGES)
    c.showPage()

    # --- Pagina 5: PDF firmado ---
    page_signed_pdf(c, 5, TOTAL_PAGES)
    c.showPage()

    # --- Pagina 6: Historial y Estado ---
    page_history_status(c, 6, TOTAL_PAGES)
    c.showPage()

    # --- Pagina 7: Troubleshooting ---
    page_troubleshooting(c, 7, TOTAL_PAGES)
    c.showPage()

    # --- Pagina 8: Tecnico ---
    page_technical(c, 8, TOTAL_PAGES)
    c.showPage()

    c.save()
    print(f"Manual generado correctamente en:\n  {OUTPUT_PATH}")


if __name__ == "__main__":
    generate()
