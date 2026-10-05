# -*- coding: utf-8 -*-

"""
COMPARADOR DE GEOMETRIAS (+ CAMPO OPCIONAL) EN ARCGIS PRO

CAPA 1 = ORIGINAL
CAPA 2 = NUEVA / REVISADA

SI SE SELECCIONA CAMPO:
  CANVIAT = "No" -> Geometria igual Y Campo igual
  CANVIAT = "Si" -> Geometria diferente O Campo diferente

SI NO SE SELECCIONA CAMPO (Solo Geometria):
  CANVIAT = "No" -> Geometria igual
  CANVIAT = "Si" -> Geometria diferente
"""

import os
import sys
import traceback
import tkinter as tk
from tkinter import filedialog

import arcpy

# ----------------------------------------------------------------------------
# INICIALIZACION DE TKINTER (Para ventanas flotantes)
# ----------------------------------------------------------------------------
try:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
except Exception:
    root = None


# ----------------------------------------------------------------------------
# SELECCIONAR GDB
# ----------------------------------------------------------------------------
def seleccionar_gdb(titulo):
    print("\n" + "=" * 75)
    print(titulo)
    print("=" * 75)

    if root:
        ruta_gdb = filedialog.askdirectory(title=titulo)
    else:
        ruta_gdb = input("Introduce la ruta de la GDB: ").strip()

    if not ruta_gdb:
        print("[-] No se ha seleccionado ninguna GDB.")
        return None

    ruta_gdb = os.path.normpath(ruta_gdb)

    if not ruta_gdb.lower().endswith(".gdb"):
        print("[-] La carpeta seleccionada no es una File Geodatabase (.gdb).")
        print("    Ruta:", ruta_gdb)
        return None

    if not arcpy.Exists(ruta_gdb):
        print("[-] ArcPy no encuentra la GDB seleccionada.")
        return None

    print("[OK] GDB seleccionada:")
    print("    ", ruta_gdb)
    return ruta_gdb


# ----------------------------------------------------------------------------
# LISTAR FEATURE CLASSES EN GDB
# ----------------------------------------------------------------------------
def listar_capas_gdb(ruta_gdb):
    print("\n" + "-" * 75)
    print("EXPLORANDO GDB:", os.path.basename(ruta_gdb))
    print("-" * 75)

    try:
        arcpy.env.workspace = ruta_gdb
        lista_capas = []
        contador = 1

        print("\n[+] Buscando Feature Classes en la raiz...")
        capas_raiz = arcpy.ListFeatureClasses() or []

        if capas_raiz:
            print("\n  [Raiz de la GDB]")
            for fc in capas_raiz:
                ruta = os.path.join(ruta_gdb, fc)
                lista_capas.append((contador, f"Raiz -> {fc}", ruta))
                print(f"    [{contador}] {fc}")
                contador += 1
        else:
            print("    No hay Feature Classes en la raiz.")

        print("\n[+] Buscando Feature Datasets...")
        datasets = arcpy.ListDatasets(feature_type="Feature") or []

        if datasets:
            for dataset in datasets:
                print(f"\n  [Dataset: {dataset}]")
                try:
                    capas_dataset = arcpy.ListFeatureClasses(feature_dataset=dataset) or []
                except Exception as e:
                    print(f"    [!] Error leyendo dataset {dataset}: {e}")
                    continue

                if not capas_dataset:
                    print("    No hay Feature Classes.")

                for fc in capas_dataset:
                    ruta = os.path.join(ruta_gdb, dataset, fc)
                    lista_capas.append((contador, f"Dataset: {dataset} -> {fc}", ruta))
                    print(f"    [{contador}] {fc}")
                    contador += 1
        else:
            print("    No hay Feature Datasets.")

        if not lista_capas:
            print("\n[-] No se ha encontrado ninguna Feature Class.")
            return []

        print(f"\n[OK] Se han encontrado {len(lista_capas)} Feature Class(es).")
        return lista_capas

    except Exception as e:
        print("\n[X] ERROR EXPLORANDO LA GDB")
        print("    ", e)
        traceback.print_exc()
        return []


