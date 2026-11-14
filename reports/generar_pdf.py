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
EUR_KM = 0.08          # ajuste por kilometraje: 800 € cada 10.000 km (estimación)
BANDAS = [60000, 80000, 100000, 120000, 140000]
BUENA, MEDIA, MUYBUENA = 0.10, 0.05, 0.15

VEH = [
    dict(key="gle", n="1", nombre="Mercedes-Benz GLE 350 de 4MATIC", corto="GLE 350 de", anos="2020–2021",
         tipo="SUV híbrido enchufable diésel (V167)", img="gle_350de.jpg",
         cred="Foto: Charles (Port Chester, NY), CC BY 2.0, Wikimedia Commons (recortada).",
         fuel="diésel", l100=7.5, iedmt=0, ref=(2021, 100000),
         # año: (media España, km España, media Alemania, km Alemania)
         refs={2021: (55176, 100300, 50125, 99400), 2020: (51286, 118000, 46402, 111300)},
         nota_refs="Medias de 2020 y 2021 con muestras grandes (134 y 55 anuncios en España; 288 y 173 en Alemania).",
         ficha=[("Motor", "2.0 diésel 194 CV + eléctrico 136 CV = 320 CV; automático 9G-TRONIC, 4MATIC"), ("CO2", "≈ 20–30 g/km → impuesto de matriculación 0 %, etiqueta CERO")],
         buscar=[("Escribir en el buscador", "«GLE 350 de 4MATIC» — con la <b>e</b> final. El «350 d» sin e no es enchufable y paga impuesto."),
                 ("Vendedor", "Particular, o concesionario con «§25a / differenzbesteuert»"),
                 ("Extras que se venden bien", "AMG Line, techo panorámico, doble pantalla, cámara 360°, Burmester"),
                 ("Comprobar", "Estado de la batería, cables de carga, historial Mercedes, sin accidentes, 2 llaves")]),
    dict(key="v", n="2", nombre="Mercedes-Benz V 300 d", corto="V 300 d", anos="2020–2021",
         tipo="Monovolumen diésel de 6–8 plazas (W447)", img="v_300d.jpg",
         cred="Foto: Charles (Port Chester, NY), CC BY 2.0, Wikimedia Commons (recortada).",
         fuel="diésel", l100=8.5, iedmt=2282, ref=(2021, 100000),
         refs={2021: (57226, 83700, 49564, 101400), 2020: (52850, 83700, 45184, 105400)},
         nota_refs="2021: media de 32 anuncios en España. 2020: valor prudente estimado a partir de 2021, porque la media española de 2020 sale de solo 10 anuncios. "
                   "Incluye 2.282 € de impuesto de matriculación (tramo del 9,75 %); con 200 g/km o más de CO2, restar unos 1.300 € a cada máximo.",
         ficha=[("Motor", "2.0 diésel de 239 CV y 500 Nm; automático 9G-TRONIC; trasera o 4MATIC"), ("CO2", "≈ 190–228 g/km → impuesto 9,75 % o 14,75 %, etiqueta C")],
         buscar=[("Escribir en el buscador", "«V 300 d» Avantgarde, Exclusive o AMG Line, carrocería «lang» (5,14 m)"),
                 ("Vendedor", "§25a o particular. Si el cliente final es una empresa, mejor con «MwSt. ausweisbar»"),
                 ("Extras que se venden bien", "7 plazas en cuero, puertas eléctricas, techo panorámico, mesa central"),
                 ("Comprobar", "<b>CO2 inferior a 200 g/km en el certificado de conformidad</b>; que no haya sido taxi ni alquiler")]),
    dict(key="cay", n="3", nombre="Porsche Cayenne E-Hybrid", corto="Cayenne E-Hybrid", anos="2019",
         tipo="SUV híbrido enchufable gasolina (9YA)", img="cayenne_ehybrid.jpg",
         cred="Foto: Alexandre Prevot, CC BY-SA 2.0, Wikimedia Commons.",
         fuel="gasolina", l100=10.5, iedmt=0, ref=(2019, 100000),
         refs={2019: (59513, 91000, 57100, 96000)},
         nota_refs="Solo hay datos de ambos países para 2019. Para un 2018, aplicar la fórmula de la página 2 con el precio real de anuncios españoles.",
         ficha=[("Motor", "3.0 V6 gasolina 340 CV + eléctrico 136 CV = 462 CV; Tiptronic S, tracción total"), ("CO2", "56–58 g/km → impuesto de matriculación 0 %, etiqueta CERO")],
         buscar=[("Escribir en el buscador", "«Cayenne E-Hybrid» (no Coupé ni Turbo S E-Hybrid: se salen de precio)"),
                 ("Vendedor", "Particular o §25a; mejor con garantía Porsche Approved"),
                 ("Extras que se venden bien", "Sport Chrono, suspensión neumática, techo panorámico, llantas de 21\""),
                 ("Comprobar", "Estado de la batería, historial Porsche, neumáticos y frenos (caros), sin accidentes")]),
]


