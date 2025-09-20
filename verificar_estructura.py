import pandas as pd
import os

archivos = ['feedback1.csv','feedback2.csv','feedback3.csv','feedback4.csv','feedback5.csv','feedback6.csv','feedback7.csv']

print('🔍 VERIFICACIÓN DE ESTRUCTURA:')
print('='*50)

for f in archivos:
    path = f'c:/Users/HP/AppData/Local/Programs/Python/Python313/evaluaciones/validacion/{f}'
    if os.path.exists(path):
        df = pd.read_csv(path, nrows=0)
        print(f'✅ {f}: {len(df.columns)} columnas')
        print(f'   Headers: {list(df.columns)[:3]}... (primeras 3)')
    else:
        print(f'❌ {f}: No encontrado')

print('='*50)