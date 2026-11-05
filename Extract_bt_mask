import sys
import os
import arcpy
import tkinter as tk
from tkinter import filedialog

# Ocultar la ventana principal de tkinter
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)


def seleccionar_gdb(titulo="Selecciona una Geodatabase (.gdb)"):
    """Abre un explorador de archivos de Windows para seleccionar una GDB."""
    print(f"\n[?] {titulo}")
    ruta_gdb = filedialog.askdirectory(title=titulo)
    if not ruta_gdb or not ruta_gdb.endswith(".gdb"):
        print("❌ No se ha seleccionado ninguna Geodatabase válida (.gdb). Cancelado.")
        sys.exit()
    return ruta_gdb


def listar_y_seleccionar_feature_class(gdb_path, etiqueta_capa="entrada"):
    """
    Lee todas las Feature Classes de la GDB (raíz y Feature Datasets)
    y permite al usuario elegir una mediante un número.
    """
    arcpy.env.workspace = gdb_path
    lista_capas = []
    contador = 1

    print(f"\n" + "=" * 60)
    print(f"📂 CAPAS DISPONIBLES EN LA GDB ({etiqueta_capa.upper()}):")
    print(f"   Ruta: {gdb_path}")
    print("=" * 60)

    # 1. Capas en la raíz de la GDB
    capas_raiz = arcpy.ListFeatureClasses()
    if capas_raiz:
        print("\n🔹 Raíz de la GDB:")
        for fc in capas_raiz:
            ruta_completa = os.path.join(gdb_path, fc)
            lista_capas.append(
                {
                    "num": contador,
                    "nom": fc,
                    "dataset": "Raíz",
                    "path": ruta_completa,
                }
            )
            print(f"   [{contador}] {fc}")
            contador += 1

    # 2. Capas dentro de Feature Datasets
    datasets = arcpy.ListDatasets("", "Feature")
    if datasets:
        for ds in datasets:
            print(f"\n📁 Feature Dataset: {ds}")
            capas_ds = arcpy.ListFeatureClasses(feature_dataset=ds)
            for fc in capas_ds:
                ruta_completa = os.path.join(gdb_path, ds, fc)
                lista_capas.append(
                    {
                        "num": contador,
                        "nom": fc,
                        "dataset": ds,
                        "path": ruta_completa,
                    }
                )
                print(f"   [{contador}] {fc}")
                contador += 1

    if not lista_capas:
        print("❌ La GDB seleccionada no contiene ninguna Feature Class.")
        sys.exit()

    # Selección del usuario
    while True:
        try:
            opcion = int(
                input(
                    f"\n👉 Introduce el número de la capa de {etiqueta_capa} con la que quieres trabajar (1-{len(lista_capas)}): "
                )
            )
            if 1 <= opcion <= len(lista_capas):
                capa_seleccionada = lista_capas[opcion - 1]
                print(
                    f"✔ Capa seleccionada: '{capa_seleccionada['nom']}' (Ubicación: {capa_seleccionada['dataset']})"
                )
                return capa_seleccionada["path"]
            else:
                print("⚠️ Número fuera de rango. Inténtalo de nuevo.")
        except ValueError:
            print("⚠️ Por favor, introduce un número entero válido.")


def pedir_y_aplicar_query(ruta_fc, etiqueta_capa=""):
    """
    Pregunta al usuario si quiere aplicar un filtro de selección (SQL) a la capa
    y crea una capa temporal en memoria con el filtro aplicado.
    """
    print(f"\n--- Filtro / Query para la capa de {etiqueta_capa} ---")
    aplicar = (
        input("¿Quieres aplicar algún filtro (Where Clause / SQL) a esta capa? (s/n): ")
        .strip()
        .lower()
    )

    if aplicar == "s":
        print(
            "\n💡 Introduce la expresión SQL tal como la escribirías en ArcGIS Pro."
        )
        print("   Ejemplos:")
        print("     - Campo de texto:   NOMBRE = 'Madrid'")
        print("     - Campo numérico:   POBLACION > 50000")