def venta(v, ano, km):                      # precio medio de anuncio en España para ese año y km
    pe, ke, _, _ = v["refs"][ano]
    return pe - (km - ke) * EUR_KM


def media_de(v, ano, km):
    _, _, pd_, kd = v["refs"][ano]
    return pd_ - (km - kd) * EUR_KM


def beneficio(v, compra, vta):
    m = vta - compra
    return m - max(m, 0) * 21 / 121 - v["costes"]


def roi(v, compra, vta):
    return beneficio(v, compra, vta) / (compra + v["costes"])


def maximo(v, vta_prudente, r):             # precio máximo de compra para una rentabilidad r
    c = (vta_prudente / 1.21 - v["costes"] * (1 + r)) / (r + 1 / 1.21)
    return int(c // 100 * 100)


for v in VEH:
    v["fuel_eur"] = sum(KM[p] * v["l100"] / 100 * PRECIO[v["fuel"]][p] for p in KM)
    v["viaje"] = sum(x for _, x in VIAJE_FIJO) + v["fuel_eur"]
    v["costes"] = v["viaje"] + ESPANA + v["iedmt"]
    a, k = v["ref"]
    v["vta_ref"] = venta(v, a, k); v["vta_pru"] = v["vta_ref"] * 0.97
    v["de_ref"] = media_de(v, a, k)
    v["max10"] = maximo(v, v["vta_pru"], BUENA); v["max5"] = maximo(v, v["vta_pru"], MEDIA); v["max15"] = maximo(v, v["vta_pru"], MUYBUENA)
    v["desc10"] = (1 - v["max10"] / v["de_ref"]) * 100


def nivel(r):
    if r >= BUENA:
        return ("Buena" if r < MUYBUENA else "Muy buena"), G_BG, G_TX
    if r >= MEDIA:
        return "Media", A_BG, A_TX
    return "Mala", R_BG, R_TX


def tabla_maximos(v):
    rows = [["Año", "Kilómetros", "Venta realista en España", "Máximo para<br/>rentabilidad 15 %", "MÁXIMO para<br/>rentabilidad 10 %", "Máximo para<br/>rentabilidad 5 %", "Media en Alemania"]]
    extra = [("BACKGROUND", (4, 0), (4, 0), colors.HexColor(G_TX))]
    i = 1
    for ano in sorted(v["refs"], reverse=True):
        for km in BANDAS:
            vp = venta(v, ano, km) * 0.97
            rows.append([f"<b>{ano}</b>", f"{km:,} km".replace(",", "."), eur(round(vp, -2)), eur(maximo(v, vp, MUYBUENA)),
                         f"<font color='{G_TX}'><b>{eur(maximo(v, vp, BUENA))}</b></font>", eur(maximo(v, vp, MEDIA)), eur(round(media_de(v, ano, km), -2))])
            extra.append(("BACKGROUND", (4, i), (4, i), G_BG)); i += 1
    return tbl(rows, [1.4 * cm, 2.4 * cm, 2.9 * cm, 2.7 * cm, 2.8 * cm, 2.6 * cm, 2.2 * cm], pad=2.6, extra=extra)


# ------------------------------------------------------------ documento
W, Hh = A4


def on_page(c, d):
    c.saveState(); c.setFont("B", 7.5); c.setFillColor(GREY)
    c.drawString(2 * cm, 1.1 * cm, "Qué coche buscar en Alemania y a qué precio · Importación a Marbella · Noviembre de 2026")
    c.drawRightString(W - 2 * cm, 1.1 * cm, f"Página {d.page}")
    c.setStrokeColor(LINE); c.line(2 * cm, 1.45 * cm, W - 2 * cm, 1.45 * cm); c.restoreState()


def cover(c, d):
    c.saveState(); c.setFillColor(NAVY); c.rect(0, Hh - 6.2 * cm, W, 6.2 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("BB", 24)
    c.drawString(2 * cm, Hh - 2.8 * cm, "Qué coche buscar en Alemania")
    c.drawString(2 * cm, Hh - 3.9 * cm, "y a qué precio")
    c.setFont("B", 11.5); c.setFillColor(colors.HexColor("#c9d6e6"))
    c.drawString(2 * cm, Hh - 5.0 * cm, "Guía de compra para importar a Marbella con buena rentabilidad · Noviembre de 2026")
    c.restoreState(); on_page(c, d)


doc = BaseDocTemplate(OUT, pagesize=A4, title="Qué coche buscar en Alemania y a qué precio", author="Estudio de mercado")
doc.addPageTemplates([
    PageTemplate(id="cover", frames=[Frame(2 * cm, 1.9 * cm, 17 * cm, Hh - 6.2 * cm - 2.3 * cm, leftPadding=0, rightPadding=0)], onPage=cover),
    PageTemplate(id="body", frames=[Frame(2 * cm, 1.9 * cm, 17 * cm, Hh - 3.6 * cm, leftPadding=0, rightPadding=0)], onPage=on_page)])
S = [NextPageTemplate("body")]
g = VEH[0]

# ---- 1. La respuesta
S.append(Paragraph("¿Es interesante? Solo comprando por debajo de estos precios", H2))
S.append(Paragraph(
    "Con 50.000 € invertidos en un coche, una rentabilidad buena es <b>al menos un 10 %</b> (unos 5.000 € limpios por coche). "
    "A precio medio de mercado la operación da entre un 0 % y un 3 %: <b>no interesa</b>. Solo interesa la unidad concreta que se consiga "
    f"<b>entre un {pct(VEH[0]['desc10'])} y un {pct(VEH[2]['desc10'])} por debajo de la media alemana</b>, según el modelo. Estos son los topes para un coche de 100.000 km:", P))
S.append(Spacer(1, 7))
BIG = ParagraphStyle("big", parent=P, fontName="BB", fontSize=17, leading=20, textColor=colors.HexColor(G_TX), alignment=1)
CT = ParagraphStyle("ct", parent=P, fontName="BB", fontSize=10, leading=12.5, alignment=1, textColor=NAVY)
CS = ParagraphStyle("cs", parent=SMALL, alignment=1, fontSize=8.2, leading=11)
cards = []
for v in VEH:
    cards.append([Image(os.path.join(A, v["img"]), width=5.2 * cm, height=3.47 * cm),
                  Paragraph(f"{v['n']}.º {v['corto']}", CT), Paragraph(f"Año {v['ref'][0]} · 100.000 km", CS),
                  Paragraph("No pagar más de", CS), Paragraph(eur(v["max10"]), BIG),
                  Paragraph(f"Media en Alemania: {eur(round(v['de_ref'], -2))}<br/><b>Un {pct(v['desc10'])} por debajo</b>", CS)])
t = Table(list(map(list, zip(*cards))), colWidths=[5.66 * cm] * 3)
t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                       ("BOX", (0, 0), (0, -1), 0.7, LINE), ("BOX", (1, 0), (1, -1), 0.7, LINE), ("BOX", (2, 0), (2, -1), 0.7, LINE),
                       ("BACKGROUND", (0, 3), (-1, 5), LIGHT), ("TOPPADDING", (0, 0), (-1, 0), 7),
                       ("TOPPADDING", (0, 1), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -2), 3), ("BOTTOMPADDING", (0, -1), (-1, -1), 8)]))
