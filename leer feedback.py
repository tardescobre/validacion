import pandas as pd
import unicodedata

def normalizar_texto(texto):
    if pd.isna(texto):
        return texto
    texto = str(texto).strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto)
                    if unicodedata.category(c) != 'Mn')
    return texto

# Lista de URLs raw de GitHub
urls = [
    "https://raw.githubusercontent.com/tardescobre/validacion/main/feedback1.csv",
    "https://raw.githubusercontent.com/tardescobre/validacion/main/feedback2.csv",
    "https://raw.githubusercontent.com/tardescobre/validacion/main/feedback3.csv",
    "https://raw.githubusercontent.com/tardescobre/validacion/main/feedback4.csv",
    "https://raw.githubusercontent.com/tardescobre/validacion/main/feedback5.csv",
    "https://raw.githubusercontent.com/tardescobre/validacion/main/feedback6.csv",
    "https://raw.githubusercontent.com/tardescobre/validacion/main/feedback7.csv"
]

dfs = []

for url in urls:
    try:
        df = pd.read_csv(url, sep=None, engine='python', encoding='utf-8')
        df.columns = [normalizar_texto(c) for c in df.columns]
        if 'nombre_profesional' in df.columns:
            df['nombre_profesional'] = df['nombre_profesional'].apply(normalizar_texto)
        dfs.append(df)
    except Exception as e:
        print(f"No se pudo leer {url}: {e}")

# Combinar y eliminar duplicados
df_combinado = pd.concat(dfs, ignore_index=True, sort=False).drop_duplicates()

# Guardar localmente
df_combinado.to_csv("feedback_combinado_corregido.csv", index=False, encoding="utf-8")

print(f"✅ Archivo generado: feedback_combinado_corregido.csv")
print(f"Total de filas: {df_combinado.shape[0]}  |  Columnas: {df_combinado.shape[1]}")

