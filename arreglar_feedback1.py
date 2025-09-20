import pandas as pd

# Leer con latin-1 para manejar encoding corrupto
df = pd.read_csv('feedback1.csv', encoding='latin-1', dtype=str, keep_default_na=False)

print("Columnas originales:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

# Mapear a estructura estándar
cols_std = [
    'nombre_profesional',
    'utilidad', 
    'eficiencia',
    'intencion_uso',
    'satisfaccion_claridad',
    'satisfaccion_diseño', 
    'modificar_secciones',
    'comentarios',
    'fecha_envio',
    'cedula_profesional',
    'profesion_profesional'
]

df_std = pd.DataFrame(columns=cols_std)

# Mapear datos
df_std['nombre_profesional'] = df['nombre_profesional']
df_std['utilidad'] = df['utilidad'] 
df_std['eficiencia'] = df['eficiencia']
df_std['intencion_uso'] = df['intencion_uso']
df_std['satisfaccion_claridad'] = df['satisfaccion_claridad']

# Buscar la columna de diseño (puede estar corrupta)
col_diseno = None
for col in df.columns:
    if 'diseÃ' in col or 'diseño' in col or 'diseno' in col:
        col_diseno = col
        break

if col_diseno:
    df_std['satisfaccion_diseño'] = df[col_diseno]
else:
    df_std['satisfaccion_diseño'] = ''

df_std['modificar_secciones'] = df['modificar_secciones']
df_std['comentarios'] = df['comentarios'] 
df_std['fecha_envio'] = df['fecha_envio']
df_std['cedula_profesional'] = df['cedula_profesional']
df_std['profesion_profesional'] = df['profesion_profesional']

# Limpiar caracteres corruptos
for col in df_std.columns:
    if df_std[col].dtype == 'object':
        df_std[col] = df_std[col].str.replace('Ã±', 'ñ', regex=False)
        df_std[col] = df_std[col].str.replace('Ã¡', 'á', regex=False) 
        df_std[col] = df_std[col].str.replace('Ã©', 'é', regex=False)
        df_std[col] = df_std[col].str.replace('Ã­', 'í', regex=False)
        df_std[col] = df_std[col].str.replace('Ã³', 'ó', regex=False)
        df_std[col] = df_std[col].str.replace('Ãº', 'ú', regex=False)

# Guardar
df_std.to_csv('feedback1.csv', index=False, encoding='utf-8-sig')
print("✅ feedback1.csv arreglado y estandarizado")