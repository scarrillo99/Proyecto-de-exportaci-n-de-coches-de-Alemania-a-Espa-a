"""Genera el PDF del estudio: vehículos, ruta, costes del viaje, inversión y retorno.

Uso: python3 reports/generar_pdf.py
Requiere reportlab. Lee las imágenes de reports/assets/.
"""
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "Importación coches Alemania a Marbella.pdf")

FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("B", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("BB", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("B", normal="B", bold="BB", italic="B", boldItalic="BB")

NAVY = colors.HexColor("#12263f")
BLUE = colors.HexColor("#0b5cad")
RED = colors.HexColor("#c0392b")
GREEN = colors.HexColor("#1e7d4f")
GREY = colors.HexColor("#5b6470")
LIGHT = colors.HexColor("#f2f5f8")
LINE = colors.HexColor("#cfd6de")
AMBER = colors.HexColor("#fff6e0")

P = ParagraphStyle("p", fontName="B", fontSize=9.2, leading=13, textColor=colors.HexColor("#1c2530"))
SMALL = ParagraphStyle("s", parent=P, fontSize=7.6, leading=10.4, textColor=GREY)
H1 = ParagraphStyle("h1", parent=P, fontName="BB", fontSize=17, leading=21, textColor=NAVY, spaceAfter=6)
H2 = ParagraphStyle("h2", parent=P, fontName="BB", fontSize=11.5, leading=15, textColor=BLUE, spaceBefore=8, spaceAfter=4)
CELL = ParagraphStyle("c", parent=P, fontSize=8.3, leading=11)
CELLB = ParagraphStyle("cb", parent=CELL, fontName="BB")
CELLH = ParagraphStyle("ch", parent=CELLB, textColor=colors.white)
NOTE = ParagraphStyle("n", parent=P, fontSize=8.6, leading=12)


def eur(x, sign=False):
    s = f"{abs(x):,.0f}".replace(",", ".")
    if x < 0:
        return f"−{s} €"
    return ("+" if sign else "") + s + " €"


def pct(x):
    return f"{x:.1f}".replace(".", ",") + " %"


def tbl(rows, widths, head=True, zebra=True, bold_last=False, pad=3.5, style_extra=()):
    data = []
    for i, r in enumerate(rows):
        st = CELLH if (head and i == 0) else (CELLB if (bold_last and i == len(rows) - 1) else CELL)
        data.append([c if not isinstance(c, str) else Paragraph(c, st) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
          ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]
    if head:
        st += [("BACKGROUND", (0, 0), (-1, 0), NAVY)]
    if zebra:
        for i in range(1 if head else 0, len(rows)):
            if (i % 2) == 0:
                st.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    if bold_last:
        st.append(("BACKGROUND", (0, len(rows) - 1), (-1, len(rows) - 1), colors.HexColor("#e3ecf6")))
    st += list(style_extra)
    t.setStyle(TableStyle(st))
    return t


def box(text, bg=AMBER, border=colors.HexColor("#e2c46b")):
    t = Table([[Paragraph(text, NOTE)]], colWidths=[17 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.6, border),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return t


# ---------------------------------------------------------------- datos y cálculos
KM = {"Alemania": 244, "Francia": 861, "España": 1164}          # Stuttgart–Marbella, 2.269 km (OSRM)
KM_TOTAL = sum(KM.values())
PRECIO = {"diésel": {"Alemania": 2.22, "Francia": 2.22, "España": 1.864},
          "gasolina": {"Alemania": 1.978, "Francia": 2.04, "España": 1.668}}

# Partidas fijas del viaje (estimaciones del estudio), sin combustible
FIJO_1P = [("Vuelo Málaga → Stuttgart (1 persona, solo ida)", 110), ("Traslados (Marbella–aeropuerto, aeropuerto–vendedor)", 60),
           ("Hotel en Alemania, 1 noche", 115), ("Dietas, 4 días × 45 €", 180),
           ("Inspección previa (TÜV / DEKRA / ADAC)", 100), ("Placas de exportación + seguro 30 días + impuesto", 180),
           ("Peajes Francia y España", 96), ("Hoteles en ruta, 2 noches × 80 €", 160), ("Varios (kit, aparcamiento, lavado)", 30)]
FIJO_2P = [("Vuelos Málaga → Stuttgart (2 personas)", 220), ("Traslados", 60), ("Hotel en Alemania, 1 noche (doble)", 135),
           ("Dietas, 2 personas × 4 días × 45 €", 360), ("Inspección previa", 100), ("Placas de exportación + seguro + impuesto", 180),
           ("Peajes Francia y España", 96), ("Hotel en ruta, 1 noche (doble)", 100), ("Varios", 30)]
OTROS = [("Trámites de matriculación en España (ITV, tasa DGT, gestoría, placas, IVTM)", 600),
         ("Póliza de garantía mecánica 12 meses", 350), ("Preparación y anuncios", 300)]
OTROS_T = sum(v for _, v in OTROS)


def combustible(tipo, l100):
    return sum(KM[p] * l100 / 100 * PRECIO[tipo][p] for p in KM)


VEH = [
    dict(key="gle", n="1.º", nombre="Mercedes-Benz GLE 350 de 4MATIC", gen="V167 · híbrido enchufable diésel · 2020–2021",
         img="gle_350de.jpg", cred="Foto: Charles (Port Chester, NY), CC BY 2.0, vía Wikimedia Commons (recortada). GLE 350 de 4MATIC de 2021.",
         fuel="diésel", l100=7.5, compra=50125, venta=55176, iedmt_tip=0, iedmt_pru=0, iedmt_txt="0 % (CO2 por debajo de 120 g/km)",
         ficha=[("Código / generación", "V167 (GLE desde 2019), 5 plazas"),
                ("Motor térmico", "2.0 diésel 4 cil. (OM 654), 194 CV"),
                ("Motor eléctrico", "136 CV; potencia conjunta 320 CV y 700 Nm"),
                ("Batería / autonomía eléctrica", "31,2 kWh; unos 90–100 km WLTP"),
                ("Cambio y tracción", "Automático 9G-TRONIC, 4MATIC"),
                ("Prestaciones", "0–100 km/h en 6,8 s; 210 km/h"),
                ("Depósito / maletero", "65 L / 490 L"),
                ("CO2 WLTP", "≈ 20–30 g/km (leer en el COC)"),
                ("Etiqueta DGT", "CERO"),
                ("Impuesto de matriculación", "0 %")],
         buscar=[("Texto de búsqueda", "«Mercedes-Benz GLE 350 de 4MATIC» (ojo: <b>350 de</b>, no 350 d)"),
                 ("Primera matriculación", "2020–2021 (más de 6 meses y más de 6.000 km)"),
                 ("Kilometraje objetivo", "80.000–120.000 km"),
                 ("Precio de compra objetivo", "≤ 47.600 € (5 % bajo la media de 50.125 €)"),
                 ("Precio de venta de referencia", "≈ 55.000 € (media española 2021)"),
                 ("Tipo de vendedor", "Particular o concesionario «§25a / differenzbesteuert»"),
                 ("Equipamiento que vende", "AMG Line, techo panorámico, MBUX doble pantalla, cámara 360°, Burmester, carga rápida DC"),
                 ("Revisar siempre", "Certificado de salud de la batería, cables de carga, historial Mercedes completo, «unfallfrei», 2 llaves")]),
    dict(key="v", n="2.º", nombre="Mercedes-Benz V 300 d", gen="W447 (restyling 2019) · monovolumen diésel · 2020–2021",
         img="v_300d.jpg", cred="Foto: Charles (Port Chester, NY), CC BY 2.0, vía Wikimedia Commons (recortada). V 300 d 4MATIC de 2022.",
         fuel="diésel", l100=8.5, compra=49564, venta=57226, iedmt_tip=2282, iedmt_pru=7311,
         iedmt_txt="9,75 % o 14,75 % según el CO2 exacto",
         ficha=[("Código / generación", "W447, restyling de 2019; 6–8 plazas"),
                ("Motor", "2.0 diésel 4 cil. (OM 654), 239 CV y 500 Nm"),
                ("Cambio y tracción", "Automático 9G-TRONIC; trasera o 4MATIC"),
                ("Carrocerías", "Compacta 4,90 m · Larga 5,14 m · Extralarga 5,37 m"),
                ("Prestaciones", "0–100 km/h en unos 7,8 s; 220 km/h"),
                ("Depósito", "57 L (70 L opcional)"),
                ("CO2 WLTP", "≈ 190–228 g/km según versión (leer en el COC)"),
                ("Etiqueta DGT", "C"),
                ("Impuesto de matriculación", "9,75 % (160–200 g) o 14,75 % (200 g o más)")],
         buscar=[("Texto de búsqueda", "«Mercedes-Benz V 300 d» Avantgarde / Exclusive / AMG Line, «lang»"),
                 ("Primera matriculación", "2020–2021"),
                 ("Kilometraje objetivo", "80.000–110.000 km"),
                 ("Precio de compra objetivo", "≤ 47.100 € (5 % bajo la media de 49.564 €)"),
                 ("Precio de venta de referencia", "≈ 57.000 € (media española 2021, muestra pequeña)"),
                 ("Tipo de vendedor", "§25a para vender a particular; «MwSt. ausweisbar» si el cliente es empresa"),
                 ("Equipamiento que vende", "7 plazas en cuero, puertas eléctricas, techo panorámico, AMG Line, Burmester, mesa central"),
                 ("Revisar siempre", "<b>CO2 por debajo de 200 g/km en el COC</b>, uso anterior (taxi, alquiler, shuttle), puertas correderas, AdBlue")]),
    dict(key="cay", n="3.º", nombre="Porsche Cayenne E-Hybrid", gen="9YA (tercera generación) · híbrido enchufable gasolina · 2018–2019",
         img="cayenne_ehybrid.jpg", cred="Foto: Alexandre Prevot, CC BY-SA 2.0, vía Wikimedia Commons. Cayenne E-Hybrid de tercera generación.",
         fuel="gasolina", l100=10.5, compra=57100, venta=59513, iedmt_tip=0, iedmt_pru=0, iedmt_txt="0 % (56–58 g/km según Porsche)",
         ficha=[("Código / generación", "9YA / E3 (desde 2018), 5 plazas"),
                ("Motor térmico", "3.0 V6 turbo gasolina, 340 CV"),
                ("Motor eléctrico", "136 CV; potencia conjunta 462 CV y 700 Nm"),
                ("Batería / autonomía eléctrica", "14,1 kWh; unos 40 km"),
                ("Cambio y tracción", "Tiptronic S de 8 marchas, total"),
                ("Prestaciones", "0–100 km/h en 5,0 s; 253 km/h"),
                ("Depósito / maletero", "75 L / 645 L"),
                ("CO2", "56–58 g/km (dato de Porsche; leer WLTP en el COC)"),
                ("Etiqueta DGT", "CERO"),
                ("Impuesto de matriculación", "0 %")],
         buscar=[("Texto de búsqueda", "«Porsche Cayenne E-Hybrid» (no Coupé, no Turbo S E-Hybrid)"),
                 ("Primera matriculación", "2018–2019"),
                 ("Kilometraje objetivo", "80.000–110.000 km"),
                 ("Precio de compra objetivo", "≤ 54.200 € (5 % bajo la media de 57.100 €)"),
                 ("Precio de venta de referencia", "≈ 59.500 € (media española 2019)"),
                 ("Tipo de vendedor", "Particular o §25a; ideal con garantía Porsche Approved"),
                 ("Equipamiento que vende", "Sport Chrono, suspensión neumática, techo panorámico, llantas de 21\", BOSE, cargador de 7,2 kW"),
                 ("Revisar siempre", "Estado de la batería, historial Porsche completo, neumáticos y frenos (caros), «unfallfrei»")]),
]

for v in VEH:
    v["fuel_eur"] = combustible(v["fuel"], v["l100"])
    v["viaje"] = sum(x for _, x in FIJO_1P) + v["fuel_eur"]
    v["viaje2"] = sum(x for _, x in FIJO_2P) + v["fuel_eur"]
    esc = {}
    for nombre, compra, venta, ied in [("Prudente", v["compra"], v["venta"] * 0.97, v["iedmt_pru"]),
                                       ("Típico", v["compra"], v["venta"], v["iedmt_tip"]),
                                       ("Favorable", v["compra"] * 0.95, v["venta"], v["iedmt_tip"])]:
        margen = venta - compra
        iva = max(margen, 0) * 21 / 121
        inversion = compra + v["viaje"] + ied + OTROS_T
        benef = venta - iva - inversion
        esc[nombre] = dict(compra=compra, venta=venta, margen=margen, iva=iva, ied=ied, inversion=inversion,
                           benef=benef, roi=benef / inversion * 100)
    v["esc"] = esc

# ---------------------------------------------------------------- documento
W, Hh = A4


def on_page(c, d):
    c.saveState()
    c.setFont("B", 7.5)
    c.setFillColor(GREY)
    c.drawString(2 * cm, 1.1 * cm, "Importación de coches de Alemania a Marbella · Estudio de inversión y retorno · Noviembre de 2026")
    c.drawRightString(W - 2 * cm, 1.1 * cm, f"Página {d.page}")
    c.setStrokeColor(LINE)
    c.line(2 * cm, 1.45 * cm, W - 2 * cm, 1.45 * cm)
    c.restoreState()


def cover(c, d):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, Hh - 9.2 * cm, W, 9.2 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("BB", 25)
    c.drawString(2 * cm, Hh - 3.6 * cm, "Importación de coches")
    c.drawString(2 * cm, Hh - 4.75 * cm, "de Alemania a Marbella")
    c.setFont("B", 12.5)
    c.drawString(2 * cm, Hh - 6.1 * cm, "Los tres vehículos seleccionados, la ruta, el coste del viaje,")
    c.drawString(2 * cm, Hh - 6.75 * cm, "la inversión y el retorno previsto por coche")
    c.setFont("B", 9.5)
    c.setFillColor(colors.HexColor("#b9c7d8"))
    c.drawString(2 * cm, Hh - 8.2 * cm, "Estudio de mercado · Noviembre de 2026")
    c.restoreState()
    on_page(c, d)


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.9 * cm,
                      title="Importación de coches de Alemania a Marbella", author="Estudio de mercado")
doc.addPageTemplates([
    PageTemplate(id="cover", frames=[Frame(2 * cm, 1.9 * cm, 17 * cm, Hh - 9.2 * cm - 2.5 * cm, id="f0", leftPadding=0, rightPadding=0)], onPage=cover),
    PageTemplate(id="body", frames=[Frame(2 * cm, 1.9 * cm, 17 * cm, Hh - 3.7 * cm, id="f1", leftPadding=0, rightPadding=0)], onPage=on_page)])

S = []
from reportlab.platypus import NextPageTemplate
S.append(NextPageTemplate("body"))

# ---- Portada: resumen
g, vv, cy = VEH
S.append(Paragraph("Resumen en una página", H2))
S.append(Paragraph(
    "Este documento concreta el estudio en números por coche. La conclusión no cambia: <b>comprando a precio medio alemán y "
    "vendiendo a precio medio español el retorno es bajo (entre el 0 % y el 3 % del capital invertido)</b>; el negocio solo "
    "funciona comprando cada unidad al menos un 5 % por debajo de la media alemana, y aun así el retorno queda en torno al 6–7 %.", P))
S.append(Spacer(1, 6))
rows = [["", "Vehículo", "Inversión total", "Beneficio típico", "Beneficio comprando 5 % más barato"]]
for v in VEH:
    t, f = v["esc"]["Típico"], v["esc"]["Favorable"]
    rows.append([v["n"], f"<b>{v['nombre']}</b><br/><font size=7.3 color='#5b6470'>{v['gen']}</font>",
                 eur(t["inversion"]), f"{eur(t['benef'], True)}<br/>({pct(t['roi'])})", f"{eur(f['benef'], True)}<br/>({pct(f['roi'])})"])
S.append(tbl(rows, [1 * cm, 6.9 * cm, 2.7 * cm, 2.9 * cm, 3.5 * cm]))
S.append(Spacer(1, 8))
rows = [["Dato clave del viaje (desde Stuttgart, 1 persona)", "Valor"],
        ["Distancia por carretera Stuttgart → Marbella", "<b>2.269 km</b> (unas 24 h de conducción)"],
        ["Días fuera de casa", "4 (vuelo y compra, placas y salida, 2 días de ruta)"],
        ["Noches de hotel", "3 (1 en Alemania, 2 en ruta)"],
        ["Combustible según el coche", f"{eur(g['fuel_eur'])} (GLE) · {eur(vv['fuel_eur'])} (Clase V) · {eur(cy['fuel_eur'])} (Cayenne)"],
        ["Coste total del viaje, avión de ida y coche de vuelta", f"<b>{eur(g['viaje'])} – {eur(cy['viaje'])}</b> según el coche"]]
S.append(tbl(rows, [8.2 * cm, 8.8 * cm]))
S.append(Spacer(1, 8))
S.append(box(
    "<b>Cómo leer las cifras.</b> Los kilómetros son exactos (cálculo de ruta por carretera). Los precios de compra y venta son "
    "<b>medias de anuncios</b> de un agregador (AutoUncle), no anuncios concretos ni precios de venta reales; no se pudo consultar "
    "mobile.de ni coches.net en directo. Los costes del viaje y el beneficio son <b>estimaciones</b>. Las fichas técnicas son datos de "
    "referencia del fabricante: el dato que manda es el del certificado de conformidad (COC) de cada unidad. Antes de comprar hay que "
    "repetir el cálculo con anuncios reales y validarlo con un asesor fiscal y una gestoría."))
S.append(PageBreak())

# ---- Fichas de vehículos
for v in VEH:
    S.append(Paragraph(f"{v['n']} {v['nombre']}", H1))
    S.append(Paragraph(v["gen"], ParagraphStyle("g", parent=P, textColor=GREY, spaceAfter=6)))
    img = Image(os.path.join(A, v["img"]), width=7.8 * cm, height=5.2 * cm)
    ficha = tbl([["Ficha técnica de referencia", ""]] + [[a, b] for a, b in v["ficha"]], [3.5 * cm, 5.0 * cm], pad=2.2,
                style_extra=[("SPAN", (0, 0), (1, 0))])
    left = Table([[img], [Paragraph(v["cred"], SMALL)]], colWidths=[7.8 * cm])
    left.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    top = Table([[left, ficha]], colWidths=[8.5 * cm, 8.5 * cm])
    top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    S.append(top)
    S.append(Paragraph("Qué unidad buscar exactamente", H2))
    S.append(tbl([["Referencia", "Criterio"]] + [[a, b] for a, b in v["buscar"]], [4.6 * cm, 12.4 * cm], pad=2.4))
    S.append(Paragraph("Inversión y retorno de una unidad", H2))
    e = v["esc"]
    cols = ["Prudente", "Típico", "Favorable"]
    rows = [["Concepto"] + cols,
            ["Precio de compra en Alemania"] + [eur(e[c]["compra"]) for c in cols],
            ["Viaje: avión de ida y vuelta en coche"] + [eur(v["viaje"])] * 3,
            ["Impuesto de matriculación"] + [eur(e[c]["ied"]) for c in cols],
            ["Matriculación, garantía y preparación"] + [eur(OTROS_T)] * 3,
            ["<b>Inversión total por coche</b>"] + [f"<b>{eur(e[c]['inversion'])}</b>" for c in cols],
            ["Precio de venta en Marbella"] + [eur(e[c]["venta"]) for c in cols],
            ["IVA sobre el margen (régimen de bienes usados)"] + [eur(-e[c]["iva"]) for c in cols],
            ["Beneficio neto (antes de IRPF o Sociedades)"] + [eur(e[c]["benef"], True) for c in cols],
            ["Retorno sobre la inversión"] + [pct(e[c]["roi"]) for c in cols]]
    extra = [("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#e3ecf6"))]
    for j, c in enumerate(cols, start=1):
        col = GREEN if e[c]["benef"] > 0 else RED
        extra += [("TEXTCOLOR", (j, 8), (j, 9), col)]
    data_rows = []
    for i, r in enumerate(rows):
        st = CELLH if i == 0 else CELL
        row = []
        for j, cell in enumerate(r):
            if i in (8, 9) and j > 0:
                col = "#1e7d4f" if e[cols[j - 1]]["benef"] > 0 else "#c0392b"
                row.append(Paragraph(f"<font color='{col}'><b>{cell}</b></font>", CELL))
            elif i in (8, 9) and j == 0:
                row.append(Paragraph(f"<b>{cell}</b>", CELL))
            else:
                row.append(Paragraph(cell, st))
        data_rows.append(row)
    S.append(tbl(data_rows, [8.3 * cm, 2.9 * cm, 2.9 * cm, 2.9 * cm], pad=2.4, style_extra=extra))
    S.append(Spacer(1, 4))
    S.append(Paragraph(
        "Prudente: compra a la media alemana y venta un 3 % bajo la media española. Típico: compra y venta a las medias. "
        "Favorable: compra un 5 % bajo la media alemana. " +
        {"gle": "La media de precios mezcla el 350 d y el 350 de; si la unidad es un 350 d (diésel no enchufable) paga impuesto de matriculación y el resultado pasa a pérdida.",
         "v": "En el escenario típico se supone el tramo del 9,75 % sobre un valor fiscal supuesto de 60.000 € × 39 %; si el CO2 del COC es de 200 g/km o más, el beneficio típico baja a unos 200 €. El prudente aplica el 14,75 % sobre el precio de compra.",
         "cay": "Entra en la lista por descarte: a precios medios pierde dinero y solo compensa en unidades muy equipadas compradas claramente bajo la media."}[v["key"]], SMALL))
    S.append(PageBreak())

# ---- Mapa y ruta
S.append(Paragraph("La ruta de vuelta: 2.269 km de Stuttgart a Marbella", H1))
S.append(Paragraph(
    "Distancias calculadas con un planificador de rutas por carretera (OSRM sobre OpenStreetMap), por la ruta más rápida. "
    "Stuttgart es el punto de compra más cercano a Marbella y tiene vuelo directo desde Málaga.", P))
S.append(Spacer(1, 4))
mp = Image(os.path.join(A, "mapa_ruta.png"))
iw, ih = mp.imageWidth, mp.imageHeight
mw = 15.6 * cm
mp.drawWidth, mp.drawHeight = mw, mw * ih / iw
mp.hAlign = "CENTER"
S.append(mp)
S.append(Spacer(1, 6))
rows = [["Origen en Alemania", "Km hasta Marbella", "Horas al volante", "Ruta y peajes"],
        ["<b>Stuttgart</b>", "<b>2.269 km</b>", "24,0 h", "Mulhouse – Lyon – Barcelona – Valencia – Granada. Sin viñeta."],
        ["Fráncfort", "2.332 km", "24,4 h", "Misma ruta que Stuttgart."],
        ["Düsseldorf", "2.345 km", "24,9 h", "Bélgica – París – Burdeos – Madrid – Jaén."],
        ["Múnich", "2.376 km", "25,5 h", "Cruza Austria y Suiza: viñeta suiza (unos 44,50 €) y austriaca."]]
S.append(tbl(rows, [3.2 * cm, 3.0 * cm, 2.8 * cm, 8.0 * cm]))
S.append(PageBreak())

S.append(Paragraph("Etapas, kilómetros por país y combustible", H1))
S.append(Paragraph("Plan de viaje recomendado (1 conductor)", H2))
rows = [["Día", "Qué se hace", "Km", "Horas de volante", "Noche"],
        ["1", "Vuelo Málaga → Stuttgart. Ver el coche, prueba, inspección y negociación.", "—", "—", "Stuttgart"],
        ["2", "Por la mañana: pago, contrato y placas de exportación en la oficina de matriculación. Salida hacia Lyon.", "621", "6,6 h", "Lyon"],
        ["3", "Lyon → Montpellier → La Jonquera → Barcelona → Tarragona.", "727", "7,7 h", "Tarragona"],
        ["4", "Tarragona → Valencia → Murcia → Granada → Málaga → Marbella.", "921", "9,7 h", "En casa"],
        ["", "<b>Total</b>", "<b>2.269</b>", "<b>24,0 h</b>", "3 noches"]]
S.append(tbl(rows, [1.1 * cm, 9.3 * cm, 1.6 * cm, 2.6 * cm, 2.4 * cm], bold_last=True))
S.append(Paragraph(
    "Con dos conductores se puede hacer en dos días de ruta y una sola noche (parada cerca de La Jonquera, km 1.109). "
    "La oficina alemana de matriculación solo abre en días laborables, a menudo solo por la mañana: es lo que puede obligar a una segunda noche en Alemania (unos 160 € más).", SMALL))
S.append(Paragraph("Kilómetros y precio del combustible por país", H2))
rows = [["País", "Km", "Diésel (€/L)", "Gasolina 95 (€/L)", "Consejo"],
        ["Alemania", "244", "2,22", "1,98", "Salir con el depósito que traiga el coche."],
        ["Francia", "861", "2,22", "2,04", "El tramo más caro: repostar lo justo."],
        ["España", "1.164", "1,86", "1,67", "Llenar en La Jonquera: unos 0,35 €/L menos."],
        ["<b>Total</b>", "<b>2.269</b>", "", "", ""]]
S.append(tbl(rows, [2.6 * cm, 1.8 * cm, 2.6 * cm, 3.2 * cm, 6.8 * cm], bold_last=True))
S.append(Paragraph("Precios de surtidor del 9 al 11 de noviembre de 2026, en niveles anormalmente altos. El reparto por país es aproximado (± 15 km).", SMALL))
S.append(Paragraph("Combustible de la vuelta según el coche", H2))
rows = [["Vehículo", "Combustible", "Consumo en autopista", "Litros en 2.269 km", "Coste"]]
for v in VEH:
    rows.append([v["nombre"], v["fuel"].capitalize(), f"{str(v['l100']).replace('.', ',')} L/100 km", f"{KM_TOTAL * v['l100'] / 100:,.0f} L".replace(",", "."), f"<b>{eur(v['fuel_eur'])}</b>"])
S.append(tbl(rows, [5.4 * cm, 2.8 * cm, 3.4 * cm, 3.2 * cm, 2.2 * cm]))
S.append(Paragraph(
    "Consumos estimados para autopista a 120–130 km/h con la batería de los híbridos ya descargada (en viaje largo funcionan casi solo con el motor térmico). "
    "El Cayenne recomienda gasolina de 98 octanos: sumar unos 35 € más.", SMALL))
S.append(PageBreak())

# ---- Coste total del viaje
S.append(Paragraph("Coste total: ir en avión y volver en coche", H1))
S.append(Paragraph("Desglose para 1 persona (1 noche en Alemania, 2 noches en ruta)", H2))
rows = [["Partida", g["nombre"].replace("Mercedes-Benz ", ""), vv["nombre"].replace("Mercedes-Benz ", ""), "Cayenne E-Hybrid"]]
for name, val in FIJO_1P:
    rows.append([name, eur(val), eur(val), eur(val)])
rows.append(["Combustible de la vuelta (2.269 km)"] + [eur(v["fuel_eur"]) for v in VEH])
rows.append(["<b>Total del viaje</b>"] + [f"<b>{eur(v['viaje'])}</b>" for v in VEH])
S.append(tbl(rows, [8.0 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm], bold_last=True))
S.append(Spacer(1, 6))
S.append(Paragraph("Comparación de escenarios (GLE 350 de como referencia)", H2))
f1 = sum(x for _, x in FIJO_1P)
f2 = sum(x for _, x in FIJO_2P)
rows = [["Escenario", "Noches", "Días", "Coste total", "Por coche"],
        ["1 persona, 1 noche en Alemania", "3", "4", eur(f1 + g["fuel_eur"]), eur(f1 + g["fuel_eur"])],
        ["1 persona, 2 noches en Alemania", "4", "5", eur(f1 + 160 + g["fuel_eur"]), eur(f1 + 160 + g["fuel_eur"])],
        ["2 personas, 1 coche (se turnan al volante)", "2", "3–4", eur(f2 + g["fuel_eur"]), eur(f2 + g["fuel_eur"])],
        ["2 personas, 2 coches en el mismo viaje", "3", "4", eur(f2 + 60 + 180 + 96 + 100 + 2 * g["fuel_eur"]), f"<b>{eur((f2 + 60 + 180 + 96 + 100 + 2 * g['fuel_eur']) / 2)}</b>"],
        ["Alternativa: viajar a verlo y enviarlo en camión abierto", "1", "2", "≈ 1.740 €", "≈ 1.740 €"],
        ["Alternativa: compra a distancia con inspección y camión", "0", "0", "≈ 1.250 €", "≈ 1.250 €"]]
S.append(tbl(rows, [8.2 * cm, 1.6 * cm, 1.5 * cm, 2.8 * cm, 2.9 * cm]))
S.append(Spacer(1, 6))
S.append(box(
    "<b>Qué es estimación y qué no.</b> Con fuente: tasa y seguro de las placas de exportación (80–120 €), peaje Lyon–La Jonquera (55,50 €), "
    "precios del combustible y tarifas del camión (900–1.500 €). Estimado: vuelo (40–220 € según fecha), hotel, dietas y traslados. "
    "El mismo viaje puede costar desde unos 890 € (todo en mínimos) hasta unos 2.440 € (temporada alta y reserva tardía). "
    "No incluye el desgaste de sumar 2.269 km al coche, posibles multas ni asistencia en carretera: el seguro de las placas de exportación cubre solo daños a terceros."))
S.append(Paragraph("Otros costes por coche, ya en España", H2))
rows = [["Concepto", "Importe usado", "Rango"],
        ["Trámites de matriculación: ITV de importación (≈ 124 €), tasa DGT (99,77 €), gestoría (150–300 €), placas, impuesto de circulación", "600 €", "355–940 €"],
        ["Póliza de garantía mecánica de 12 meses (obligatorio dar 1 año de garantía como vendedor profesional)", "350 €", "150–500 €"],
        ["Preparación para la venta y anuncios (limpieza, fotos, portales)", "300 €", "sin fuente"],
        ["<b>Total</b>", f"<b>{eur(OTROS_T)}</b>", ""]]
S.append(tbl(rows, [11.4 * cm, 2.6 * cm, 3.0 * cm], bold_last=True))
S.append(PageBreak())

# ---- Inversión y retorno
S.append(Paragraph("Inversión y retorno: los tres coches frente a frente", H1))
rows = [["Escenario típico (compra y venta a precios medios)"] + [v["nombre"].replace("Mercedes-Benz ", "") for v in VEH]]
t = [v["esc"]["Típico"] for v in VEH]
rows += [["Precio de compra"] + [eur(x["compra"]) for x in t],
         ["Viaje"] + [eur(v["viaje"]) for v in VEH],
         ["Impuesto de matriculación"] + [eur(x["ied"]) for x in t],
         ["Matriculación, garantía, preparación"] + [eur(OTROS_T)] * 3,
         ["<b>Capital que hay que poner</b>"] + [f"<b>{eur(x['inversion'])}</b>" for x in t],
         ["Precio de venta"] + [eur(x["venta"]) for x in t],
         ["IVA sobre el margen"] + [eur(-x["iva"]) for x in t],
         ["<b>Beneficio neto</b>"] + [f"<font color='{'#1e7d4f' if x['benef'] > 0 else '#c0392b'}'><b>{eur(x['benef'], True)}</b></font>" for x in t],
         ["<b>Retorno sobre la inversión</b>"] + [f"<font color='{'#1e7d4f' if x['benef'] > 0 else '#c0392b'}'><b>{pct(x['roi'])}</b></font>" for x in t]]
S.append(tbl(rows, [6.8 * cm, 3.4 * cm, 3.4 * cm, 3.4 * cm], style_extra=[("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#e3ecf6"))]))
S.append(Spacer(1, 8))
rows = [["Beneficio neto por coche según el escenario", "Prudente", "Típico", "Favorable"]]
for v in VEH:
    r = [v["nombre"]]
    for c in ["Prudente", "Típico", "Favorable"]:
        x = v["esc"][c]
        r.append(f"<font color='{'#1e7d4f' if x['benef'] > 0 else '#c0392b'}'><b>{eur(x['benef'], True)}</b></font><br/>{pct(x['roi'])}")
    rows.append(r)
S.append(tbl(rows, [7.4 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm]))
S.append(Spacer(1, 8))
S.append(Paragraph("Lo que estos números dicen", H2))
for txt in [
    "<b>El retorno a precios medios no compensa.</b> El mejor caso típico deja unos 1.500 € sobre casi 53.000 € invertidos. Un solo mes más en stock cuesta 500–600 € de depreciación en estos modelos, y una avería fuera de póliza ronda los 1.000 €.",
    "<b>El beneficio está en la unidad, no en el modelo.</b> Cada 1.000 € que se rebaje el precio de compra en la negociación suma unos 830 € de beneficio neto. Comprar un 5 % bajo la media convierte el GLE y la Clase V en operaciones de unos 3.500 €.",
    "<b>El impuesto de matriculación decide.</b> Los dos híbridos enchufables pagan 0 %. La Clase V depende de un dato del certificado de conformidad: con 200 g/km o más de CO2, el beneficio típico prácticamente desaparece.",
    "<b>Regla de compra propuesta.</b> No comprar si, comparando anuncios reales de unidades equivalentes en mobile.de y coches.net, la diferencia de precio no supera con claridad los 6.000 €, y exigir un beneficio previsto de al menos 2.000 € en el escenario típico y positivo en el prudente.",
    "<b>No incluido en el cálculo:</b> el impuesto sobre el beneficio (IRPF o Sociedades), la cuota de autónomos, el coste del tiempo (4 días de viaje más gestiones) ni el coste de tener el capital inmovilizado entre 1 y 3 meses."]:
    S.append(Paragraph("• " + txt, ParagraphStyle("b", parent=P, leftIndent=10, firstLineIndent=-10, spaceAfter=4)))
S.append(PageBreak())

# ---- Documentación
S.append(Paragraph("Documentación: pasos en orden", H1))
S.append(Paragraph("El orden es rígido: cada paso necesita el documento que entrega el anterior. Varios detalles deben confirmarse con la gestoría.", P))


def fase(titulo, items):
    rows = [[titulo, ""]] + [["☐", x] for x in items]
    t = tbl(rows, [0.8 * cm, 16.2 * cm], style_extra=[("SPAN", (0, 0), (1, 0))], zebra=False)
    return KeepTogether([Spacer(1, 6), t])


S.append(fase("Fase 0 · Antes de la primera compra (una sola vez)", [
    "Decidir la forma jurídica con un asesor fiscal: para repetir operaciones hay que darse de alta como autónomo o sociedad (modelo 036, epígrafe 654.1).",
    "Elegir régimen de IVA: lo eficiente para vender a particulares es comprar a particular o a concesionario en régimen de margen (§25a) y revender en régimen de bienes usados.",
    "Elegir gestoría en Málaga o Marbella con experiencia en importación y pedir presupuesto cerrado.",
    "Preguntar a la ITV (VEIASA) cómo se pide cita para un vehículo importado, la tarifa y la espera.",
    "Cotizar una póliza de garantía mecánica y redactar el contrato de venta con la garantía de un año por escrito."]))
S.append(fase("Fase 1 · Antes de viajar", [
    "Comparar anuncios reales de la misma versión, año y kilómetros en Alemania y en España.",
    "Pedir al vendedor: número de bastidor, fotos de la documentación (Teil I y Teil II), última ITV alemana (HU), libro de mantenimiento y confirmación escrita de «unfallfrei» (sin accidentes).",
    "Confirmar que existe el certificado de conformidad europeo (COC) y leer en él el CO2 WLTP. Si falta, pedirlo al fabricante (120–280 €, hasta 21 días laborables en Mercedes).",
    "Informe de historial por número de bastidor y verificación del vendedor (registro mercantil, dirección física, NIF-IVA).",
    "Factura proforma con el régimen de IVA por escrito. Señal solo contra contrato firmado y a una cuenta a nombre del vendedor.",
    "Encargar por adelantado las placas de exportación y pedir cita de ITV de importación en España."]))
S.append(fase("Fase 2 · En Alemania, el día de la compra", [
    "Comprobar que el número de bastidor del coche coincide con Teil I y Teil II; prueba de conducción; dos llaves.",
    "Firmar contrato y factura con bastidor, kilómetros, «unfallfrei», precio y régimen de IVA.",
    "Pagar por transferencia bancaria (en España el límite de efectivo con empresas es de 1.000 €).",
    "Llevarse los originales: Teil I, Teil II, COC, informe de la ITV alemana, libro de mantenimiento, facturas y las dos llaves.",
    "Obtener las placas de exportación (Ausfuhrkennzeichen, banda roja). Las placas amarillas de 5 días no valen para cruzar Francia."]))
S.append(fase("Fase 3 · El viaje", [
    "Llevar en el coche: documentación con la anotación de exportación, certificado de seguro, contrato o factura, DNI y carné.",
    "Chaleco y triángulos. De noviembre a marzo: neumáticos de invierno o fundas (obligatorio en zonas de montaña de Francia y con nieve en Alemania).",
    "Guardar los tiques de peaje y combustible como prueba del transporte."]))
S.append(fase("Fase 4 · En España, hasta tener placas (de 2 a 6 semanas)", [
    "Ficha técnica reducida, solo si falta el COC (50–150 €).",
    "ITV de importación: comprobar que la tarjeta recoge la fecha de primera matriculación, la norma Euro y el CO2 WLTP.",
    "Impuesto de matriculación (modelo 576): se presenta aunque la cuota sea cero.",
    "Impuesto de circulación en el Ayuntamiento de Marbella.",
    "Solicitud de matriculación en la DGT (tasa de 99,77 €), placas, seguro español y etiqueta ambiental.",
    "El plazo para matricular es de un mes. Si la ITV se retrasa: placas verdes temporales (20,61 €, 60 días)."]))
S.append(fase("Fase 5 · La venta", [
    "Factura de venta con la mención «Régimen especial de los bienes usados» (sin IVA desglosado).",
    "Contrato con la garantía de un año pactada por escrito, kilometraje y origen importado declarado.",
    "Entregar al cliente el historial alemán, el informe por bastidor y la póliza de garantía.",
    "Cobro por transferencia y cambio de titularidad en la DGT en un máximo de 30 días.",
    "Declarar el IVA del margen en el modelo 303 del trimestre."]))
S.append(Spacer(1, 8))
S.append(box(
    "<b>Decisión pendiente para la gestoría:</b> matricular el coche a nombre de la empresa y transferirlo después (permite tenerlo expuesto, "
    "pero el cliente será segundo titular) o matricularlo directamente a nombre del cliente final (primer titular, pero la venta debe estar cerrada antes)."))
S.append(Spacer(1, 14))

# ---- Verificaciones y fuentes
S.append(Paragraph("Qué hay que verificar antes de comprar", H1))
rows = [["Punto sin confirmar", "Por qué importa", "Con quién"],
        ["Precios reales de unidades comparables en mobile.de y coches.net", "Decide si hay negocio: todo el cálculo parte de medias de un agregador", "Búsqueda propia"],
        ["CO2 WLTP exacto de cada unidad (GLE 350 de y, sobre todo, V 300 d)", "Un tramo de diferencia mueve 1.400 € o más", "COC del vendedor"],
        ["Valor fiscal del coche en las tablas de Hacienda y porcentaje por antigüedad", "Es la base del impuesto de matriculación; aquí se ha supuesto", "Asesor / gestoría"],
        ["Tipo del impuesto de matriculación en Andalucía para 200 g/km o más (14,75 % o 16,90 %)", "Afecta a la Clase V", "Asesor fiscal"],
        ["Funcionamiento exacto del régimen de bienes usados y forma jurídica", "Un IVA mal planteado convierte la operación en pérdida", "Asesor fiscal"],
        ["Tarifa y espera de la ITV de importación; impuesto de circulación de Marbella", "Coste y plazo hasta tener placas", "VEIASA / gestoría"],
        ["Vuelo, hotel, seguro de placas, camión y póliza de garantía en fechas concretas", "Las cifras del viaje son en parte estimadas", "Cotizaciones reales"],
        ["Fichas técnicas de este documento", "Son datos de referencia del fabricante, no de la unidad concreta", "COC y vendedor"]]
S.append(tbl(rows, [7.2 * cm, 6.4 * cm, 3.4 * cm]))
S.append(Paragraph("Modelos descartados", H2))
S.append(Paragraph(
    "Porsche Macan 2.0 (paga el 14,75 % y sale en pérdidas de unos 1.650 € a precios medios), VW California (igual o más barata en España), "
    "Tesla Model Y y eléctricos en general (sin diferencia de precio), Porsche 718 y 911, Land Rover Defender, y cualquier coche de más de 200 g/km de CO2 "
    "o con menos de 6 meses o 6.000 km (se considera nuevo y paga el 21 % de IVA en España).", P))
S.append(Paragraph("Fuentes y créditos", H2))
for txt in [
    "Precios medios de anuncios: AutoUncle.de y AutoUncle.es (instantáneas de 2026), leídos a través de resultados de búsqueda.",
    "Ruta y kilómetros: Project OSRM sobre datos de © colaboradores de OpenStreetMap. Mapa base: Natural Earth.",
    "Combustible: ADAC (Alemania), Selectra (Francia) y prensa económica española, 9–11 de noviembre de 2026.",
    "Placas de exportación: ADAC, bussgeldkatalog.org y oficinas de matriculación de Berlín y Karlsruhe. Tasas españolas: RACE y DGT.",
    "Fotografías: Wikimedia Commons. GLE 350 de y V 300 d, de Charles (Port Chester, Nueva York), licencia CC BY 2.0, recortadas. "
    "Cayenne E-Hybrid, de Alexandre Prevot, licencia CC BY-SA 2.0. Son fotos ilustrativas del modelo, no de unidades en venta.",
    "El informe completo, con todas las fuentes enlazadas y las notas de investigación, está en el repositorio del proyecto (carpetas reports y research_notes)."]:
    S.append(Paragraph("• " + txt, ParagraphStyle("b2", parent=SMALL, leftIndent=10, firstLineIndent=-10, spaceAfter=3, fontSize=8, leading=11)))

doc.build(S)
print("OK", OUT)
for v in VEH:
    print(v["key"], round(v["fuel_eur"]), round(v["viaje"]), {k: (round(e["inversion"]), round(e["benef"]), round(e["roi"], 1)) for k, e in v["esc"].items()})