S.append(t)
S.append(Spacer(1, 8))
rows = [["Rentabilidad por coche", "En un coche de 50.000 €", "Qué hacer"],
        [f"<font color='{R_TX}'><b>Mala: menos del 5 %</b></font>", "Menos de 2.500 €", f"<font color='{R_TX}'><b>No comprar</b></font>"],
        [f"<font color='{A_TX}'><b>Media: del 5 % al 10 %</b></font>", "De 2.500 € a 5.000 €", f"<font color='{A_TX}'><b>No compensa el riesgo: seguir negociando o dejarlo</b></font>"],
        [f"<font color='{G_TX}'><b>Buena: del 10 % al 15 %</b></font>", "De 5.000 € a 7.500 €", f"<font color='{G_TX}'><b>Comprar</b></font>"],
        [f"<font color='{G_TX}'><b>Muy buena: más del 15 %</b></font>", "Más de 7.500 €", f"<font color='{G_TX}'><b>Comprar sin dudar (y desconfiar: revisar bien el coche)</b></font>"]]
S.append(tbl(rows, [5.2 * cm, 4.2 * cm, 7.6 * cm], zebra=False, pad=3.2,
             extra=[("BACKGROUND", (0, 1), (-1, 1), R_BG), ("BACKGROUND", (0, 2), (-1, 2), A_BG), ("BACKGROUND", (0, 3), (-1, 4), G_BG)]))
