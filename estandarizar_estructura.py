import pandas as pd
import os
from pathlib import Path

# Estructura estándar basada en feedback3 y feedback5
COLUMNAS_ESTANDAR = [
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

def estandarizar_csv(archivo_path):
    """Convierte CSV a estructura estándar"""
    try:
        # Leer con encoding robusto
        df = pd.read_csv(archivo_path, encoding='utf-8-sig', dtype=str, keep_default_na=False)
        
        # Si está vacío, crear con headers estándar
        if df.empty:
            df_std = pd.DataFrame(columns=COLUMNAS_ESTANDAR)
        else:
            # Crear DataFrame con columnas estándar
            df_std = pd.DataFrame(columns=COLUMNAS_ESTANDAR)
            
            # Mapear datos existentes
            for col in COLUMNAS_ESTANDAR:
                if col in df.columns:
                    df_std[col] = df[col]
                else:
                    df_std[col] = ''
            
            # Limpiar encoding corrupto (ñ mal codificada)
            for col in df_std.columns:
                if df_std[col].dtype == 'object':
                    df_std[col] = df_std[col].str.replace('Sí', 'Sí', regex=False)
                    df_std[col] = df_std[col].str.replace('diseño', 'diseño', regex=False)
        
        # Guardar con estructura estándar
        df_std.to_csv(archivo_path, index=False, encoding='utf-8-sig')
        print(f"✅ {os.path.basename(archivo_path)} - Estandarizado ({len(df_std)} filas)")
        
    except Exception as e:
        print(f"❌ Error en {os.path.basename(archivo_path)}: {e}")

def main():
    base_dir = Path(__file__).parent
    archivos_csv = ['feedback1.csv', 'feedback2.csv', 'feedback4.csv', 'feedback6.csv', 'feedback7.csv']
    
    print("🔧 Estandarizando estructura de CSV...")
    print(f"📋 Estructura estándar: {len(COLUMNAS_ESTANDAR)} columnas")
    print("=" * 50)
    
    for archivo in archivos_csv:
        archivo_path = base_dir / archivo
        if archivo_path.exists():
            estandarizar_csv(archivo_path)
        else:
            print(f"⚠️  No encontrado: {archivo}")
    
    print("=" * 50)
    print("✅ Estandarización completada!")
    print("📊 Ahora todos los CSV tienen la misma estructura que feedback3 y feedback5")

if __name__ == "__main__":
    main()