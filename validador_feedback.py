import pandas as pd
import re
import os
from datetime import datetime

def validar_y_limpiar_texto(texto, campo_nombre="campo"):
    """
    Valida y limpia texto eliminando TODOS los caracteres especiales problemáticos
    """
    if not texto or pd.isna(texto):
        return ""
    
    texto = str(texto).strip()
    
    # 1. Eliminar TODOS los caracteres problemáticos para CSV
    texto = texto.replace(',', ' ')   # ELIMINAR comas (causan división)
    texto = texto.replace('"', ' ')   # ELIMINAR comillas dobles
    texto = texto.replace("'", ' ')   # ELIMINAR comillas simples
    texto = texto.replace(';', ' ')   # ELIMINAR punto y coma
    texto = texto.replace('\n', ' ')  # Saltos de línea por espacios
    texto = texto.replace('\r', ' ')  # Retornos de carro por espacios
    texto = texto.replace('\t', ' ')  # Tabs por espacios
    texto = texto.replace('|', ' ')   # Pipes
    texto = texto.replace('\\', ' ')  # Barras invertidas
    
    # 2. Espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    # 3. Validar longitud
    if len(texto) > 500:
        print(f"⚠️ Advertencia: {campo_nombre} muy largo, se truncará")
        texto = texto[:497] + "..."
    
    return texto

def validar_fila_feedback(fila_dict):
    """
    Valida una fila completa de feedback antes de guardar
    """
    errores = []
    
    # Campos obligatorios
    obligatorios = ['nombre_profesional', 'utilidad', 'eficiencia', 'intencion_uso', 
                   'satisfaccion_claridad', 'satisfaccion_diseño']
    
    for campo in obligatorios:
        if not fila_dict.get(campo) or str(fila_dict[campo]).strip() == "":
            errores.append(f"Campo obligatorio vacío: {campo}")
    
    # Validar tipos numéricos
    numericos = ['utilidad', 'eficiencia', 'intencion_uso', 'satisfaccion_claridad', 'satisfaccion_diseño']
    for campo in numericos:
        if campo in fila_dict:
            try:
                val = float(fila_dict[campo])
                if val < 0 or val > 10:
                    errores.append(f"{campo} debe estar entre 0 y 10")
            except (ValueError, TypeError):
                errores.append(f"{campo} debe ser un número")
    
    # Limpiar textos
    campos_texto = ['modificar_secciones', 'comentarios', 'nombre_profesional']
    for campo in campos_texto:
        if campo in fila_dict:
            fila_dict[campo] = validar_y_limpiar_texto(fila_dict[campo], campo)
    
    return errores, fila_dict

def guardar_feedback_seguro(nueva_fila_dict, archivo_path):
    """
    Guarda feedback con validación completa
    """
    # 1. Validar la fila
    errores, fila_limpia = validar_fila_feedback(nueva_fila_dict)
    
    if errores:
        return False, errores
    
    # 2. Convertir a DataFrame
    nueva_fila_df = pd.DataFrame([fila_limpia])
    
    # 3. Leer archivo existente o crear nuevo
    if os.path.exists(archivo_path):
        try:
            df_existente = pd.read_csv(archivo_path, encoding='utf-8-sig')
            df_final = pd.concat([df_existente, nueva_fila_df], ignore_index=True)
        except Exception as e:
            return False, [f"Error leyendo archivo existente: {e}"]
    else:
        df_final = nueva_fila_df
    
    # 4. Validar estructura final
    columnas_esperadas = [
        'nombre_profesional', 'utilidad', 'eficiencia', 'intencion_uso',
        'satisfaccion_claridad', 'satisfaccion_diseño', 'modificar_secciones',
        'comentarios', 'fecha_envio', 'cedula_profesional', 'profesion_profesional'
    ]
    
    # Asegurar que todas las columnas existan
    for col in columnas_esperadas:
        if col not in df_final.columns:
            df_final[col] = ""
    
    # Reordenar columnas
    df_final = df_final[columnas_esperadas]
    
    # 5. Guardar con encoding seguro
    try:
        # Limpiar TODOS los caracteres especiales + QUOTE_NONE
        df_clean = df_final.copy()
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = (df_clean[col].astype(str)
                            .str.replace(',', ' ')    # ELIMINAR comas
                            .str.replace('"', ' ')    # ELIMINAR comillas dobles
                            .str.replace("'", ' ')    # ELIMINAR comillas simples
                            .str.replace(';', ' ')    # ELIMINAR punto y coma
                            .str.replace('\n', ' ')   # Saltos de línea
                            .str.replace('\r', ' ')   # Retornos de carro
                            .str.replace('\t', ' ')   # Tabs
                            .str.replace('|', ' ')    # Pipes
                            .str.replace('\\', ' '))  # Barras invertidas
        # Limpiar espacios múltiples
        for col in df_clean.select_dtypes(include=['object']).columns:
            df_clean[col] = df_clean[col].str.replace(r'\s+', ' ', regex=True).str.strip()
        df_clean.to_csv(archivo_path, index=False, encoding='utf-8-sig', quoting=3)
        return True, []
    except Exception as e:
        return False, [f"Error guardando archivo: {e}"]

# Ejemplo de uso:
if __name__ == "__main__":
    # Simular datos de prueba
    datos_prueba = {
        'nombre_profesional': 'Juan Pérez',
        'utilidad': 5,
        'eficiencia': 4,
        'intencion_uso': 8,
        'satisfaccion_claridad': 5,
        'satisfaccion_diseño': 4,
        'modificar_secciones': 'Agregaría más opciones, pero está bien',
        'comentarios': 'Muy buena aplicación!',
        'fecha_envio': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'cedula_profesional': '12345678',
        'profesion_profesional': 'Psicólogo'
    }
    
    exito, errores = guardar_feedback_seguro(datos_prueba, 'test_feedback.csv')
    if exito:
        print("✅ Guardado exitosamente")
    else:
        print("❌ Errores:", errores)