S.append(Spacer(1, 7))
S.append(box(
    "<b>Lo que esto significa.</b> No es un negocio de comprar cualquier coche del modelo correcto: es esperar la unidad concreta que está barata "
    "y negociarla hasta el tope. Habrá pocas. Si un vendedor no baja hasta el precio máximo, se deja pasar. "
    "<b>Aviso:</b> los precios salen de medias de anuncios (AutoUncle) y de estimaciones, no de ventas reales; antes de cada compra hay que "
    "comprobar a cuánto se anuncia ese mismo coche en España."))
S.append(PageBreak())

# ---- 2. Rentabilidad y por qué los precios
S.append(Paragraph("Qué es una rentabilidad buena, media y mala", H1))
S.append(Paragraph("Rentabilidad = beneficio limpio del coche ÷ todo el dinero que has puesto (coche + viaje + matriculación + garantía).", SUB))
S += bullets([
    "<b>Por qué menos del 5 % es malo.</b> Son menos de 2.500 €. Una avería en garantía cuesta unos 1.000 € y cada mes sin vender el coche pierde 500–600 € de valor: "
    "con un imprevisto y dos meses de espera el beneficio ha desaparecido, después de 4 días de viaje y semanas de gestiones.",
    "<b>Por qué del 5 % al 10 % no compensa.</b> Se gana algo, pero con 50.000 € parados entre uno y tres meses y respondiendo un año por las averías, "
    "el beneficio no paga el riesgo ni el tiempo.",
    "<b>Por qué el 10 % es el listón.</b> Unos 5.000 € por coche dejan margen para absorber una avería y un par de meses de espera y seguir ganando más de 2.500 €. "
    "Si el coche se vende en dos o tres meses, el mismo dinero puede dar cuatro o cinco operaciones al año.",
    "<b>El 15 %</b> exige comprar un 16 % por debajo de la media alemana: aparece muy pocas veces y casi siempre hay un motivo (daño, historial, estafa)."])
S.append(Paragraph("Por qué manda el precio de compra: adónde va el dinero", H2))
c_med = g["de_ref"]; c_bue = g["max10"]


def cascada(c):
    m = g["vta_pru"] - c; iva = m * 21 / 121; b = beneficio(g, c, g["vta_pru"])
    return [eur(g["vta_pru"]), eur(-c), eur(-iva), eur(-g["viaje"]), eur(-ESPANA), eur(b, True), pct(roi(g, c, g["vta_pru"]) * 100, 1)]


A1, A2 = cascada(c_med), cascada(c_bue)
lab = ["Precio de venta realista en España (3 % bajo la media de anuncios)", "Precio de compra en Alemania", "IVA (21 % solo sobre la diferencia entre compra y venta)",
       "Viaje: avión de ida y vuelta por carretera", "España: matriculación, garantía y preparación", "<b>Beneficio limpio</b>", "<b>Rentabilidad</b>"]
rows = [["GLE 350 de · 2021 · 100.000 km", "Comprando a precio medio", "Comprando al precio máximo"]]
for i, l in enumerate(lab):
    if i >= 5:
        rows.append([l, f"<font color='{R_TX}'><b>{A1[i]}</b></font>", f"<font color='{G_TX}'><b>{A2[i]}</b></font>"])
    else:
        rows.append([l, A1[i], A2[i]])
S.append(tbl(rows, [9.4 * cm, 3.8 * cm, 3.8 * cm], pad=3.2, extra=[("BACKGROUND", (1, 6), (1, 7), R_BG), ("BACKGROUND", (2, 6), (2, 7), G_BG)]))
S.append(Spacer(1, 5))
S.append(Paragraph(
    "El precio de venta lo fija el mercado español y los costes (unos 2.650 €) son casi fijos. <b>Lo único que se puede mover es el precio de compra</b>: "
    "cada 1.000 € que se rebajan en Alemania son unos 830 € más de beneficio y casi dos puntos más de rentabilidad.", P))
