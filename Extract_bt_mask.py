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
        print("     - Varios valores:   TIPO IN ('A', 'B')")

        where_clause = input(" SQL Expression: ").strip()

        nom_layer_temp = f"layer_temp_{os.path.basename(ruta_fc)}"
        try:
            # Crear MakeFeatureLayer con la cláusula WHERE
            arcpy.management.MakeFeatureLayer(
                in_features=ruta_fc,
                out_layer=nom_layer_temp,
                where_clause=where_clause,
            )

            rec_count = int(
                arcpy.management.GetCount(nom_layer_temp).getOutput(0)
            )
            print(
                f"✔ ¡Filtro aplicado correctamente! Entidades seleccionadas: {rec_count}"
            )
            return nom_layer_temp
        except arcpy.ExecuteError:
            print("❌ Error en la expresión SQL:")
            print(arcpy.GetMessages(2))
            sys.exit()
    else:
        print("ℹ No se aplicará ningún filtro a esta capa.")
        return ruta_fc


def definir_salida(gdb_entrada):
    """Define la GDB de salida, el Feature Dataset (si procede) y el nombre de la nueva capa."""
    print("\n" + "=" * 60)
    print("🎯 DEFINICIÓN DE LA SALIDA")
    print("=" * 60)

    # a) Selección de GDB de salida
    print("¿Dónde quieres guardar el resultado?")
    print(" [1] Utilizar la misma GDB de entrada de la primera capa")
    print(" [2] Seleccionar otra GDB mediante el explorador")

    opcion_gdb = input("Elige una opción (1/2): ").strip()

    if opcion_gdb == "2":
        gdb_salida = seleccionar_gdb(
            "Selecciona la Geodatabase (.gdb) de SALIDA"
        )
    else:
        gdb_salida = gdb_entrada
        print(f"✔ Se usará la GDB de entrada: {gdb_salida}")

    arcpy.env.workspace = gdb_salida

    # b) Feature Dataset o Raíz
    print("\n¿Dónde quieres ubicar la nueva capa dentro de la GDB?")
    print(" [1] Dentro de un Feature Dataset existente")
    print(" [2] Directamente en la raíz de la GDB")

    opcion_ds = input("Elige una opción (1/2): ").strip()
    ds_destino = ""

    if opcion_ds == "1":
        datasets = arcpy.ListDatasets("", "Feature")
        if datasets:
            print("\n📁 Feature Datasets disponibles:")
            for idx, ds in enumerate(datasets, start=1):
                print(f"   [{idx}] {ds}")

            while True:
                try:
                    num_ds = int(
                        input(
                            f"Selecciona el número de Feature Dataset (1-{len(datasets)}): "
                        )
                    )
                    if 1 <= num_ds <= len(datasets):
                        ds_destino = datasets[num_ds - 1]
                        print(
                            f"✔ Resultado ubicado en el Feature Dataset: '{ds_destino}'"
                        )
                        break
                    else:
                        print("⚠️ Número fuera de rango.")
                except ValueError:
                    print("⚠️ Introduce un número válido.")
        else:
            print(
                "ℹ La GDB de salida no tiene ningún Feature Dataset. Se guardará en la raíz."
            )

    # c) Nombre de la nueva Feature Class
    nom_salida = input("\n👉 Introduce el nombre de la nueva capa de resultado: ").strip()
    # Limpiar caracteres no permitidos
    nom_salida = arcpy.ValidateTableName(nom_salida, gdb_salida)

    # Construir la ruta final de salida
    if ds_destino:
        ruta_salida_final = os.path.join(gdb_salida, ds_destino, nom_salida)
    else:
        ruta_salida_final = os.path.join(gdb_salida, nom_salida)

    return ruta_salida_final


def main():
    print("=" * 60)
    print("   EXTRACT BY MASK / CLIP AUTOMATIZADO CON ARCPY")
    print("=" * 60)

    try:
        # 1. SELECCIÓN Y FILTRO DE LA CAPA DE ENTRADA (INPUT)
        gdb_in_1 = seleccionar_gdb(
            "1. Selecciona la GDB de la CAPA DE ENTRADA (Feature a recortar)"
        )
        fc_input = listar_y_seleccionar_feature_class(
            gdb_in_1, "ENTRADA (Input)"
        )
        fc_input_procesar = pedir_y_aplicar_query(fc_input, "ENTRADA")

        # 2. SELECCIÓN Y FILTRO DE LA CAPA DE CORTE (MASK / CLIP)
        gdb_in_2 = seleccionar_gdb(
            "2. Selecciona la GDB de la CAPA DE CORTE (Máscara / Clip Feature)"
        )
        fc_clip = listar_y_seleccionar_feature_class(gdb_in_2, "CORTE (Clip)")
        fc_clip_processar = pedir_y_aplicar_query(fc_clip, "CORTE")

        # 3. DEFINICIÓN DE LA SALIDA
        ruta_salida = definir_salida(gdb_in_1)

        # 4. EJECUCIÓN DEL GEOPROCESO (CLIP / EXTRACT BY MASK)
        print("\n" + "=" * 60)
        print("⚙️ EJECUTANDO EL GEOPROCESO DE CORTE (CLIP)...")
        print(f"   Input:   {fc_input}")
        print(f"   Clip:    {fc_clip}")
        print(f"   Salida:  {ruta_salida}")
        print("=" * 60)

        # Habilitar sobreescritura si el archivo ya existe
        arcpy.env.overwriteOutput = True

        # Ejecución de la herramienta Clip
        arcpy.analysis.Clip(
            in_features=fc_input_procesar,
            clip_features=fc_clip_processar,
            out_feature_class=ruta_salida,
        )

        print("\n✅ ¡GEOPROCESO FINALIZADO CON ÉXITO!")
        print(f"📍 Capa creada en: {ruta_salida}")

    except arcpy.ExecuteError:
        print("\n❌ ERROR DE ARCPY DURANTE LA EJECUCIÓN:")
        print(arcpy.GetMessages(2))
    except Exception as e:
        print(f"\n❌ SE HA PRODUCIDO UN ERROR INESPERADO: {e}")


if __name__ == "__main__":
    main()
