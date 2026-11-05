# Scripts GIS – ArcGIS Pro

Colección de scripts desarrollados en Python con **ArcPy** para automatizar diferentes tareas y procesos de trabajo en ArcGIS Pro.

El repositorio incluye herramientas de análisis espacial, gestión de datos vectoriales y automatización de geoprocesos.

## Scripts

| Script | Descripción |
|---|---|
| `Afegir_camp_si_intersecta.py` | Añade atributos entre capas mediante una unión espacial (Spatial Join) por intersección. |
| `Extract_bt_mask.py` | Recorta entidades de una capa utilizando otra como máscara (Clip), con posibilidad de aplicar consultas SQL. |
| `afegir_codi_unic.py` | Añade un identificador numérico secuencial y único a las entidades de una capa. |
| `comprobar_canvis_v3.py` | Compara dos versiones de una capa para identificar cambios geométricos y de atributos. |
| `prueba.py` | Genera polígonos aleatorios en una geodatabase para realizar pruebas con ArcPy. |

## Requisitos

- ArcGIS Pro
- Python 3 (entorno de ArcGIS Pro)
- ArcPy

## Ejecución

Los scripts deben ejecutarse utilizando el intérprete de Python incluido en ArcGIS Pro.

```powershell
& "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" "ruta\del\script.py"
```

## Autor

**Gerard Franch Duxans**

[GitHub – gerardfradu](https://github.com/gerardfradu)