S.append(Paragraph("La fórmula para cualquier coche", H2))
F = ParagraphStyle("f", parent=P, fontName="BB", fontSize=12, leading=17, alignment=1, textColor=NAVY)
S.append(box("Precio máximo de compra = precio de venta realista en España × 0,89 − 3.150 €<br/>"
             "<font size=9 color='#5b6470'>para una rentabilidad del 10 %. Para el 5 % se multiplica por 0,94 y para el 15 % por 0,85. "
             "Si el coche no es híbrido enchufable, restar además el impuesto de matriculación.</font>", bg=LIGHT, border=LINE, style=F))
S.append(Paragraph("Precio de venta realista = precio medio al que se anuncia ese mismo coche (año, kilómetros, equipamiento) en España, menos un 3 % de negociación.", SMALL))
S.append(PageBreak())

# ---- 3. Por qué estos vehículos
S.append(Paragraph("Por qué estos tres coches y no otros", H1))
S.append(Paragraph("Tienen que cumplirse tres cosas a la vez. De todos los modelos medidos, solo estos se acercan.", SUB))
rows = [["", "Condición", "Por qué"],
        ["1", "<b>Que en España se anuncie claramente más caro que en Alemania</b>", "Es de donde sale el beneficio. En la mayoría de modelos la diferencia es del 0–5 % y no cubre los 2.650 € de costes."],
        ["2", "<b>Que pague poco o nada de impuesto de matriculación</b>", "Se paga según el CO2: 0 % hasta 120 g/km y 14,75 % desde 200 g/km. En un coche de 50.000 € son entre 0 y unos 7.000 €."],
        ["3", "<b>Que se venda rápido y a buen precio</b>", "SUV y monovolúmenes premium, automáticos y bien equipados. Cada mes parado cuesta 500–600 €."]]
S.append(tbl(rows, [0.9 * cm, 6.6 * cm, 9.5 * cm], pad=2.4))
S.append(Paragraph("Todos los modelos comparados", H2))
OK, KO = f"<font color='{G_TX}'><b>Sí</b></font>", f"<font color='{R_TX}'><b>No</b></font>"
rows = [["Modelo (año)", "Alemania", "España", "Diferencia", "Impuesto", "¿Vale?"],
        ["<b>GLE 350 de (2021)</b>", "50.125 €", "55.176 €", "+5.051 € (+10 %)", "0 %", OK],
        ["<b>V 300 d (2021)</b>", "49.564 €", "57.226 €", "+7.662 € (+15 %)", "9,75–14,75 %", f"<font color='{A_TX}'><b>Con poco CO2</b></font>"],
        ["<b>Cayenne E-Hybrid (2019)</b>", "57.100 €", "59.513 €", "+2.413 € (+4 %)", "0 %", f"<font color='{A_TX}'><b>Muy barato</b></font>"],
        ["Porsche Macan (2019)", "47.806 €", "52.718 €", "+4.912 € (+10 %)", "14,75 %", KO],
        ["Land Rover Defender (2021)", "54.700 €", "55.562 €", "+860 € (+2 %)", "14,75 %", KO],
        ["Tesla Model Y (2022–2023)", "34.600 €", "34.500 €", "≈ 0 €", "0 %", KO],
        ["Porsche 718 (2018–2019)", "62.700 €", "62.800 €", "≈ 0 €", "14,75 %", KO],
        ["VW California T6.1 (2021)", "54.715 €", "51.571 €", "−3.144 € (−6 %)", "alto", KO]]
