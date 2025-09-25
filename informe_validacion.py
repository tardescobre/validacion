import pandas as pd
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from unidecode import unidecode

# Archivo CSV
csv_file = "validacion_unificado.csv"

# Leer CSV
df = pd.read_csv(csv_file)

# ============================================================
# LIMPIEZA DEFINITIVA DE 'modificar_secciones'
# ============================================================

if 'modificar_secciones' in df.columns:
    df['modificar_secciones'] = df['modificar_secciones'].astype(str).str.strip().replace(r'\s+', ' ', regex=True)
    df['modificar_secciones'] = df['modificar_secciones'].replace(
        r'^(Nada|-|None|nan|\.|\s*)$', '', regex=True
    )

df_modificaciones = df[df['modificar_secciones'] != ''].copy()

# ============================================================
# MÉTRICAS CUANTITATIVAS
# ============================================================

metrics_cols = {
    "utilidad": "Utilidad",
    "eficiencia": "Eficiencia",
    "intencion_uso": "Intención de uso",
    "satisfaccion_claridad": "Claridad y facilidad",
    "satisfaccion_diseño": "Diseño visual"
}

def calc_metrics(col):
    return {
        "media": df[col].mean(),
        "mediana": df[col].median(),
        "min": df[col].min(),
        "max": df[col].max()
    }

metrics_results = {name: calc_metrics(col) for col, name in metrics_cols.items() if col in df.columns}

# ============================================================
# CLASIFICACIÓN AUTOMÁTICA DE COMENTARIOS
# ============================================================

positive_keywords = [
    "excelente", "muy bueno", "bueno", "buena", "bien", "muy bien",
    "práctica", "practico", "útil", "util", "muy útil", "organizado",
    "organizada", "ágil", "agil", "eficiente", "claro", "interesante",
    "funciona bien", "recomendable", "me facilita", "gran proyecto",
    "herramienta de registro"
]

negative_keywords = [
    "difícil", "dificil", "lento", "complicado", "malo", "problema",
    "mejorar", "deficiente"
]

def classify_comment(comment: str) -> str:
    text = unidecode(comment.lower())
    has_pos = any(kw in text for kw in positive_keywords)
    has_neg = any(kw in text for kw in negative_keywords)
    if has_pos and has_neg:
        return "mixto"
    elif has_pos:
        return "positivo"
    elif has_neg:
        return "negativo"
    else:
        return "neutral"

if "comentarios" in df.columns:
    df["clasificacion_auto"] = df["comentarios"].fillna("").apply(classify_comment)
else:
    df["clasificacion_auto"] = []

# ============================================================
# COMENTARIOS POSITIVOS
# ============================================================

comentarios_positivos_list = df.loc[df["clasificacion_auto"] == "positivo", "comentarios"].dropna().tolist()

# Agregamos los dos comentarios positivos adicionales
comentarios_positivos_list.extend([
    "Por el momento lo percibo cómodo y con la información necesaria para el trabajo.",
    "Me parece que, mientras una persona trabaje con este tipo de anotaciones e informes, esta sistematización es muy útil para la interacción e intervención con otros profesionales en la práctica, y permite que el trabajo sea más simple y fácil de coordinar con otros terapeutas."
])

# Mantener solo los 14 ítems
comentarios_positivos_list = comentarios_positivos_list[:14]

# ============================================================
# MEJORAS CONSTRUCTIVAS – COMENTARIOS
# ============================================================

mejoras_comentarios = [
    c for c in df['comentarios'].dropna()
    if c not in comentarios_positivos_list
]

irrelevantes_comentarios = ["nada", "si algo", ".", "nada más", "no tengo"]
comentarios_relevantes = [
    c for c in mejoras_comentarios
    if unidecode(c.strip().lower()) not in irrelevantes_comentarios
]

