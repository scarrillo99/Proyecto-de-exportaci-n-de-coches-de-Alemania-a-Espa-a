"""Genera «Guía para el buscador de coches.pdf»: el encargo para quien busca los coches en Alemania.

Uso: python3 reports/generar_pdf_buscador.py   (requiere reportlab; imágenes en reports/assets/)
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "Guía para el buscador de coches.pdf")
FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("B", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("BB", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFontFamily("B", normal="B", bold="BB", italic="B", boldItalic="BB")

NAVY = colors.HexColor("#12263f"); BLUE = colors.HexColor("#0b5cad"); GREY = colors.HexColor("#5b6470")
LIGHT = colors.HexColor("#f2f5f8"); LINE = colors.HexColor("#cfd6de")
G_BG = colors.HexColor("#dff3e6"); G_TX = "#17693f"; A_BG = colors.HexColor("#fff1cc"); A_TX = "#8a5a00"
R_BG = colors.HexColor("#fbe0dc"); R_TX = "#a93226"

P = ParagraphStyle("p", fontName="B", fontSize=10, leading=14.5, textColor=colors.HexColor("#1c2530"))
SMALL = ParagraphStyle("s", parent=P, fontSize=7.8, leading=10.6, textColor=GREY)
H1 = ParagraphStyle("h1", parent=P, fontName="BB", fontSize=18, leading=22, textColor=NAVY, spaceAfter=4)
SUB = ParagraphStyle("sub", parent=P, textColor=GREY, spaceAfter=8)
H2 = ParagraphStyle("h2", parent=P, fontName="BB", fontSize=12, leading=15, textColor=BLUE, spaceBefore=10, spaceAfter=5)
CELL = ParagraphStyle("c", parent=P, fontSize=8.8, leading=11.6)
CELLH = ParagraphStyle("ch", parent=CELL, fontName="BB", textColor=colors.white)
BUL = ParagraphStyle("b", parent=P, leftIndent=11, firstLineIndent=-11, spaceAfter=3.5)


def eur(x):
    s = f"{abs(x):,.0f}".replace(",", ".")
    return f"−{s} €" if x < 0 else s + " €"


def tbl(rows, widths, head=True, zebra=True, pad=3.4, extra=()):
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
    t = Table([[Paragraph(text, style or ParagraphStyle("n", parent=P, fontSize=9.4, leading=13.2))]], colWidths=[w])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("BOX", (0, 0), (-1, -1), 0.7, border),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t


def bullets(items):
    return [Paragraph("• " + x, BUL) for x in items]


# ------------------------------------------------------------ cálculo (igual que la guía de compra)
EUR_KM = 0.08
BANDAS = [60000, 80000, 100000, 120000, 140000]
MARGEN_AVISO = 1.05    # se avisa si el precio anunciado está hasta un 5 % por encima del tope (margen de negociación)
VEH = [
    dict(nombre="Mercedes-Benz GLE 350 de 4MATIC", corto="GLE 350 de", img="gle_350de.jpg", costes=2628,
         refs={2021: (55176, 100300), 2020: (51286, 118000)},
         nota="Tiene que ser «350 <b>de</b>» (híbrido enchufable). El «350 d» sin la e no vale."),
    dict(nombre="Mercedes-Benz V 300 d", corto="V 300 d", img="v_300d.jpg", costes=4956,
         refs={2021: (57226, 83700), 2020: (52850, 83700)},
         nota="Solo si el CO2 del certificado de conformidad es inferior a 200 g/km y no ha sido taxi ni alquiler."),
    dict(nombre="Porsche Cayenne E-Hybrid", corto="Cayenne E-Hybrid", img="cayenne_ehybrid.jpg", costes=2720,
         refs={2019: (59513, 91000)},
         nota="No Coupé ni Turbo S E-Hybrid. Mejor con garantía Porsche Approved."),
]


def tope(v, ano, km, r=0.10):
    pe, ke = v["refs"][ano]
    vp = (pe - (km - ke) * EUR_KM) * 0.97
    return int(((vp / 1.21 - v["costes"] * (1 + r)) / (r + 1 / 1.21)) // 100 * 100)


def tabla_topes(v):
    rows = [["Año", "Kilómetros", "Avisar si piden hasta", "TOPE DE COMPRA"]]
    extra = [("BACKGROUND", (3, 0), (3, 0), colors.HexColor(G_TX))]
    i = 1
    for ano in sorted(v["refs"], reverse=True):
        for km in BANDAS:
            t = tope(v, ano, km)
            rows.append([f"<b>{ano}</b>", f"{km:,} km".replace(",", "."), eur(int(t * MARGEN_AVISO // 100 * 100)), f"<font color='{G_TX}'><b>{eur(t)}</b></font>"])
            extra.append(("BACKGROUND", (3, i), (3, i), G_BG)); i += 1
    return tbl(rows, [1.5 * cm, 2.7 * cm, 3.6 * cm, 3.2 * cm], pad=2.2, extra=extra)


# ------------------------------------------------------------ documento
W, Hh = A4


def on_page(c, d):
    c.saveState(); c.setFont("B", 7.5); c.setFillColor(GREY)
    c.drawString(2 * cm, 1.1 * cm, "Guía para el buscador de coches · Importación de Alemania a Marbella · Noviembre de 2026")
    c.drawRightString(W - 2 * cm, 1.1 * cm, f"Página {d.page}")
    c.setStrokeColor(LINE); c.line(2 * cm, 1.45 * cm, W - 2 * cm, 1.45 * cm); c.restoreState()


def cover(c, d):
    c.saveState(); c.setFillColor(NAVY); c.rect(0, Hh - 6.0 * cm, W, 6.0 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white); c.setFont("BB", 24)
    c.drawString(2 * cm, Hh - 2.8 * cm, "Guía para el buscador de coches")
    c.setFont("B", 12.5); c.setFillColor(colors.HexColor("#c9d6e6"))
    c.drawString(2 * cm, Hh - 3.9 * cm, "Qué coche buscar en Alemania, a qué precio y cuándo avisar")
    c.setFont("B", 9.5)
    c.drawString(2 * cm, Hh - 5.0 * cm, "Importación a Marbella · Noviembre de 2026")
    c.restoreState(); on_page(c, d)


doc = BaseDocTemplate(OUT, pagesize=A4, title="Guía para el buscador de coches", author="Estudio de mercado")
doc.addPageTemplates([
    PageTemplate(id="cover", frames=[Frame(2 * cm, 1.9 * cm, 17 * cm, Hh - 6.0 * cm - 2.3 * cm, leftPadding=0, rightPadding=0)], onPage=cover),
    PageTemplate(id="body", frames=[Frame(2 * cm, 1.9 * cm, 17 * cm, Hh - 3.6 * cm, leftPadding=0, rightPadding=0)], onPage=on_page)])
S = [NextPageTemplate("body")]

# ---- 1. El planteamiento
S.append(Paragraph("El planteamiento en cuatro líneas", H2))
S += bullets([
    "<b>Tú buscas, yo invierto.</b> Tú localizas en Alemania el coche concreto que cumple las condiciones de esta guía; yo pongo el dinero para comprarlo, operación a operación.",
    "<b>No compramos coches de un modelo: compramos gangas.</b> A precio normal de mercado esto deja entre un 0 % y un 3 % y no interesa. Solo interesa el coche que se pueda comprar <b>entre un 11 % y un 16 % por debajo</b> de lo que cuesta de media en Alemania.",
    "<b>El objetivo es ganar al menos un 10 % por coche</b> (unos 5.000 € limpios en un coche de 50.000 €). Por debajo de eso no compensa el riesgo de averías ni el tiempo.",
    "<b>Habrá pocos.</b> Lo normal es descartar casi todos los anuncios. Un aviso al mes que cumpla todo vale más que diez que no cumplen."])
S.append(Paragraph("Cuándo avisarme", H2))
S.append(box(
    "<b>Avísame solo si el coche pasa los cinco filtros de la página 3 y el precio anunciado está dentro de la columna «Avisar si piden hasta» de la página 2.</b> "
    "Esa columna deja un 5 % de margen para negociar; el precio final de compra nunca puede superar el «tope de compra».", bg=G_BG, border=colors.HexColor("#9ccfb0")))
S.append(Paragraph("Por qué el listón es el 10 %", H2))
rows = [["Rentabilidad por coche", "En un coche de 50.000 €", "Qué hacemos"],
        [f"<font color='{R_TX}'><b>Mala: menos del 5 %</b></font>", "Menos de 2.500 €", f"<font color='{R_TX}'><b>No se compra. No hace falta avisar.</b></font>"],
        [f"<font color='{A_TX}'><b>Media: del 5 % al 10 %</b></font>", "De 2.500 € a 5.000 €", f"<font color='{A_TX}'><b>Solo si se puede negociar hasta el tope</b></font>"],
        [f"<font color='{G_TX}'><b>Buena: 10 % o más</b></font>", "5.000 € o más", f"<font color='{G_TX}'><b>Avisar enseguida</b></font>"]]
S.append(tbl(rows, [5.2 * cm, 4.2 * cm, 7.6 * cm], zebra=False,
             extra=[("BACKGROUND", (0, 1), (-1, 1), R_BG), ("BACKGROUND", (0, 2), (-1, 2), A_BG), ("BACKGROUND", (0, 3), (-1, 3), G_BG)]))
S.append(Spacer(1, 6))
S.append(Paragraph(
    "Una avería en garantía cuesta unos 1.000 € y cada mes que el coche tarda en venderse pierde 500–600 € de valor. "
    "Con 5.000 € de beneficio previsto se puede absorber un imprevisto y seguir ganando; con 2.000 € no.", P))
S.append(Paragraph("De dónde sale el beneficio", H2))
S.append(Paragraph(
    "El precio de venta lo marca el mercado español y los costes son casi fijos: unos 1.400 € de viaje (avión de ida y vuelta por carretera, 2.269 km) "
    "y 1.250 € en España (matriculación, garantía y preparación), más el IVA sobre la diferencia. "
    "<b>Lo único que podemos mover es el precio de compra:</b> cada 1.000 € que se rebajan en Alemania son unos 830 € más de beneficio.", P))
S.append(Spacer(1, 6))
S.append(box(
    "<b>Aviso.</b> Los topes de esta guía salen de precios medios de anuncios y de estimaciones, no de ventas reales. Antes de cada compra se comprueba "
    "a cuánto se anuncia ese mismo coche en España; si es menos de lo previsto, el tope baja."))
S.append(PageBreak())

# ---- 2. Coches y topes
S.append(Paragraph("Los coches que buscamos y su precio máximo", H1))
S.append(Paragraph("Por orden de prioridad. El tope es el precio de compra final para ganar un 10 %.", SUB))
for i, v in enumerate(VEH, start=1):
    img = Image(os.path.join(A, v["img"]), width=5.4 * cm, height=3.6 * cm)
    left = Table([[Paragraph(f"<b>{i}. {v['nombre']}</b>", ParagraphStyle("vn", parent=P, fontSize=10.5, leading=13, textColor=NAVY))],
                  [img], [Paragraph(v["nota"], ParagraphStyle("vx", parent=P, fontSize=8.6, leading=11.6))]], colWidths=[5.7 * cm])
    left.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    t = Table([[left, tabla_topes(v)]], colWidths=[6.0 * cm, 11.0 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    S.append(t)
S.append(Paragraph(
    "Para kilometrajes intermedios, usar la fila de más kilómetros. Fotos ilustrativas del modelo: Charles (Port Chester, NY), CC BY 2.0, y Alexandre Prevot, CC BY-SA 2.0, vía Wikimedia Commons. "
    "El ajuste por kilómetros (800 € cada 10.000 km) es una estimación.", SMALL))
S.append(PageBreak())

# ---- 3. Filtros y búsqueda
S.append(Paragraph("Los cinco filtros y cómo buscar", H1))
S.append(Paragraph("Si un coche falla en uno solo de los filtros, se descarta sin avisar.", SUB))
rows = [["", "Filtro", "Cómo comprobarlo", "Por qué"],
        ["1", "<b>Híbrido enchufable</b>, CO2 inferior a 120 g/km", "Certificado de conformidad (COC) o ficha del anuncio", "Paga 0 % de impuesto de matriculación; un coche de 200 g/km paga hasta 7.000 €."],
        ["2", "<b>Vendedor particular o «§25a»</b>", "El anuncio dice «Privatanbieter» o «differenzbesteuert»", "El IVA en España se paga solo sobre el margen."],
        ["3", "<b>Precio dentro de la tabla</b>", "Página 2, según año y kilómetros", "Por encima no se llega al 10 %."],
        ["4", "<b>Historial limpio</b>", "«Unfallfrei», «scheckheftgepflegt», 1–2 dueños", "Respondemos un año por las averías ante el comprador."],
        ["5", "<b>Más de 6 meses y de 6.000 km</b>", "Fecha de primera matriculación y kilómetros", "Si no, cuenta como coche nuevo y paga el 21 % de IVA."]]
S.append(tbl(rows, [0.8 * cm, 4.6 * cm, 5.2 * cm, 6.4 * cm], pad=3.0))
S.append(Paragraph("La excepción es la Clase V, que no es híbrida: vale solo con CO2 inferior a 200 g/km y su tope ya descuenta el impuesto.", SMALL))
S.append(Paragraph("Dónde y cómo buscar", H2))
S += bullets([
    "<b>Portales:</b> mobile.de y AutoScout24.de. Guardar una búsqueda por modelo con el precio máximo de la columna de aviso y activar las alertas.",
    "<b>Vendedores particulares</b> (filtro «Privatanbieter»): suelen ser más baratos y con prisa por vender.",
    "<b>Anuncios con más de 60–90 días publicados:</b> el concesionario tiene dinero parado y acepta rebajas, sobre todo a fin de mes.",
    "<b>Ser rápido:</b> las buenas unidades duran horas o pocos días. Llamar el mismo día y pedir los papeles.",
    "<b>Otros modelos que también valen</b> si pasan los filtros: BMW X5 xDrive45e y Mercedes GLC 300 e / 300 de. Su tope se calcula con la fórmula de abajo."])
F = ParagraphStyle("f", parent=P, fontName="BB", fontSize=11.5, leading=16, alignment=1, textColor=NAVY)
S.append(box("Tope de compra = precio de venta realista en España × 0,89 − 3.150 €<br/>"
             "<font size=8.6 color='#5b6470'>Precio de venta realista = media de anuncios del mismo coche en coches.net, menos un 3 %.</font>", bg=LIGHT, border=LINE, style=F))
S.append(Paragraph("Palabras alemanas que hay que conocer", H2))
rows = [["En el anuncio", "Significa", "¿Vale?"],
        ["Privatanbieter / differenzbesteuert (§25a)", "Vendedor particular / régimen de margen", f"<font color='{G_TX}'><b>Sí</b></font>"],
        ["Unfallfrei · Scheckheftgepflegt", "Sin accidentes · Mantenimiento sellado", f"<font color='{G_TX}'><b>Sí</b></font>"],
        ["MwSt. ausweisbar · Nettopreis", "IVA desglosado · Precio sin IVA", f"<font color='{A_TX}'><b>Consultar antes</b></font>"],
        ["Unfallwagen · Unfallschaden · Bastlerfahrzeug", "Accidentado · Para reparar", f"<font color='{R_TX}'><b>No</b></font>"],
        ["Nur Export · Nur Gewerbe · Im Kundenauftrag", "Se vende sin ninguna garantía", f"<font color='{R_TX}'><b>No</b></font>"],
        ["Erstzulassung (EZ) · Vorbesitzer · HU", "Primera matriculación · Dueños anteriores · ITV alemana", "Datos a anotar"]]
S.append(tbl(rows, [6.6 * cm, 7.0 * cm, 3.4 * cm], pad=2.6))
S.append(PageBreak())

# ---- 4. Ficha de aviso
S.append(Paragraph("Qué mandarme en cada aviso", H1))
S.append(Paragraph("Con estos datos puedo decidir en 24 horas. Si falta alguno, se pide al vendedor antes de avisar.", SUB))
rows = [["Dato", "Qué anotar"],
        ["Enlace del anuncio", "Y cuántos días lleva publicado"],
        ["Modelo exacto y versión", "Por ejemplo: GLE 350 de 4MATIC AMG Line"],
        ["Primera matriculación y kilómetros", "Mes y año; kilómetros actuales"],
        ["Precio anunciado", "Y si el vendedor acepta negociar"],
        ["Tipo de vendedor e IVA", "Particular, concesionario §25a o IVA desglosado"],
        ["CO2 (g/km)", "Del certificado de conformidad; confirmar que el vendedor lo tiene"],
        ["Historial", "Número de dueños, «unfallfrei» por escrito, libro de mantenimiento, 2 llaves"],
        ["ITV alemana (HU)", "Fecha de caducidad: sin ITV en vigor no hay placas de exportación"],
        ["Equipamiento y estado", "Extras principales, neumáticos, daños visibles, fotos"],
        ["Ciudad", "Y aeropuerto más cercano"],
        ["<b>Comparación en España</b>", "<b>2 o 3 anuncios del mismo coche en coches.net</b> (mismo año, kilómetros parecidos) con su precio"],
        ["<b>La cuenta</b>", "Tope de la tabla para ese año y kilómetros, y cuánto habría que rebajar"]]
S.append(tbl(rows, [5.6 * cm, 11.4 * cm], pad=3.0))
S.append(Paragraph("Qué pasa después del aviso", H2))
rows = [["Paso", "Qué se hace", "Quién"],
        ["1", "Revisar los datos y decidir si se sigue adelante, en 24 horas", "Inversor"],
        ["2", "Pedir número de bastidor y fotos de los papeles; informe de historial e inspección independiente (TÜV, DEKRA o ADAC)", "Buscador"],
        ["3", "Negociar hasta el tope. Si el vendedor no baja, se deja", "Buscador, con el tope acordado"],
        ["4", "Señal solo contra contrato firmado y a una cuenta a nombre del vendedor; pago por transferencia", "Inversor"],
        ["5", "Viaje, placas de exportación y vuelta por carretera (4 días)", "A acordar"],
        ["6", "Matriculación en España (2 a 6 semanas) y venta", "A acordar"]]
S.append(tbl(rows, [1.5 * cm, 11.3 * cm, 4.2 * cm], pad=3.0))
S.append(Paragraph("Lo que nunca se hace", H2))
S += bullets([
    "Pagar una señal antes de ver el coche y los papeles, o a una cuenta que no esté a nombre del vendedor.",
    "Comprar por encima del tope «porque el coche es muy bonito».",
    "Comprar sin certificado de conformidad, sin libro de mantenimiento o con kilómetros que no cuadran.",
    "Fiarse de un precio muy por debajo de todos los demás: casi siempre es una estafa o un coche accidentado."])
S.append(Spacer(1, 4))
S.append(box(
    "<b>Pendiente de acordar entre nosotros:</b> cómo se reparte el beneficio de cada operación, quién paga los gastos de búsqueda e inspección si el coche "
    "al final no se compra, quién hace el viaje y a nombre de quién se compra y se vende el coche (hay que consultarlo con un asesor fiscal)."))

# ---- Qué es real y qué falta por comprobar
S.append(PageBreak())
S.append(Paragraph("Qué es real y qué falta por comprobar", H1))
S.append(Paragraph("La lógica es sólida, pero las cifras no están verificadas y nadie ha comprobado todavía que existan coches a estos precios.", SUB))
OKc, NOc = f"<font color='{G_TX}'><b>Sólido</b></font>", f"<font color='{R_TX}'><b>Sin comprobar</b></font>"
rows = [["Qué", "Estado", "Detalle"],
        ["La cuenta del beneficio", OKc, "Venta − compra − IVA sobre el margen − costes. Es aritmética: funciona con cualquier precio real que se le meta."],
        ["Los kilómetros de la ruta", OKc, "2.269 km de Stuttgart a Marbella, calculados con un planificador de rutas."],
        ["Los tramos del impuesto de matriculación", OKc, "0 % hasta 120 g/km y 14,75 % desde 200 g/km: coinciden varias fuentes."],
        ["Los precios de compra y de venta", NOc, "Son medias de anuncios de un agregador, no anuncios reales de mobile.de ni de coches.net. Y un precio de anuncio no es un precio de venta."],
        ["El ajuste por kilómetros", NOc, "800 € cada 10.000 km es una estimación."],
        ["Costes del viaje, garantía y preparación", NOc, "En parte estimados; faltan presupuestos reales."],
        ["Fichas técnicas y consejos de búsqueda", NOc, "Datos de referencia sin fuente contrastada: manda la documentación de cada coche."],
        ["La parte fiscal", NOc, "IVA sobre el margen y forma jurídica, sin validar por un asesor."]]
ex = [("BACKGROUND", (1, i), (1, i), G_BG) for i in (1, 2, 3)] + [("BACKGROUND", (1, i), (1, i), R_BG) for i in (4, 5, 6, 7, 8)]
S.append(tbl(rows, [4.7 * cm, 3.1 * cm, 9.2 * cm], zebra=False, pad=2.0, extra=ex))
S.append(Paragraph("¿Es rentable? ¿Es posible encontrar coches así?", H2))
S += bullets([
    "<b>Rentable, solo con una condición:</b> comprar entre un 11 % y un 16 % por debajo de la media alemana. A precio normal deja entre un 0 % y un 3 %.",
    "<b>No se sabe si esos coches existen en cantidad suficiente.</b> Un coche sano tan por debajo de mercado es raro: los profesionales alemanes y los importadores que ya hacen esto vigilan los mismos anuncios y llegan antes.",
    "<b>Muchos de los que aparecen tan baratos tienen un motivo:</b> accidente, historial dudoso, IVA no incluido o estafa.",
    "<b>Puede haber excepciones</b> (un particular con prisa, un coche con meses publicado), pero no hay datos de su frecuencia."])
S.append(Paragraph("La prueba antes de poner dinero: tres o cuatro semanas sin comprar", H2))
rows = [["Paso", "Qué hacer"],
        ["1", "Poner alertas en mobile.de y AutoScout24 con los precios de la columna «avisar si piden hasta» de cada modelo."],
        ["2", "Anotar cada coche que aparezca y pase los cinco filtros: fecha, enlace, año, kilómetros, precio pedido y tope de la tabla."],
        ["3", "Buscar ese mismo coche en coches.net (mismo año, kilómetros parecidos) y anotar a cuánto se anuncia en España."],
        ["4", "Al terminar, contar cuántos coches válidos han salido y rehacer los topes con los precios reales."]]
S.append(tbl(rows, [1.5 * cm, 15.5 * cm], pad=2.0))
S.append(Spacer(1, 6))
S.append(box(
    "<b>Cómo leer el resultado.</b> Si en un mes no aparece ningún coche válido, el planteamiento no es viable y no se ha perdido nada. "
    "Si aparecen, se hace <b>una sola compra piloto</b> con el de menor riesgo (un híbrido enchufable, que paga 0 % de impuesto de matriculación) "
    "y se decide si continuar con los números reales de esa operación.", bg=G_BG, border=colors.HexColor("#9ccfb0")))

S.append(PageBreak())
S.append(Paragraph("Registro de la prueba", H1))
S.append(Paragraph("Una fila por cada coche que aparezca dentro de precio. Al terminar el mes, se cuentan los que pasan los cinco filtros.", SUB))
rows = [["Fecha", "Modelo, año y km", "Precio pedido", "Tope", "¿Pasa los 5 filtros?", "Precio en España"]] + [[""] * 6 for _ in range(18)]
S.append(tbl(rows, [2.0 * cm, 5.0 * cm, 2.6 * cm, 2.2 * cm, 2.7 * cm, 2.5 * cm], zebra=False, pad=6.5,
             extra=[("GRID", (0, 0), (-1, -1), 0.4, LINE)]))

doc.build(S)
print("OK")
