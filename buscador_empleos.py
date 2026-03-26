# pip install python-jobspy reportlab


# --- imports ---
from jobspy import scrape_jobs
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import datetime
import os


# --- input usuario ---
def obtener_input_usuario():
    print("\n========================================")
    print("   BUSCADOR DE EMPLEOS - Argentina")
    print("========================================\n")

    puesto = input("¿Qué puesto estás buscando? (ej: administrador de sistemas): ").strip()

    if not puesto:
        print("Error: tenés que ingresar un puesto.")
        exit(1)

    ubicacion = input("¿En qué ciudad/provincia? (dejá vacío para buscar en toda Argentina): ").strip()

    if not ubicacion:
        ubicacion = "Argentina"

    cantidad = input("¿Cuántos resultados querés por fuente? (default: 15): ").strip()

    try:
        cantidad = int(cantidad)
    except ValueError:
        cantidad = 15

    return puesto, ubicacion, cantidad


# --- scraping ---
def scrapear_empleos(puesto, ubicacion, cantidad):
    print(f"\n🔍 Buscando '{puesto}' en {ubicacion}...")
    print("   (esto puede tardar unos segundos)\n")

    try:
        empleos = scrape_jobs(
            site_name=["linkedin", "indeed"],
            search_term=puesto,
            location=ubicacion,
            country_indeed="Argentina",
            results_wanted=cantidad,
            hours_old=72,
            verbose=0,
        )
        return empleos

    except Exception as e:
        print(f"Error durante el scraping: {e}")
        return None


# --- limpieza de resultados ---
def limpiar_resultados(df_empleos):
    if df_empleos is None or df_empleos.empty:
        return []

    empleos_limpios = []

    for _, fila in df_empleos.iterrows():
        titulo = str(fila.get("title", "")).strip()
        url = str(fila.get("job_url", "")).strip()

        # jobspy a veces devuelve nan, hay que filtrarlo
        if not titulo or not url or titulo == "nan" or url == "nan":
            continue

        empresa = str(fila.get("company", "No disponible")).strip()
        if empresa == "nan":
            empresa = "No disponible"

        ciudad = str(fila.get("city", "")).strip()
        estado = str(fila.get("state", "")).strip()
        if ciudad == "nan": ciudad = ""
        if estado == "nan": estado = ""

        ubicacion_display = ", ".join(filter(None, [ciudad, estado])) or "No especificada"
        fuente = str(fila.get("site", "")).strip().capitalize()

        fecha = fila.get("date_posted", None)
        if fecha and str(fecha) != "nan":
            try:
                fecha_display = str(fecha)[:10]
            except:
                fecha_display = "No disponible"
        else:
            fecha_display = "No disponible"

        empleos_limpios.append({
            "titulo": titulo,
            "empresa": empresa,
            "ubicacion": ubicacion_display,
            "fuente": fuente,
            "fecha": fecha_display,
            "url": url,
        })

    return empleos_limpios