S.append(tbl(rows, [4.6 * cm, 2.3 * cm, 2.0 * cm, 3.3 * cm, 2.5 * cm, 2.3 * cm], pad=2.2))
S.append(Paragraph("Precios medios de anuncios (AutoUncle, 2026). El Macan es el más visible en Marbella, pero su impuesto se come toda la diferencia: sale en pérdidas.", SMALL))
S.append(Paragraph("Por qué son más baratos en Alemania y más caros en España", H2))
S += bullets([
    "<b>Hay mucha más oferta en Alemania.</b> Del GLE 350 de 2021 hay 288 anuncios en Alemania frente a 134 en toda España; del V 300 d, 273 frente a 32. "
    "El stock alemán de coches de combustión sube y sus precios bajan, lo que ayuda a negociar.",
    "<b>Alemania produce muchos híbridos enchufables de segunda mano</b> porque allí son coches de empresa habituales; al acabar el contrato salen al mercado en grandes cantidades (contexto general, no medido aquí).",
    "<b>En España el híbrido enchufable usado está muy demandado:</b> sus ventas crecen un 45,6 % y lleva etiqueta CERO, mientras hay pocas unidades.",
    "<b>La diferencia no es mayor porque muchos ya hacen esto:</b> Alemania es el origen del 44 % de los usados importados en España. Por eso el margen está en la unidad barata, no en el modelo."])
S.append(Paragraph("Dónde venderlos: Marbella, alrededores o toda España", H2))
S += bullets([
    "<b>No hay prueba de que en Marbella se pague más.</b> Los precios de esta guía son medias de toda España, y los anuncios de Marbella están en esa línea.",
    "<b>Lo que da Marbella es salida:</b> 185 de los 308 Porsche de ocasión de la provincia de Málaga se anuncian allí, y hay comprador extranjero de poder adquisitivo alto.",
    "<b>Lo sensato es anunciar en portales nacionales</b> (coches.net, AutoScout24) con el coche en Marbella: llega a toda España y Andalucía es la comunidad con más ventas de usados."])
S.append(PageBreak())

# ---- 4. Filtros y ejemplo de negociación
S.append(Paragraph("Cómo decidir y negociar un coche concreto", H1))
S.append(Paragraph("Primero los cinco filtros; si los pasa, se calcula el tope y se negocia hasta ahí.", SUB))
rows = [["", "Filtro (si falla uno, se descarta)", "Por qué"],
        ["1", "<b>Híbrido enchufable</b> (CO2 inferior a 120 g/km en el certificado de conformidad)", "Paga 0 % de impuesto de matriculación."],
        ["2", "<b>Vendedor particular o concesionario con «§25a»</b> (differenzbesteuert)", "El IVA en España se paga solo sobre el margen, no sobre el precio entero."],
        ["3", "<b>Precio igual o inferior al máximo</b> de su año y kilómetros", "Por encima, la rentabilidad baja del 10 %."],
        ["4", "<b>Historial limpio</b>: sin accidentes, mantenimiento sellado, 1–2 dueños", "Como vendedor profesional respondes un año por las averías."],
        ["5", "<b>Más de 6 meses y más de 6.000 km</b>", "Si no, cuenta como coche nuevo y paga el 21 % de IVA en España."]]
S.append(tbl(rows, [0.9 * cm, 8.4 * cm, 7.7 * cm], pad=3.0))
S.append(Paragraph("Ejemplo: un GLE 350 de de 2021 con 90.000 km anunciado a 48.900 €", H2))
ej_v = venta(g, 2021, 90000); ej_p = ej_v * 0.97; ej_c = 48900
m10, m5 = maximo(g, ej_p, BUENA), maximo(g, ej_p, MEDIA)
rows = [["Paso", "Cuenta", "Resultado"],
        ["1. ¿A cuánto se anuncia el mismo coche en España?", "Media de anuncios iguales (2021, 90.000 km)", eur(round(ej_v, -2))],
        ["2. Precio de venta realista", "Menos un 3 % de negociación", eur(round(ej_p, -2))],
        ["3. Rentabilidad si lo compro a lo que piden", f"Comprando a {eur(ej_c)}: beneficio {eur(beneficio(g, ej_c, ej_p), True)}", f"<font color='{R_TX}'><b>{pct(roi(g, ej_c, ej_p) * 100, 1)} · Mala</b></font>"],
        ["4. Tope para rentabilidad media (5 %)", "Por encima de este precio, ni plantearlo", eur(m5)],
        ["5. <b>Tope para rentabilidad buena (10 %)</b>", f"Hay que conseguir una rebaja de {eur(ej_c - m10)} ({pct((1 - m10 / ej_c) * 100)})", f"<font color='{G_TX}'><b>{eur(m10)}</b></font>"]]