# ----------------------------------------------------------------------------
# SELECCIONAR CAPA
# ----------------------------------------------------------------------------
def seleccionar_capa(ruta_gdb, nombre_rol):
    lista_capas = listar_capas_gdb(ruta_gdb)
    if not lista_capas:
        return None

    print("\n" + "-" * 75)
    print(f"SELECCION DE LA CAPA: {nombre_rol}")
    print("-" * 75)

    while True:
        try:
            entrada = input(f"\nEscribe el NUMERO de la capa {nombre_rol}: ").strip()
            if not entrada:
                print("[-] Debes escribir un numero.")
                continue

            numero = int(entrada)
            capa_seleccionada = next((c for c in lista_capas if c[0] == numero), None)

            if capa_seleccionada is None:
                print("[-] Numero no valido.")
                continue

            ruta_capa = capa_seleccionada[2]

            print("\n[OK] Capa seleccionada:")
            print("    ", capa_seleccionada[1])
            print("    ", ruta_capa)

            if not arcpy.Exists(ruta_capa):
                print("[-] ArcPy no encuentra la Feature Class.")
                return None

            return ruta_capa

        except ValueError:
            print("[-] Escribe un numero entero valido.")
        except KeyboardInterrupt:
            print("\n[!] Proceso cancelado.")
            return None


# ----------------------------------------------------------------------------
# SELECCIONAR CAMPO COMUN (OPCIONAL)
# ----------------------------------------------------------------------------
def seleccionar_campo(capa_original, capa_nueva):
    print("\n" + "=" * 75)
    print("SELECCION DEL CAMPO A COMPROBAR (OPCIONAL)")
    print("=" * 75)

    print("\nCAPA 1 - ORIGINAL:\n    ", capa_original)
    print("\nCAPA 2 - NUEVA / REVISADA:\n    ", capa_nueva)

    campos_original = arcpy.ListFields(capa_original)
    campos_nueva = arcpy.ListFields(capa_nueva)

    nombres_nueva = {c.name.upper() for c in campos_nueva}

    campos_comunes = []
    tipos_omitidos = ("OID", "GEOMETRY", "BLOB", "RASTER")

    for campo in campos_original:
        if campo.type.upper() in tipos_omitidos:
            continue
        if campo.name.upper() in nombres_nueva:
            campos_comunes.append(campo)

    print("\n" + "-" * 75)
    print("CAMPOS DISPONIBLES EN AMBAS CAPAS")
    print("-" * 75)
    print("[0] Omitir campo (SOLO COMPARAR GEOMETRIA)")

    for i, campo in enumerate(campos_comunes, start=1):
        print(f"[{i}] {campo.name} | Tipo: {campo.type} | Alias: {campo.aliasName}")

    print("-" * 75)

    while True:
        try:
            entrada = input("\nEscribe el NUMERO del campo a comprobar [0 para omitir]: ").strip()
            
            # Si se pulsa ENTER sin escribir nada o escribe '0'
            if not entrada or entrada == "0":
                print("\n[OK] No se ha seleccionado ningun campo. Solo se compararan geometrias.")
                return None

            numero = int(entrada)
            if numero < 1 or numero > len(campos_comunes):
                print("[-] Numero fuera de rango.")
                continue

            campo_sel = campos_comunes[numero - 1]

            print("\n[OK] Campo seleccionado:")
            print("     Nombre:", campo_sel.name)
            print("     Alias: ", campo_sel.aliasName)
            print("     Tipo:  ", campo_sel.type)

            return campo_sel.name

        except ValueError:
            print("[-] Escribe un numero valido.")
        except KeyboardInterrupt:
            print("\n[!] Proceso cancelado.")
            return None