# --- generacion del pdf ---
def generar_pdf(empleos, puesto, ubicacion):
    fecha_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    nombre_archivo = f"empleos_{puesto.replace(' ', '_')}_{fecha_hora}.pdf"

    doc = SimpleDocTemplate(
        nombre_archivo,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    estilo_titulo_doc = ParagraphStyle(
        "TituloDoc",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    estilo_seccion = ParagraphStyle(
        "Seccion",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=14,
        spaceAfter=6,
    )
    estilo_titulo_empleo = ParagraphStyle(
        "TituloEmpleo",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#0f3460"),
        fontName="Helvetica-Bold",
        spaceAfter=2,
    )
    estilo_detalle = ParagraphStyle(
        "Detalle",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#444444"),
        spaceAfter=1,
    )
    estilo_url = ParagraphStyle(
        "URL",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#0066cc"),
        spaceAfter=4,
    )

    contenido = []

    contenido.append(Paragraph("🔍 Informe de Búsqueda de Empleos", estilo_titulo_doc))
    contenido.append(Paragraph(f"Puesto: <b>{puesto.title()}</b> · Ubicación: <b>{ubicacion}</b>", estilo_subtitulo))

    fecha_generacion = datetime.datetime.now().strftime("%d/%m/%Y a las %H:%M")
    contenido.append(Paragraph(f"Generado el {fecha_generacion}", estilo_subtitulo))
    contenido.append(Spacer(1, 0.3*cm))
    contenido.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a1a2e")))
    contenido.append(Spacer(1, 0.3*cm))

    total = len(empleos)
    desde_linkedin = sum(1 for e in empleos if e["fuente"].lower() == "linkedin")
    desde_indeed = sum(1 for e in empleos if e["fuente"].lower() == "indeed")

    contenido.append(Paragraph("Resumen", estilo_seccion))

    datos_resumen = [
        ["Total de empleos encontrados", str(total)],
        ["Desde LinkedIn", str(desde_linkedin)],
        ["Desde Indeed", str(desde_indeed)],
    ]

    tabla_resumen = Table(datos_resumen, colWidths=[10*cm, 4*cm])
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#e8f0fe")),
        ("BACKGROUND",    (0, 1), (-1, 1), colors.HexColor("#f9f9f9")),
        ("BACKGROUND",    (0, 2), (-1, 2), colors.HexColor("#e8f0fe")),
        ("TEXTCOLOR",     (0, 0), (-1, -1), colors.HexColor("#1a1a2e")),
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("FONTNAME",      (1, 0), (1, -1), "Helvetica-Bold"),
        ("ALIGN",         (1, 0), (1, -1), "CENTER"),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    contenido.append(tabla_resumen)

    contenido.append(Paragraph("Empleos Encontrados", estilo_seccion))

    if not empleos:
        contenido.append(Paragraph(
            "No se encontraron resultados. Probá con otro término o ubicación.",
            ParagraphStyle("SinResultados", parent=styles["Normal"], fontSize=11,
                           textColor=colors.HexColor("#888888"), alignment=TA_CENTER, spaceBefore=20)
        ))
    else:
        for i, empleo in enumerate(empleos, 1):
            contenido.append(Paragraph(f"{i}. {empleo['titulo']}", estilo_titulo_empleo))
            contenido.append(Paragraph(
                f"🏢 <b>{empleo['empresa']}</b>   📍 {empleo['ubicacion']}   📅 {empleo['fecha']}   🌐 {empleo['fuente']}",
                estilo_detalle
            ))
            contenido.append(Paragraph(
                f'<link href="{empleo["url"]}">{empleo["url"]}</link>',
                estilo_url
            ))
            if i < total:
                contenido.append(HRFlowable(width="100%", thickness=0.5,
                                            color=colors.HexColor("#dddddd"), spaceAfter=4))

    contenido.append(Spacer(1, 0.5*cm))
    contenido.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    contenido.append(Paragraph(
        "Informe generado automáticamente. Los links pueden expirar con el tiempo.",
        ParagraphStyle("Pie", parent=styles["Normal"], fontSize=8,
                       textColor=colors.grey, alignment=TA_CENTER, spaceBefore=4)
    ))

    doc.build(contenido)
    return nombre_archivo


# --- main ---
def main():
    puesto, ubicacion, cantidad = obtener_input_usuario()
    df_empleos = scrapear_empleos(puesto, ubicacion, cantidad)
    empleos = limpiar_resultados(df_empleos)

    print(f"✅ Se encontraron {len(empleos)} empleos válidos.")
    print("📄 Generando informe PDF...")

    archivo = generar_pdf(empleos, puesto, ubicacion)
    ruta_completa = os.path.abspath(archivo)

    print(f"\n✅ ¡Listo! El informe fue guardado en:")
    print(f"   {ruta_completa}\n")


if __name__ == "__main__":
    main()