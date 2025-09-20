# validacion

Feedback y registro de profesionales

## Normalización y unificación de CSV

Agregué un script `normalize_and_merge.py` que:

- Detecta encoding y delimitador de cada `feedback*.csv`
- Lee de forma robusta (maneja comillas y saltos de línea en celdas)
- Normaliza encabezados (por ejemplo, `satisfaccion_diseno` -> `satisfaccion_diseño`)
- Elimina columnas auxiliares `*_opcion`
- Guarda versiones limpias por archivo en `./limpios/`
- Unifica todo en `validacion_unificado.csv` con columnas canónicas:
	- nombre_profesional, utilidad, eficiencia, intencion_uso, satisfaccion_claridad, satisfaccion_diseño, modificar_secciones, comentarios, fecha_envio, cedula_profesional, profesion_profesional

### Cómo correr

1) Instalar dependencias (una vez):

```
pip install -r requirements-normalize.txt
```

2) Ejecutar el script:

```
python normalize_and_merge.py
```

Esto generará:
- `limpios/feedbackX_limpio.csv` para cada archivo
- `validacion_unificado.csv` con todos los casos

Notas:
- Se escribe todo en UTF-8 con BOM (utf-8-sig) para abrir bien en Excel.
- Si aparecen filas con comillas internas largas, están preservadas correctamente en una sola celda de `comentarios`.