# ----------------------------------------------------------------------------
# DEFINIR DESTINO DE SALIDA
# ----------------------------------------------------------------------------
def definir_destino_salida(gdb_origen):
    print("\n" + "=" * 75)
    print("DEFINICION DE LA CAPA DE SALIDA")
    print("=" * 75)

    print("\n1. Utilizar la misma GDB de origen")
    print("2. Seleccionar otra GDB")

    opcion = input("Elige una opcion (1 o 2) [1]: ").strip()
    gdb_salida = seleccionar_gdb("Selecciona la GDB DE SALIDA") if opcion == "2" else gdb_origen

    if not gdb_salida:
        return None, None

    arcpy.env.workspace = gdb_salida

    print("\nDonde quieres guardar el resultado?")
    print("1. En la raiz de la GDB")
    print("2. Dentro de un Feature Dataset existente")

    opcion_dataset = input("Elige una opcion (1 o 2) [1]: ").strip()
    dataset_salida = None

    if opcion_dataset == "2":
        datasets = arcpy.ListDatasets(feature_type="Feature") or []
        if datasets:
            print("\nFeature Datasets disponibles:")
            for i, dataset in enumerate(datasets, start=1):
                print(f"[{i}] {dataset}")

            while True:
                try:
                    num = int(input("Selecciona el numero del Dataset: ").strip())
                    if 1 <= num <= len(datasets):
                        dataset_salida = datasets[num - 1]
                        break
                    print("[-] Numero fuera de rango.")
                except ValueError:
                    print("[-] Escribe un numero valido.")
        else:
            print("[!] No hay Feature Datasets. Se guardara en la raiz.")

    while True:
        nombre = input("\nEscribe el nombre de la Feature Class de resultado: ").strip()
        if not nombre:
            print("[-] El nombre no puede estar vacio.")
            continue

        nombre = arcpy.ValidateTableName(nombre, gdb_salida)
        break

    ruta_salida = (
        os.path.join(gdb_salida, dataset_salida, nombre)
        if dataset_salida
        else os.path.join(gdb_salida, nombre)
    )

    print("\n[OK] Salida configurada:")
    print("     GDB:    ", gdb_salida)
    print("     Dataset:", dataset_salida if dataset_salida else "(raiz)")
    print("     Capa:   ", nombre)
    print("     Ruta:   ", ruta_salida)

    return gdb_salida, ruta_salida


# ----------------------------------------------------------------------------
# COMPROBAR COMPATIBILIDAD
# ----------------------------------------------------------------------------
def comprobar_capas(capa_original, capa_nueva):
    print("\n" + "-" * 75)
    print("COMPROBANDO LAS CAPAS")
    print("-" * 75)

    if not arcpy.Exists(capa_original):
        raise RuntimeError(f"No existe la capa ORIGINAL:\n{capa_original}")
    if not arcpy.Exists(capa_nueva):
        raise RuntimeError(f"No existe la capa NUEVA:\n{capa_nueva}")

    desc_orig = arcpy.Describe(capa_original)
    desc_nueva = arcpy.Describe(capa_nueva)

    print(f"\n[OK] CAPA 1 - ORIGINAL: {capa_original}")
    print(f"[OK] CAPA 2 - NUEVA:    {capa_nueva}")

    print("\nTipo geometrico:")
    print("     Capa 1:", desc_orig.shapeType)
    print("     Capa 2:", desc_nueva.shapeType)

    if desc_orig.shapeType != desc_nueva.shapeType:
        raise RuntimeError("Las dos capas no tienen el mismo tipo geometrico.")


