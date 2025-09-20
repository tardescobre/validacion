import pandas as pd
import os
from pathlib import Path

def verificar_estructura_csv(archivo_path):
    """
    Verifica si un CSV tiene la estructura correcta
    """
    try:
        df = pd.read_csv(archivo_path, dtype=str)
        
        # Estructura esperada
        columnas_esperadas = [
            'nombre_profesional', 'utilidad', 'eficiencia', 'intencion_uso',
            'satisfaccion_claridad', 'satisfaccion_diseño', 'modificar_secciones',
            'comentarios', 'fecha_envio', 'cedula_profesional', 'profesion_profesional'
        ]
        
        problemas = []
        
        # 1. Verificar número de columnas
        if len(df.columns) != len(columnas_esperadas):
            problemas.append(f"❌ Columnas incorrectas: tiene {len(df.columns)}, esperaba {len(columnas_esperadas)}")
        
        # 2. Verificar nombres de columnas
        for col in columnas_esperadas:
            if col not in df.columns:
                problemas.append(f"❌ Falta columna: {col}")
        
        # 3. Verificar si se puede leer correctamente
        if df.empty:
            problemas.append("⚠️ Archivo vacío (solo headers)")
        else:
            # Verificar filas problemáticas
            for i, row in df.iterrows():
                if row.isna().all():
                    problemas.append(f"❌ Fila {i+2} completamente vacía")
                elif len([x for x in row if pd.notna(x) and str(x).strip()]) < 5:
                    problemas.append(f"⚠️ Fila {i+2} tiene pocos datos válidos")
        
        # 4. Verificar encoding
        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            if 'Ã' in contenido:
                problemas.append("⚠️ Posible problema de encoding (caracteres Ã)")
        except:
            problemas.append("⚠️ Problema de encoding detectado")
        
        if not problemas:
            return True, [f"✅ {os.path.basename(archivo_path)}: Estructura correcta ({len(df)} filas)"]
        else:
            return False, [f"📄 {os.path.basename(archivo_path)}:"] + problemas
            
    except Exception as e:
        return False, [f"❌ {os.path.basename(archivo_path)}: Error leyendo archivo - {e}"]

def auditar_todos_los_csv():
    """
    Audita todos los CSV de feedback
    """
    archivos = ['feedback1.csv', 'feedback2.csv', 'feedback3.csv', 'feedback4.csv', 
               'feedback5.csv', 'feedback6.csv', 'feedback7.csv']
    
    print("🔍 AUDITORÍA DE ESTRUCTURA CSV")
    print("=" * 50)
    
    todos_ok = True
    for archivo in archivos:
        if os.path.exists(archivo):
            ok, mensajes = verificar_estructura_csv(archivo)
            for msg in mensajes:
                print(msg)
            if not ok:
                todos_ok = False
        else:
            print(f"❌ {archivo}: No encontrado")
            todos_ok = False
    
    print("=" * 50)
    if todos_ok:
        print("🎉 ¡TODOS LOS CSV TIENEN ESTRUCTURA CORRECTA!")
        print("📊 Listos para mostrar como tablas en GitHub")
    else:
        print("⚠️ Algunos CSV necesitan corrección")
        print("💡 Ejecuta el script de corrección correspondiente")
    
    return todos_ok

if __name__ == "__main__":
    auditar_todos_los_csv()