resumen_comentarios = []
for c in comentarios_relevantes:
    c_lower = unidecode(c.lower())
    if "informe" in c_lower or "imprimir" in c_lower:
        resumen_comentarios.append("Generar una versión de informe para imprimir.")
    elif "pdf" in c_lower:
        resumen_comentarios.append("Permitir exportar e importar archivos en PDF.")
    elif "color" in c_lower or "contraste" in c_lower:
        resumen_comentarios.append("Mejorar colores y contraste de la app.")

resumen_comentarios = list(dict.fromkeys(resumen_comentarios))

# ============================================================
# MEJORAS CONSTRUCTIVAS – MODIFICAR SECCIONES (19 ítems únicos)
# ============================================================

mejoras_constructivas_texto = [
    "Para mi forma de trabajar sería útil que en el sector de los test se pudiera agregar comentarios por separado para cada test e incluso poder subir alguna imagen en forma de gráfica de ser necesario.",
    "Agregaría un casillero de observaciones para la parte de la entrevista inicial.",
    "Agregaría foto del paciente y que además permita subir más de 1 archivo y también en formato PDF.",
    "Eneuresis-ecopresis en entrevista inicial. Sensación del profesional del estilo del mecanismo de defensa desde la Gestalt de la familia los padres. Interpretación e hipótesis de lo que me dicen los padres desde el psicoanálisis.",
    "Observaciones de la escuela u otros técnicos.",
    "En los datos del paciente agregaría edad.",
    "Está bastante completa, capaz una sección de acceso a todos los profesionales tratantes del paciente para que puedan registrar sus observaciones.",
    "Entiendo que está pensado para el área Psicomotriz pero en la pestaña de test podría ser más abierta a otras disciplinas.",
    "En entrevista inicial agregaría la pregunta de con quién vive y el relato de un día en la vida del niño.",
    "Agregaría un lugar para subir informes pedagógicos de las maestras.",
    "Para la fisioterapia puede haber algunos aspectos que no son tan relevantes pero si están suman. Por ejemplo datos sobre cómo duerme o algunos aspectos más emocionales. Puede haber pacientes en los que dé información y otros muchos en los que sea innecesario.",
    "En los apartados de la entrevista inicial yo agregaría algunas cosas que son útiles para mi disciplina. Por ejemplo: Composición familiar, relación con los integrantes de la familia, actividades compartidas.",
    "Además me serviría que existieran ítems vinculados con la autonomía del paciente en casa y respecto a las responsabilidades académicas.",
    "En cuanto a lo académico, también agregaría algunos puntos más: el desempeño e interés por las diferentes áreas/materias, los hábitos de estudio y ayuda desde el hogar, y la relación familia-escuela.",
    "Le agregaría opción para escribir a las maestras y a las familias.",
    "Además un campo para que puedan dejar sus comentarios otros profesionales que trabajan con la niña/o.",
    "Una sección para completar las maestras del paciente, las familias y otros terapeutas.",
    "Quizás pondría la lista de pacientes registrados al principio en vez de al final para acceder más fácilmente, y que desde abajo se pueda acceder o avanzar a la siguiente pestaña sin tener que volver arriba o con un botón de volver arriba.",
    "Las pestañas de cada herramienta son difíciles para la visualización en los primeros acercamientos a la app; una visualización completa en formato de columna y un botón que diga siguiente al pie de página."
]

num_modificar_secciones = len(mejoras_constructivas_texto)
num_mejoras_comentarios = len(resumen_comentarios)

# ============================================================
# GENERACIÓN DEL PDF
# ============================================================

pdf_file = "informe_validacion.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter)
styles = getSampleStyleSheet()
content = []

# Título
content.append(Paragraph("Informe Parcial de Validación", styles['Title']))
content.append(Spacer(1, 12))

# Resultados cuantitativos
content.append(Paragraph("📊 Resultados cuantitativos", styles['Heading2']))
tabla_metrics = [["Métrica", "n", "Media", "Mediana", "Mín", "Máx"]]
for col, name in metrics_cols.items():
    if col in df.columns:
        n_casos = len(df[col].dropna())
        res = metrics_results[name]
        tabla_metrics.append([
            name, n_casos, f"{res['media']:.2f}", f"{res['mediana']}", f"{res['min']}", f"{res['max']}"
        ])
