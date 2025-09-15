import csv
import pandas as pd

# ----------------------------
# 1. Leer feedback1 con csv.reader
# ----------------------------
feedback1_rows = []
with open('feedback1.csv', 'r', encoding='cp1252', newline='') as f:  # cp1252 suele manejar acentos en Windows
    reader = csv.reader(f, delimiter=',', quotechar='"', doublequote=True)
    for row in reader:
        feedback1_rows.append(row)

# Convertir a DataFrame
df1 = pd.DataFrame(feedback1_rows[1:], columns=feedback1_rows[0])  # primera fila como header

# ----------------------------
# 2. Leer feedback2 con pandas normalmente
# ----------------------------
df2 = pd.read_csv('feedback2.csv', encoding='utf-8', dtype=str)

# ----------------------------
# 3. Asegurar que ambos DataFrames tengan las mismas columnas
# ----------------------------
for col in df1.columns:
    if col not in df2.columns:
        df2[col] = pd.NA

for col in df2.columns:
    if col not in df1.columns:
        df1[col] = pd.NA

df2 = df2[df1.columns]

# ----------------------------
# 4. Combinar ambos DataFrames
# ----------------------------
df_combinado = pd.concat([df1, df2], ignore_index=True)

# ----------------------------
# 5. Guardar CSV final
# ----------------------------
df_combinado.to_csv('feedback_combinado.csv', index=False, encoding='utf-8-sig')
print("CSV combinado generado correctamente: feedback_combinado.csv\n")

# ----------------------------
# 6. Resumen automático del feedback
# ----------------------------
print("----- RESUMEN DEL FEEDBACK -----\n")

# Número de respuestas por profesional
if 'nombre_profesional' in df_combinado.columns:
    print("Número de respuestas por profesional:")
    print(df_combinado['nombre_profesional'].value_counts())
    print("\n")

# Promedio de intención de uso
if 'utilidad' in df_combinado.columns:
    df_combinado['utilidad'] = pd.to_numeric(df_combinado['utilidad'], errors='coerce')
    print(f"Promedio de intención de uso: {df_combinado['utilidad'].mean():.2f}\n")

# Distribución de respuestas cualitativas
if 'utilidad_opcion' in df_combinado.columns:
    print("Distribución de respuestas cualitativas:")
    print(df_combinado['utilidad_opcion'].value_counts())
    print("\n")

# Comentarios vacíos
comentarios_cols = ['observaciones', 'comentarios']  # ajustar según tu CSV
total_vacios = 0
for col in comentarios_cols:
    if col in df_combinado.columns:
        total_vacios += df_combinado[col].isna().sum()
print(f"Total de comentarios vacíos: {total_vacios}\n")

# Filas con valores faltantes en columnas clave
columnas_clave = ['nombre_profesional', 'utilidad', 'utilidad_opcion']
faltantes = df_combinado[columnas_clave].isna().sum()
print("Filas con valores faltantes en columnas clave:")
print(faltantes)
