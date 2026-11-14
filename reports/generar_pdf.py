"""Genera el PDF «Qué coche buscar en Alemania y a qué precio».

Uso: python3 reports/generar_pdf.py   (requiere reportlab; imágenes en reports/assets/)
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "Importación coches Alemania a Marbella.pdf")
FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("B", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("BB", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("B", normal="B", bold="BB", italic="B", boldItalic="BB")

NAVY = colors.HexColor("#12263f"); BLUE = colors.HexColor("#0b5cad"); GREY = colors.HexColor("#5b6470")
LIGHT = colors.HexColor("#f2f5f8"); LINE = colors.HexColor("#cfd6de")
G_BG = colors.HexColor("#dff3e6"); G_TX = "#17693f"
A_BG = colors.HexColor("#fff1cc"); A_TX = "#8a5a00"
R_BG = colors.HexColor("#fbe0dc"); R_TX = "#a93226"

P = ParagraphStyle("p", fontName="B", fontSize=10, leading=14.5, textColor=colors.HexColor("#1c2530"))
SMALL = ParagraphStyle("s", parent=P, fontSize=7.8, leading=10.6, textColor=GREY)
H1 = ParagraphStyle("h1", parent=P, fontName="BB", fontSize=18, leading=22, textColor=NAVY, spaceAfter=4)
SUB = ParagraphStyle("sub", parent=P, textColor=GREY, spaceAfter=8)
H2 = ParagraphStyle("h2", parent=P, fontName="BB", fontSize=12, leading=15, textColor=BLUE, spaceBefore=10, spaceAfter=5)
CELL = ParagraphStyle("c", parent=P, fontSize=8.8, leading=11.6)
CELLH = ParagraphStyle("ch", parent=CELL, fontName="BB", textColor=colors.white)
BUL = ParagraphStyle("b", parent=P, leftIndent=11, firstLineIndent=-11, spaceAfter=3.5)


def eur(x, sign=False):
    s = f"{abs(x):,.0f}".replace(",", ".")
    return (f"−{s} €" if x < 0 else ("+" if sign else "") + s + " €")


def pct(x, d=0):
    return f"{x:.{d}f}".replace(".", ",") + " %"


def tbl(rows, widths, head=True, zebra=True, pad=3.6, extra=()):
    data = [[(Paragraph(c, CELLH if (head and i == 0) else CELL) if isinstance(c, str) else c) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
          ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]
    if head:
        st.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        st += [("BACKGROUND", (0, i), (-1, i), LIGHT) for i in range(2, len(rows), 2)]
    t.setStyle(TableStyle(st + list(extra)))
    return t


def box(text, bg=A_BG, border=colors.HexColor("#e2c46b"), w=17 * cm, style=None):
    t = Table([[Paragraph(text, style or ParagraphStyle("n", parent=P, fontSize=9.2, leading=13))]], colWidths=[w])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.7, border),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def bullets(items):
    return [Paragraph("• " + x, BUL) for x in items]


# ------------------------------------------------------------ datos y cálculo
KM = {"Alemania": 244, "Francia": 861, "España": 1164}
PRECIO = {"diésel": {"Alemania": 2.22, "Francia": 2.22, "España": 1.864},
          "gasolina": {"Alemania": 1.978, "Francia": 2.04, "España": 1.668}}
VIAJE_FIJO = [("Vuelo Málaga → Stuttgart", 110), ("Traslados", 60), ("Hotel en Alemania (1 noche)", 115),
              ("Hoteles en ruta (2 noches)", 160), ("Dietas (4 días)", 180), ("Inspección del coche", 100),
              ("Placas de exportación y seguro", 180), ("Peajes", 96), ("Varios", 30)]
ESPANA = 1250          # matriculación 600 + garantía 350 + preparación 300
OBJ = 3000             # beneficio objetivo por coche
VERDE, AMBAR = 3000, 1500

VEH = [
    dict(key="gle", n="1", nombre="Mercedes-Benz GLE 350 de 4MATIC", corto="GLE 350 de", anos="2020–2021",
         tipo="SUV híbrido enchufable diésel (V167)", img="gle_350de.jpg",
         cred="Foto: Charles (Port Chester, NY), CC BY 2.0, Wikimedia Commons (recortada).",
         fuel="diésel", l100=7.5, media_de=50125, media_es=55176, iedmt=0,
         porque="Paga 0 % de impuesto de matriculación y lleva etiqueta CERO. Es el dato de precios más sólido del estudio.",
         precios=[51000, 50000, 49000, 48000, 47000, 46000, 45000, 44000],
         ficha=[("Motor", "2.0 diésel 194 CV + eléctrico 136 CV = 320 CV"), ("Cambio / tracción", "Automático 9G-TRONIC, 4MATIC"),
                ("Batería", "31,2 kWh, unos 90–100 km eléctricos"), ("CO2", "≈ 20–30 g/km → impuesto 0 %"), ("Etiqueta DGT", "CERO")],
         buscar=[("Escribir en el buscador", "«GLE 350 de 4MATIC» — con la <b>e</b> final. El «350 d» sin e no es enchufable y paga impuesto."),
                 ("Año y kilómetros", "2020–2021, entre 80.000 y 120.000 km"),
                 ("Vendedor", "Particular, o concesionario con «§25a / differenzbesteuert»"),
                 ("Extras que se venden bien", "AMG Line, techo panorámico, doble pantalla, cámara 360°, Burmester"),
                 ("Comprobar", "Estado de la batería, cables de carga, historial Mercedes, sin accidentes, 2 llaves")]),
    dict(key="v", n="2", nombre="Mercedes-Benz V 300 d", corto="V 300 d", anos="2020–2021",
         tipo="Monovolumen diésel de 6–8 plazas (W447)", img="v_300d.jpg",
         cred="Foto: Charles (Port Chester, NY), CC BY 2.0, Wikimedia Commons (recortada).",
         fuel="diésel", l100=8.5, media_de=49564, media_es=57226, iedmt=2282,
         porque="Tiene la mayor diferencia de precio entre Alemania y España, pero paga impuesto de matriculación: solo vale si el CO2 es inferior a 200 g/km.",
         precios=[50000, 49000, 48000, 47000, 46000, 45000, 44000, 43000],
         ficha=[("Motor", "2.0 diésel de 239 CV y 500 Nm"), ("Cambio / tracción", "Automático 9G-TRONIC; trasera o 4MATIC"),
                ("Carrocería", "Larga (5,14 m) es la más demandada"), ("CO2", "≈ 190–228 g/km → impuesto 9,75 % o 14,75 %"), ("Etiqueta DGT", "C")],
         buscar=[("Escribir en el buscador", "«V 300 d» Avantgarde, Exclusive o AMG Line, carrocería «lang»"),
                 ("Año y kilómetros", "2020–2021, entre 80.000 y 110.000 km"),
                 ("Vendedor", "§25a o particular. Si el cliente final es una empresa, mejor con «MwSt. ausweisbar»"),
                 ("Extras que se venden bien", "7 plazas en cuero, puertas eléctricas, techo panorámico, mesa central"),
                 ("Comprobar", "<b>CO2 inferior a 200 g/km en el certificado de conformidad</b>; que no haya sido taxi ni alquiler")]),
    dict(key="cay", n="3", nombre="Porsche Cayenne E-Hybrid", corto="Cayenne E-Hybrid", anos="2018–2019",
         tipo="SUV híbrido enchufable gasolina (9YA)", img="cayenne_ehybrid.jpg",
         cred="Foto: Alexandre Prevot, CC BY-SA 2.0, Wikimedia Commons.",
         fuel="gasolina", l100=10.5, media_de=57100, media_es=59513, iedmt=0,
         porque="Paga 0 % de impuesto y es la marca que más se mueve en Marbella, pero la diferencia de precio media es pequeña: exige el mayor descuento.",
         precios=[57000, 55000, 54000, 53000, 52000, 51000, 50000, 49000],
         ficha=[("Motor", "3.0 V6 gasolina 340 CV + eléctrico 136 CV = 462 CV"), ("Cambio / tracción", "Tiptronic S de 8 marchas, total"),
                ("Batería", "14,1 kWh, unos 40 km eléctricos"), ("CO2", "56–58 g/km → impuesto 0 %"), ("Etiqueta DGT", "CERO")],
         buscar=[("Escribir en el buscador", "«Cayenne E-Hybrid» (no Coupé ni Turbo S E-Hybrid: se salen de precio)"),
                 ("Año y kilómetros", "2018–2019, entre 80.000 y 110.000 km"),
                 ("Vendedor", "Particular o §25a; mejor con garantía Porsche Approved"),
                 ("Extras que se venden bien", "Sport Chrono, suspensión neumática, techo panorámico, llantas de 21\""),
                 ("Comprobar", "Estado de la batería, historial Porsche, neumáticos y frenos (caros), sin accidentes")]),
]


def beneficio(v, compra, venta):
    margen = venta - compra
    return margen - max(margen, 0) * 21 / 121 - v["costes"]


for v in VEH:
    v["fuel_eur"] = sum(KM[p] * v["l100"] / 100 * PRECIO[v["fuel"]][p] for p in KM)
    v["viaje"] = sum(x for _, x in VIAJE_FIJO) + v["fuel_eur"]
    v["costes"] = v["viaje"] + ESPANA + v["iedmt"]
    v["venta_pru"] = v["media_es"] * 0.97
    v["max"] = int((v["venta_pru"] - (OBJ + v["costes"]) * 1.21) // 100 * 100)   # precio máximo de compra
    v["desc"] = (1 - v["max"] / v["media_de"]) * 100


def veredicto(b):
    if b >= VERDE:
        return "Comprar", G_BG, G_TX
    if b >= AMBAR:
        return "Solo si la unidad es muy buena", A_BG, A_TX
    return "No comprar", R_BG, R_TX


def semaforo(v):
    rows = [["Si lo compras por…", "Respecto a la media alemana", "Ganas vendiendo a precio medio", "Ganas vendiendo un 3 % más barato", "Decisión"]]
    extra = []
    for i, c in enumerate(v["precios"], start=1):
        b1, b2 = beneficio(v, c, v["media_es"]), beneficio(v, c, v["venta_pru"])
        txt, bg, tx = veredicto(b2)
        d = (c / v["media_de"] - 1) * 100
        rows.append([f"<b>{eur(c)}</b>", ("media" if abs(d) < 0.6 else pct(d).replace("-", "−")), eur(b1, True),
                     f"<font color='{tx}'><b>{eur(b2, True)}</b></font>", f"<font color='{tx}'><b>{txt}</b></font>"])
        extra += [("BACKGROUND", (3, i), (4, i), bg)]
    return tbl(rows, [3.0 * cm, 3.0 * cm, 3.3 * cm, 3.5 * cm, 4.2 * cm], zebra=False, pad=2.8, extra=extra)


# ------------------------------------------------------------ documento
W, Hh = A4


def on_page(c, d):
    c.saveState(); c.setFont("B", 7.5); c.setFillColor(GREY)
    c.drawString(2 * cm, 1.1 * cm, "Qué coche buscar en Alemania y a qué precio · Importación a Marbella · Noviembre de 2026")
    c.drawRightString(W - 2 * cm, 1.1 * cm, f"Página {d.page}")
    c.setStrokeColor(LINE); c.line(2 * cm, 1.45 * cm, W - 2 * cm, 1.45 * cm); c.restoreState()


def cover(c, d):
    c.saveState(); c.setFillColor(NAVY); c.rect(0, Hh - 6.6 * cm, W, 6.6 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("BB", 24)
    c.drawString(2 * cm, Hh - 2.9 * cm, "Qué coche buscar en Alemania")
    c.drawString(2 * cm, Hh - 4.0 * cm, "y a qué precio")
    c.setFont("B", 11.5); c.setFillColor(colors.HexColor("#c9d6e6"))
    c.drawString(2 * cm, Hh - 5.2 * cm, "Guía de compra para importar a Marbella con beneficio · Noviembre de 2026")
    c.restoreState(); on_page(c, d)


doc = BaseDocTemplate(OUT, pagesize=A4, title="Qué coche buscar en Alemania y a qué precio", author="Estudio de mercado")
doc.addPageTemplates([
    PageTemplate(id="cover", frames=[Frame(2 * cm, 1.9 * cm, 17 * cm, Hh - 6.6 * cm - 2.4 * cm, leftPadding=0, rightPadding=0)], onPage=cover),
    PageTemplate(id="body", frames=[Frame(2 * cm, 1.9 * cm, 17 * cm, Hh - 3.6 * cm, leftPadding=0, rightPadding=0)], onPage=on_page)])
S = [NextPageTemplate("body")]

# ---- 1. La respuesta
S.append(Paragraph("La respuesta en una página", H2))
S.append(Paragraph(
    "A precio medio de mercado <b>no interesa</b>: el mejor coche deja unos 1.500 € sobre 53.000 € invertidos. "
    f"<b>Sí interesa si se compra por debajo de un precio máximo.</b> Ese precio está calculado para ganar al menos {eur(OBJ)} "
    "limpios por coche aunque luego haya que venderlo un 3 % más barato que la media española.", P))
S.append(Spacer(1, 8))
BIG = ParagraphStyle("big", parent=P, fontName="BB", fontSize=17, leading=20, textColor=colors.HexColor(G_TX), alignment=1)
CT = ParagraphStyle("ct", parent=P, fontName="BB", fontSize=10, leading=12.5, alignment=1, textColor=NAVY)
CS = ParagraphStyle("cs", parent=SMALL, alignment=1, fontSize=8.2, leading=11)
cards = []
for v in VEH:
    cards.append([Image(os.path.join(A, v["img"]), width=5.2 * cm, height=3.47 * cm),
                  Paragraph(f"{v['n']}.º {v['corto']}", CT), Paragraph(f"{v['anos']} · {v['tipo'].split(' (')[0]}", CS),
                  Paragraph("Precio máximo de compra", CS), Paragraph(eur(v["max"]), BIG),
                  Paragraph(f"Media en Alemania: {eur(v['media_de'])}<br/><b>Hay que comprar un {pct(v['desc'])} más barato</b>", CS)])
t = Table(list(map(list, zip(*cards))), colWidths=[5.66 * cm] * 3)
t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                       ("BOX", (0, 0), (0, -1), 0.7, LINE), ("BOX", (1, 0), (1, -1), 0.7, LINE), ("BOX", (2, 0), (2, -1), 0.7, LINE),
                       ("BACKGROUND", (0, 3), (-1, 5), LIGHT), ("TOPPADDING", (0, 0), (-1, 0), 7),
                       ("TOPPADDING", (0, 1), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -2), 3), ("BOTTOMPADDING", (0, -1), (-1, -1), 8)]))
S.append(t)
S.append(Spacer(1, 10))
S.append(box(
    "<b>En qué centrarse:</b> el <b>GLE 350 de</b> es el objetivo principal (el que menos descuento exige y no paga impuesto de matriculación). "
    "La <b>Clase V</b> es la segunda opción, solo con CO2 inferior a 200 g/km. El <b>Cayenne</b> solo si aparece una unidad un 11 % por debajo de la media.",
    bg=G_BG, border=colors.HexColor("#9ccfb0")))
S.append(Spacer(1, 8))
S.append(box(
    "<b>Aviso sobre las cifras.</b> Los precios medios salen de un agregador de anuncios (AutoUncle), no de anuncios concretos ni de ventas reales, "
    "y los costes son en parte estimados. Los precios máximos de esta guía son un punto de partida: antes de comprar hay que recalcularlos "
    "con el precio real al que se anuncian coches iguales en España."))
S.append(PageBreak())

# ---- 2. La regla
S.append(Paragraph("La regla para decidir en dos minutos", H1))
S.append(Paragraph("Sirve para cualquier anuncio que encuentres, de estos modelos o de otros.", SUB))
S.append(Paragraph("Paso 1 · La cuenta rápida", H2))
F = ParagraphStyle("f", parent=P, fontName="BB", fontSize=12.5, leading=18, alignment=1, textColor=NAVY)
S.append(box("Beneficio ≈ (precio de venta en España − precio de compra en Alemania) × 0,83 − 2.700 €<br/>"
             "<font size=9 color='#5b6470'>y si el coche no es híbrido enchufable, restar además el impuesto de matriculación</font>",
             bg=LIGHT, border=LINE, style=F))
S.append(Spacer(1, 4))
S.append(Paragraph(
    "El 0,83 descuenta el IVA, que se paga solo sobre la diferencia entre compra y venta. Los 2.700 € son los costes fijos por coche: "
    "unos 1.400 € de viaje (avión de ida y vuelta por carretera) y 1.250 € en España (matriculación, garantía y preparación). "
    "<b>Para ganar 3.000 € hace falta una diferencia de precio de unos 6.900 €</b> entre lo que pagas en Alemania y lo que cobras en Marbella.", P))
S.append(Paragraph("Paso 2 · Los cinco filtros (si falla uno, se descarta)", H2))
rows = [["", "Filtro", "Por qué"],
        ["1", "<b>Híbrido enchufable</b> (CO2 inferior a 120 g/km en el certificado de conformidad)", "Paga 0 % de impuesto de matriculación. Un coche de 200 g/km o más paga el 14,75 %, entre 3.000 y 7.000 €."],
        ["2", "<b>Vendedor particular o concesionario con «§25a»</b> (differenzbesteuert)", "Permite pagar el IVA en España solo sobre el margen, no sobre el precio entero."],
        ["3", "<b>Precio igual o inferior al máximo</b> de esta guía", "Por encima, el beneficio no cubre el riesgo de avería ni un mes extra sin vender."],
        ["4", "<b>Historial limpio</b>: sin accidentes, mantenimiento sellado, 1–2 dueños, kilómetros coherentes", "Como vendedor profesional respondes un año por las averías."],
        ["5", "<b>Más de 6 meses y más de 6.000 km</b>", "Si no, Hacienda lo trata como coche nuevo y paga el 21 % de IVA en España."]]
S.append(tbl(rows, [0.9 * cm, 7.9 * cm, 8.2 * cm]))
S.append(Paragraph("Paso 3 · El semáforo", H2))
rows = [["Beneficio previsto en el caso prudente", "Decisión"],
        [f"<font color='{G_TX}'><b>{eur(VERDE)} o más</b></font>", f"<font color='{G_TX}'><b>Comprar</b></font>"],
        [f"<font color='{A_TX}'><b>Entre {eur(AMBAR)} y {eur(VERDE)}</b></font>", f"<font color='{A_TX}'><b>Solo si la unidad es muy buena y fácil de vender</b></font>"],
        [f"<font color='{R_TX}'><b>Menos de {eur(AMBAR)}</b></font>", f"<font color='{R_TX}'><b>No comprar</b></font>"]]
S.append(tbl(rows, [7.0 * cm, 10.0 * cm], zebra=False,
             extra=[("BACKGROUND", (0, 1), (-1, 1), G_BG), ("BACKGROUND", (0, 2), (-1, 2), A_BG), ("BACKGROUND", (0, 3), (-1, 3), R_BG)]))
S.append(Paragraph("«Caso prudente» = vender un 3 % por debajo del precio medio al que se anuncia ese coche en España.", SMALL))
S.append(PageBreak())

# ---- 3. Fichas por vehículo
for v in VEH:
    S.append(Paragraph(f"Objetivo {v['n']} · {v['nombre']}", H1))
    S.append(Paragraph(f"{v['tipo']} · {v['anos']}", SUB))
    img = Image(os.path.join(A, v["img"]), width=7.5 * cm, height=5.0 * cm)
    left = Table([[img], [Paragraph(v["cred"] + " Imagen ilustrativa del modelo.", SMALL)]], colWidths=[7.5 * cm])
    left.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    MAXS = ParagraphStyle("mx", parent=P, alignment=1, fontSize=9, leading=12, textColor=GREY)
    right = Table([[Paragraph("PRECIO MÁXIMO DE COMPRA", MAXS)], [Paragraph(eur(v["max"]), ParagraphStyle("bg", parent=BIG, fontSize=24, leading=28))],
                   [Paragraph(f"un {pct(v['desc'])} por debajo de la media alemana ({eur(v['media_de'])})", MAXS)],
                   [Paragraph(v["porque"], ParagraphStyle("pq", parent=P, fontSize=9.2, leading=12.8))]], colWidths=[8.9 * cm])
    right.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 2), G_BG), ("BOX", (0, 0), (-1, 2), 0.7, colors.HexColor("#9ccfb0")),
                               ("TOPPADDING", (0, 0), (-1, 0), 9), ("BOTTOMPADDING", (0, 2), (-1, 2), 9), ("TOPPADDING", (0, 3), (-1, 3), 9),
                               ("LEFTPADDING", (0, 3), (-1, 3), 2)]))
    top = Table([[left, right]], colWidths=[8.0 * cm, 9.0 * cm])
    top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    S.append(top)
    S.append(Paragraph("Cuánto se gana según el precio de compra", H2))
    S.append(semaforo(v))
    S.append(Paragraph(
        f"Venta a precio medio: {eur(v['media_es'])}. Venta un 3 % más barata: {eur(v['venta_pru'])}. Costes descontados: viaje {eur(v['viaje'])}, "
        f"España {eur(ESPANA)}" + (f", impuesto de matriculación {eur(v['iedmt'])} (tramo del 9,75 %; con 200 g/km o más son unos 1.200 € adicionales)" if v["iedmt"] else ", impuesto de matriculación 0 €")
        + " e IVA sobre el margen. Antes del impuesto sobre el beneficio.", SMALL))
    S.append(Paragraph("Qué unidad buscar", H2))
    S.append(tbl([["Referencia", "Criterio"]] + [[a, b] for a, b in v["buscar"]] + [[a, b] for a, b in v["ficha"] if a in ("Motor", "Cambio / tracción", "CO2")], [4.3 * cm, 12.7 * cm], pad=2.4))
    S.append(PageBreak())

# ---- 4. Dónde encontrar unidades baratas
S.append(Paragraph("Dónde aparecen los coches por debajo de mercado", H1))
S.append(Paragraph("Orientación práctica basada en cómo funciona el mercado alemán; no son datos medidos en este estudio.", SUB))
rows = [["Dónde buscar", "Por qué sale más barato", "A tener en cuenta"],
        ["<b>Vendedores particulares</b> (filtro «Privatanbieter» en mobile.de y AutoScout24)", "No tienen margen de concesionario y muchos quieren vender rápido.", "Sin garantía del vendedor: inspección independiente obligatoria. Encaja con el IVA sobre el margen."],
        ["<b>Anuncios con muchos días publicados</b> (más de 60–90 días)", "El concesionario tiene dinero parado y acepta rebajas, sobre todo a fin de mes o de trimestre.", "Preguntar por qué no se ha vendido: color, equipamiento o algún daño."],
        ["<b>Etiquetas de precio de los portales</b> («Sehr guter Preis», «Top-Angebot»)", "El propio portal compara el anuncio con coches iguales.", "Ordenar por precio y desconfiar del más barato de todos: suele haber un motivo."],
        ["<b>Alertas de búsqueda</b> (guardar la búsqueda con precio máximo)", "Las buenas unidades duran horas o pocos días: gana quien llama primero.", "Tener el dinero y el viaje listos para cerrar en 48 horas."],
        ["<b>Coches de leasing y de empresa</b> en concesionarios oficiales", "Llegan en lotes al acabar los contratos y hay que darles salida.", "Suelen venderse con IVA desglosado: conviene sobre todo si el cliente final es una empresa."],
        ["<b>Subastas para profesionales</b> (BCA, Autobid, Auto1)", "Es el canal donde compran los concesionarios, por debajo del precio de anuncio.", "Solo con alta como empresa. Hay comisiones y se compra sin ver el coche: para más adelante."]]
S.append(tbl(rows, [5.3 * cm, 5.6 * cm, 6.1 * cm]))
S.append(Paragraph("Cómo bajar el precio de un anuncio concreto", H2))
S += bullets([
    "<b>Llevar anotados dos o tres anuncios iguales más baratos</b> y enseñarlos.",
    "<b>Usar lo que haya que gastar:</b> neumáticos gastados, revisión o ITV alemana próxima, arañazos, segunda llave que falta. Cada punto vale entre 200 y 1.000 €.",
    "<b>Ofrecer pago inmediato por transferencia</b> y recogida esa misma semana.",
    "<b>Recordar la cuenta:</b> cada 1.000 € de rebaja son unos 830 € más de beneficio."])
S.append(Paragraph("Señales de trampa: descartar el anuncio", H2))
S += bullets([
    "Precio muy por debajo de todos los demás, vendedor que pide una señal antes de enseñar el coche o que solo contesta por correo.",
    "Texto «Unfallwagen», «Unfallschaden» (accidentado), «Bastlerfahrzeug» (para reparar) o «nur Export / nur Gewerbe» (se vende sin ninguna garantía).",
    "Precio anunciado «netto»: es sin IVA, y un particular español acaba pagando un 19 % más.",
    "Sin libro de mantenimiento, sin certificado de conformidad o con kilómetros que no cuadran con las revisiones.",
    "En la Clase V: uso anterior como taxi, alquiler o traslados de aeropuerto."])
S.append(Paragraph("Otros modelos que cumplen los filtros y merece la pena mirar", H2))
S.append(Paragraph(
    "<b>BMW X5 xDrive45e</b> y <b>Mercedes GLC 300 e / 300 de</b>: también son híbridos enchufables con 0 % de impuesto de matriculación. "
    "No hay datos suficientes para ponerles precio máximo; se les aplica la cuenta rápida de la página 2 con anuncios reales.", P))
S.append(PageBreak())

# ---- 5. Viaje
S.append(Paragraph("El viaje: 2.269 km y unos 1.400 € por coche", H1))
S.append(Paragraph("Avión de Málaga a Stuttgart y vuelta por carretera hasta Marbella, una persona.", SUB))
mp = Image(os.path.join(A, "mapa_ruta.png")); mw = 9.6 * cm
mp.drawWidth, mp.drawHeight = mw, mw * mp.imageHeight / mp.imageWidth
rows = [["Partida", "Coste"]] + [[a, eur(b)] for a, b in VIAJE_FIJO] + [["Combustible (GLE 350 de)", eur(VEH[0]["fuel_eur"])],
                                                                      ["<b>Total</b>", f"<b>{eur(VEH[0]['viaje'])}</b>"]]
cost = tbl(rows, [5.0 * cm, 2.0 * cm], pad=3.0, extra=[("BACKGROUND", (0, len(rows) - 1), (-1, len(rows) - 1), colors.HexColor("#e3ecf6"))])
side = Table([[cost], [Paragraph(f"Con la Clase V: {eur(VEH[1]['viaje'])}. Con el Cayenne: {eur(VEH[2]['viaje'])}. "
                                 "Rango posible: de 890 € a 2.440 € según vuelo, hotel y fechas.", SMALL)]], colWidths=[7.0 * cm])
side.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
t = Table([[mp, side]], colWidths=[9.9 * cm, 7.1 * cm])
t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
S.append(t)
S.append(Paragraph("Plan de cuatro días", H2))
rows = [["Día", "Qué se hace", "Km", "Horas", "Noche"],
        ["1", "Vuelo a Stuttgart. Ver el coche, prueba, inspección y negociación.", "—", "—", "Stuttgart"],
        ["2", "Pago, contrato y placas de exportación por la mañana. Salida hacia Lyon.", "621", "6,6", "Lyon"],
        ["3", "Lyon – Montpellier – La Jonquera – Barcelona – Tarragona.", "727", "7,7", "Tarragona"],
        ["4", "Tarragona – Valencia – Murcia – Granada – Málaga – Marbella.", "921", "9,7", "En casa"],
        ["", "<b>Total</b>", "<b>2.269</b>", "<b>24,0</b>", "3 noches"]]
S.append(tbl(rows, [1.1 * cm, 10.2 * cm, 1.6 * cm, 1.6 * cm, 2.5 * cm], pad=3.0))
S += [Spacer(1, 5)] + bullets([
    "<b>Repostar al entrar en España</b> (La Jonquera): el litro cuesta unos 0,35 € menos que en Francia.",
    "<b>Dos personas y dos coches en el mismo viaje</b> bajan el coste a unos 1.200 € por coche.",
    "<b>En camión</b> cuesta 900–1.500 € por coche y evita sumarle 2.269 km: conviene en invierno o para el Cayenne.",
    "Desde Fráncfort son 2.332 km, desde Düsseldorf 2.345 km y desde Múnich 2.376 km (con viñetas de Suiza y Austria)."])
S.append(PageBreak())

# ---- 6. Papeles
S.append(Paragraph("Los papeles, en orden", H1))
S.append(Paragraph("Cada paso necesita el documento del anterior. Los detalles se confirman con la gestoría.", SUB))


def fase(titulo, items):
    return KeepTogether([tbl([[titulo, ""]] + [["☐", x] for x in items], [0.8 * cm, 16.2 * cm], zebra=False, pad=2.3,
                             extra=[("SPAN", (0, 0), (1, 0))]), Spacer(1, 5)])


S.append(fase("Antes de la primera compra (una sola vez)", [
    "Alta como autónomo o sociedad con un asesor fiscal (modelo 036, epígrafe 654.1) y elección del régimen de IVA sobre el margen.",
    "Elegir gestoría en Málaga o Marbella con experiencia en importación; preguntar cita y tarifa de la ITV de importación.",
    "Contratar póliza de garantía mecánica y preparar el contrato de venta con un año de garantía por escrito."]))
S.append(fase("Antes de viajar", [
    "Pedir al vendedor: número de bastidor, fotos de la documentación (Teil I y Teil II), última ITV alemana y libro de mantenimiento.",
    "Confirmar que tiene el certificado de conformidad (COC) y leer en él el CO2.",
    "Informe de historial por número de bastidor y comprobación del vendedor (empresa registrada, dirección real).",
    "Régimen de IVA por escrito en la factura proforma. Encargar las placas de exportación."]))
S.append(fase("En Alemania", [
    "Comprobar que el bastidor del coche coincide con los papeles. Prueba de conducción. Dos llaves.",
    "Contrato y factura con bastidor, kilómetros, «unfallfrei» (sin accidentes), precio y régimen de IVA. Pago por transferencia.",
    "Llevarse los originales: Teil I, Teil II, COC, informe de ITV, libro de mantenimiento.",
    "Placas de exportación (banda roja). Las amarillas de 5 días no valen para cruzar Francia."]))
S.append(fase("En España, hasta tener matrícula (2 a 6 semanas)", [
    "ITV de importación → impuesto de matriculación (modelo 576, aunque salga 0 €) → impuesto de circulación → matriculación en la DGT.",
    "Plazo: un mes. Si la ITV se retrasa, placas verdes temporales."]))
S.append(fase("En la venta", [
    "Factura con la mención «Régimen especial de los bienes usados», contrato con la garantía de un año y origen importado declarado.",
    "Cobro por transferencia, cambio de titularidad en 30 días e IVA del margen en la declaración trimestral."]))
S.append(Paragraph("Qué falta por confirmar", H2))
S += bullets([
    "<b>Precios reales:</b> comparar 10–15 anuncios iguales en mobile.de y en coches.net antes de fijar el precio máximo definitivo.",
    "<b>CO2 y valor fiscal</b> de cada unidad, sobre todo en la Clase V (asesor y certificado de conformidad).",
    "<b>Fiscalidad:</b> funcionamiento exacto del IVA sobre el margen y tipo del impuesto de matriculación en Andalucía (asesor fiscal).",
    "<b>Fichas técnicas:</b> son datos de referencia; manda lo que diga la documentación de cada coche."])
S.append(Paragraph(
    "Fuentes: precios medios de AutoUncle.de y AutoUncle.es (2026); ruta de Project OSRM con datos de © colaboradores de OpenStreetMap; combustible de ADAC, "
    "Selectra y prensa española (9–11 de noviembre de 2026); fotografías de Wikimedia Commons con la licencia indicada en cada una.", SMALL))

doc.build(S)
print("OK")
for v in VEH:
    print(v["key"], "max", v["max"], round(v["desc"], 1), "costes", round(v["costes"]), [round(beneficio(v, c, v["venta_pru"])) for c in v["precios"]])