S.append(tbl(rows, [6.3 * cm, 7.4 * cm, 3.3 * cm], pad=3.0, extra=[("BACKGROUND", (2, 3), (2, 3), R_BG), ("BACKGROUND", (2, 5), (2, 5), G_BG)]))
S.append(Spacer(1, 5))
S += bullets([
    f"<b>Cómo negociarlo:</b> abrir con una oferta por debajo del tope (por ejemplo {eur(m10 - 1500)}), justificarla con anuncios iguales más baratos y con lo que haya que gastar en el coche, "
    f"y subir como mucho hasta {eur(m10)}.",
    f"<b>Si el vendedor no baja de {eur(m10)}, se deja.</b> Una rebaja del {pct((1 - m10 / ej_c) * 100)} sobre el precio anunciado es difícil en un concesionario y más posible con un particular con prisa o un coche que lleva meses publicado.",
    "<b>Antes de ofrecer nada:</b> comprobar el paso 1 con anuncios reales de ese día en coches.net. Si en España se anuncia más barato de lo previsto, el tope baja en la misma proporción."])
S.append(PageBreak())

# ---- 5. Fichas por vehículo
for v in VEH:
    S.append(Paragraph(f"Objetivo {v['n']} · {v['nombre']}", H1))
    S.append(Paragraph(f"{v['tipo']} · {v['anos']}", SUB))
    img = Image(os.path.join(A, v["img"]), width=7.2 * cm, height=4.8 * cm)
    left = Table([[img], [Paragraph(v["cred"] + " Imagen ilustrativa del modelo.", SMALL)]], colWidths=[7.2 * cm])
    left.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    MAXS = ParagraphStyle("mx", parent=P, alignment=1, fontSize=9, leading=12, textColor=GREY)
    r5 = roi(v, v["de_ref"], v["vta_pru"]) * 100
    right = Table([[Paragraph(f"AÑO {v['ref'][0]} · 100.000 KM · NO PAGAR MÁS DE", MAXS)], [Paragraph(eur(v["max10"]), ParagraphStyle("bg", parent=BIG, fontSize=24, leading=28))],
                   [Paragraph(f"para una rentabilidad del 10 % · un {pct(v['desc10'])} bajo la media alemana ({eur(round(v['de_ref'], -2))})", MAXS)],
                   [Paragraph(f"<b>Comprado a precio medio alemán, la rentabilidad sería del {pct(r5, 1).replace('-', '−')}: mala.</b> "
                              f"Para un 5 % el tope es {eur(v['max5'])}; para un 15 %, {eur(v['max15'])}.", ParagraphStyle("pq", parent=P, fontSize=9.2, leading=12.8))]], colWidths=[9.3 * cm])
    right.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 2), G_BG), ("BOX", (0, 0), (-1, 2), 0.7, colors.HexColor("#9ccfb0")),
                               ("TOPPADDING", (0, 0), (-1, 0), 9), ("BOTTOMPADDING", (0, 2), (-1, 2), 9), ("TOPPADDING", (0, 3), (-1, 3), 9),
                               ("LEFTPADDING", (0, 3), (-1, 3), 2)]))
    top = Table([[left, right]], colWidths=[7.7 * cm, 9.3 * cm])
    top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    S.append(top)
    S.append(Paragraph("Precio máximo de compra según año y kilómetros", H2))
    S.append(tabla_maximos(v))
    S.append(Paragraph(
        v["nota_refs"] + " El ajuste por kilómetros (800 € cada 10.000 km) es una estimación. «Venta realista» = media de anuncios en España menos un 3 %. "
        f"Costes incluidos: viaje {eur(v['viaje'])}, España {eur(ESPANA)} e IVA sobre el margen. Antes del impuesto sobre el beneficio.", SMALL))
    S.append(Paragraph("Qué unidad buscar", H2))
    S.append(tbl([["Referencia", "Criterio"]] + [[a, b] for a, b in v["buscar"]] + [[a, b] for a, b in v["ficha"]], [4.3 * cm, 12.7 * cm], pad=2.4))
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
    "No hay datos suficientes para ponerles precio máximo; se les aplica la fórmula de la página 2 con anuncios reales.", P))
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
    print(v["key"], "max10", v["max10"], "max5", v["max5"], "max15", v["max15"], "desc", round(v["desc10"], 1), "de_ref", round(v["de_ref"]), "roi medio", round(roi(v, v["de_ref"], v["vta_pru"]) * 100, 1))
print("ejemplo", round(ej_v), m10, m5)