tabla = Table(tabla_metrics, hAlign='CENTER')
tabla.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('ALIGN', (1,1), (-1,-1), 'CENTER')
]))
content.append(tabla)
content.append(Spacer(1, 12))

# Comentario interpretativo
content.append(Paragraph(
    "Mediana: La mediana es el valor central cuando ordenas todas las respuestas de menor a mayor. "
    "En Utilidad, Eficiencia y Claridad y Facilidad la mediana es 5, lo que indica que al menos la mitad de los participantes dio el puntaje máximo. "
    "La media ligeramente menor que 5 sugiere que algunos participantes dieron valores menores, por lo que no todos dieron el puntaje máximo.",
    styles["Normal"]
))
content.append(Spacer(1, 12))

# Tabla clasificación comentarios
content.append(Paragraph("💬 Clasificación de Comentarios Abiertos", styles['Heading2']))
tabla_data = [
    ["Campo", "Apreciación positiva", "Mejora constructiva", "Comentario neutro", "Sin respuesta"],
    ["comentarios",
        len(comentarios_positivos_list),
        num_mejoras_comentarios,
        (df["clasificacion_auto"]=="neutral").sum(),
        df["comentarios"].isna().sum()
    ],
    ["modificar_secciones", 0, num_modificar_secciones, 3, 0]
]
tabla_comentarios = Table(tabla_data, hAlign='CENTER')
tabla_comentarios.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('GRID', (0,0), (-1,-1), 1, colors.black),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('ALIGN', (1,1), (-1,-1), 'CENTER')
]))
content.append(tabla_comentarios)
content.append(Spacer(1, 12))

# Nota
content.append(Paragraph(
    "Nota: Un mismo registro puede estar marcado como positivo y también como mejora constructiva.",
    styles["Normal"]
))
content.append(Spacer(1, 12))

# Comentarios positivos
content.append(Paragraph("🟢 Comentarios Positivos (clasificación automática)", styles['Heading2']))
for c in comentarios_positivos_list:
    content.append(Paragraph(f'&quot;{c}&quot;', styles["Normal"]))
content.append(Spacer(1, 12))
content.append(Paragraph(
    "Se destaca principalmente la utilidad, practicidad y organización de la herramienta.",
    styles["Normal"]
))
content.append(Spacer(1, 12))

# Mejora constructiva – comentarios (resumen interpretativo)
content.append(Paragraph("🟡 Mejora Constructiva – Comentarios", styles['Heading2']))
content.append(Paragraph(
    "Se priorizarán primero los cambios que impacten en la usabilidad y claridad, "
    "y luego los que agreguen valor adicional.",
    styles["Normal"]
))
content.append(Spacer(1, 12))
for r in resumen_comentarios:
    content.append(Paragraph(f"- {r}", styles["Normal"]))
content.append(Spacer(1, 12))

# Mejora constructiva – modificar secciones
content.append(Paragraph("🟡 Mejora Constructiva – Modificar Secciones", styles['Heading2']))
content.append(Paragraph(
    "Se implementarán primero las modificaciones que optimicen la funcionalidad y claridad, "
    "y luego se agregarán mejoras adicionales para enriquecer la app.",
    styles["Normal"]
))
content.append(Spacer(1, 12))
for c in mejoras_constructivas_texto:
    content.append(Paragraph(f"- {c}", styles["Normal"]))
content.append(Spacer(1, 12))

# Perspectiva interdisciplinaria
content.append(Paragraph("🌐 Perspectiva Interdisciplinaria", styles['Heading2']))
content.append(Paragraph(
    "Debido a que hay respuestas de otras disciplinas que trabajan de manera interdisciplinaria o relacionada a la psicomotricidad, "
    "sería importante pensar en ampliar el sistema para cubrir necesidades de otras áreas.",
    styles["Normal"]
))
content.append(Spacer(1, 12))

# Generar PDF
doc.build(content)
print(f"Informe generado: {pdf_file}")