# ----------------------------------------------------------------------------
# GENERAR CLAVE ESPACIAL PARA COMPARACION RAPIDA (O(1))
# ----------------------------------------------------------------------------
def obtener_hash_geometria(geom, decimales=3):
    if geom is None:
        return None
    cent = geom.trueCentroid
    area_length = geom.area if geom.type in ("polygon", "multipatch") else geom.length
    return (round(cent.X, decimales), round(cent.Y, decimales), round(area_length, decimales))


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    try:
        print("\n" + "=" * 75)
        print("  COMPARADOR DE GEOMETRIA + CAMPO OPCIONAL (ARCGIS PRO)")
        print("=" * 75)

        gdb_original = seleccionar_gdb(">>> PASO 1: SELECCION DE LA GDB ORIGINAL")
        if not gdb_original:
            return

        capa_original = seleccionar_capa(gdb_original, "ORIGINAL")
        if not capa_original:
            return

        gdb_nueva = seleccionar_gdb(">>> PASO 3: SELECCION DE LA GDB NUEVA / REVISADA")
        if not gdb_nueva:
            return

        capa_nueva = seleccionar_capa(gdb_nueva, "NUEVA / REVISADA")
        if not capa_nueva:
            return

        comprobar_capas(capa_original, capa_nueva)

        campo_comprobar = seleccionar_campo(capa_original, capa_nueva)

        gdb_salida, ruta_salida = definir_destino_salida(gdb_original)
        if not gdb_salida or not ruta_salida:
            return

        print("\n" + "=" * 75)
        print("  EJECUTANDO COMPARACION")
        print("=" * 75)

        arcpy.env.overwriteOutput = True

        print("\n[1/4] Copiando Capa 1 ORIGINAL a capa de salida...")
        arcpy.management.CopyFeatures(capa_original, ruta_salida)
        print("[OK] Capa original copiada.")

        print("\n[2/4] Preparando campo CANVIAT...")
        campo_canviat = "CANVIAT"
        campos_existentes = [c.name.upper() for c in arcpy.ListFields(ruta_salida)]

        if campo_canviat.upper() not in campos_existentes:
            arcpy.management.AddField(
                ruta_salida,
                campo_canviat,
                "TEXT",
                field_length=10,
                field_alias="Se ha modificado?"
            )
            print("[OK] Campo CANVIAT creado.")

        print("\n[3/4] Indexando Capa 2 en memoria...")
        mapa_nueva = {}
        conteo_capa_2 = 0

        # Si se selecciono campo, lo incluimos en el SearchCursor
        campos_cursor_nueva = ["SHAPE@", campo_comprobar] if campo_comprobar else ["SHAPE@"]

        with arcpy.da.SearchCursor(capa_nueva, campos_cursor_nueva) as cursor:
            for fila in cursor:
                geom = fila[0]
                valor = fila[1] if campo_comprobar else None
                if geom is not None:
                    clave_espacial = obtener_hash_geometria(geom)
                    mapa_nueva[clave_espacial] = (geom, valor)
                    conteo_capa_2 += 1

        print(f"[OK] Cargadas e indexadas {conteo_capa_2} entidades de la Capa 2.")

        print("\n[4/4] Comparando entidades...")

        total = 0
        sin_cambios = 0
        cambiados = 0
        cambios_geometria = 0
        cambios_campo = 0

        # Campos a consultar en UpdateCursor
        if campo_comprobar:
            campos_cursor_orig = ["SHAPE@", campo_comprobar, campo_canviat]
        else:
            campos_cursor_orig = ["SHAPE@", campo_canviat]

        with arcpy.da.UpdateCursor(ruta_salida, campos_cursor_orig) as cursor:
            for fila in cursor:
                total += 1

                if total % 1000 == 0:
                    print(f"    Entidades procesadas: {total}")

                geom_orig = fila[0]
                valor_orig = fila[1] if campo_comprobar else None

                if geom_orig is None:
                    if campo_comprobar:
                        cursor.updateRow([geom_orig, valor_orig, "Si"])
                    else:
                        cursor.updateRow([geom_orig, "Si"])
                    cambiados += 1
                    cambios_geometria += 1
                    continue

                clave_orig = obtener_hash_geometria(geom_orig)

                if clave_orig in mapa_nueva:
                    geom_nueva, valor_nuevo = mapa_nueva[clave_orig]

                    if geom_orig.equals(geom_nueva):
                        if campo_comprobar:
                            v_orig_norm = "" if valor_orig is None else str(valor_orig).strip()
                            v_nuev_norm = "" if valor_nuevo is None else str(valor_nuevo).strip()

                            if v_orig_norm == v_nuev_norm:
                                estado = "No"
                                sin_cambios += 1
                            else:
                                estado = "Si"
                                cambiados += 1
                                cambios_campo += 1
                        else:
                            # Sin campo -> Geometria identica
                            estado = "No"
                            sin_cambios += 1
                    else:
                        estado = "Si"
                        cambiados += 1
                        cambios_geometria += 1
                else:
                    estado = "Si"
                    cambiados += 1
                    cambios_geometria += 1

                if campo_comprobar:
                    cursor.updateRow([geom_orig, valor_orig, estado])
                else:
                    cursor.updateRow([geom_orig, estado])

        # IMPRIMIR RESUMEN
        print("\n" + "=" * 75)
        print("  COMPARACION FINALIZADA CON EXITO")
        print("=" * 75)
        print(f"Total entidades:        {total}")
        print(f"Sin cambios (CANVIAT=No): {sin_cambios}")
        print(f"Con cambios (CANVIAT=Si): {cambiados}")
        print("  - Cambios en geometria: ", cambios_geometria)
        if campo_comprobar:
            print(f"  - Cambios en campo '{campo_comprobar}':", cambios_campo)
        else:
            print("  - Comparacion de campo: [OMITIDO]")
        print("Ruta de salida:         ", ruta_salida)

    except KeyboardInterrupt:
        print("\n[!] Proceso cancelado por el usuario.")
    except Exception as e:
        print("\n[X] ERROR DURANTE LA EJECUCION:")
        print("   ", e)
        traceback.print_exc()
    finally:
        if root:
            try:
                root.destroy()
            except Exception:
                pass


if __name__ == "__main__":
    main()
    print("\n" + "=" * 75)
    print(" SCRIPT FINALIZADO")
    print("=" * 75)
    try:
        input("Pulsa ENTER para cerrar esta ventana: ")
    except Exception:
        pass