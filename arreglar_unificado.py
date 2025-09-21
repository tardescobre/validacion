import pandas as pd
import os

def arreglar_validacion_unificado():
    """Arregla el archivo validacion_unificado.csv usando los CSV individuales correctos"""
    
    # Lista de archivos CSV individuales
    archivos_csv = [f for f in os.listdir('.') if f.startswith('feedback') and f.endswith('.csv')]
    archivos_csv.sort()
    
    print("ARREGLANDO validacion_unificado.csv")
    print("=" * 50)
    
    # Lista para almacenar todos los DataFrames
    dfs_unidos = []
    
    # Leer cada archivo CSV individual
    for archivo in archivos_csv:
        print(f"Procesando {archivo}...")
        
        try:
            # Leer con diferentes codificaciones
            df = None
            encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(archivo, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is not None and len(df.columns) == 11:
                dfs_unidos.append(df)
                print(f"  {archivo}: OK - {len(df)} filas agregadas")
            else:
                print(f"  {archivo}: ERROR - estructura incorrecta")
                
        except Exception as e:
            print(f"  {archivo}: ERROR - {str(e)}")
    
    # Unir todos los DataFrames
    if dfs_unidos:
        df_final = pd.concat(dfs_unidos, ignore_index=True)
        
        # Guardar el archivo unificado corregido
        df_final.to_csv('validacion_unificado.csv', 
                       index=False, 
                       encoding='utf-8-sig',
                       quoting=1)  # QUOTE_ALL para evitar problemas con comas
        
        print("=" * 50)
        print(f"ARCHIVO CORREGIDO EXITOSAMENTE!")
        print(f"Total de registros: {len(df_final)}")
        print(f"Columnas: {len(df_final.columns)}")
        print("Archivo guardado como: validacion_unificado.csv")
        
        # Mostrar primeras filas para verificar
        print("\nPrimeras 3 filas del archivo corregido:")
        print(df_final.head(3).to_string())
        
    else:
        print("ERROR: No se pudieron procesar los archivos CSV")

if __name__ == "__main__":
    arreglar_validacion_unificado()