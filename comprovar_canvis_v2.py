```python
# -*- coding: utf-8 -*-

"""
COMPARADOR DE GEOMETRIES + CAMP EN ARCGIS PRO (ArcPy)

Capa 1 = ORIGINAL
    Versió antiga / de referència.

Capa 2 = NOVA / REVISADA
    Versió nova que es vol comparar.

CRITERI:

    CANVIAT = "No"
        -> La geometria de la Capa 1 existeix igual a la Capa 2
        Y
        -> El camp seleccionat té el mateix valor.

    CANVIAT = "Si"
        -> La geometria ha canviat
        O
        -> El camp seleccionat ha canviat
        O
        -> La geometria original ja no existeix a la Capa 2.

El resultat és una còpia de la Capa 1 amb el camp CANVIAT.
"""


import os
import traceback
import tkinter as tk
from tkinter import filedialog

import arcpy


# ===========================================================================
# CONFIGURACIÓ FINESTRA
# ===========================================================================

root = tk.Tk()
root.withdraw()

try:
    root.attributes("-topmost", True)
except Exception:
    pass


# ===========================================================================
# SELECCIONAR GDB
# ===========================================================================

def seleccionar_gdb(titol):

    print("\n" + "=" * 75)
    print(titol)
    print("=" * 75)

    ruta_gdb = filedialog.askdirectory(
        title=titol
    )

    if not ruta_gdb:

        print("[-] No s'ha seleccionat cap GDB.")
        return None

    ruta_gdb = os.path.normpath(ruta_gdb)

    if not ruta_gdb.lower().endswith(".gdb"):

        print("[-] La carpeta seleccionada no és una GDB.")
        print(f"    Ruta: {ruta_gdb}")

        return None

    if not arcpy.Exists(ruta_gdb):

        print("[-] ArcPy no troba la GDB.")

        return None

    print("\n[OK] GDB seleccionada:")
    print(f"     {ruta_gdb}")

    return ruta_gdb


# ===========================================================================
# LLISTAR CAPES DE LA GDB
# ===========================================================================

def llistar_capes_gdb(ruta_gdb):

    print("\n" + "-" * 75)
    print(
        f"EXPLORANT GDB: "
        f"{os.path.basename(ruta_gdb)}"
    )
    print("-" * 75)

    try:

        arcpy.env.workspace = ruta_gdb

        llista_capes = []

        comptador = 1

        # -------------------------------------------------------------------
        # CAPES A L'ARREL
        # -------------------------------------------------------------------

        print("\n[+] Buscant Feature Classes a l'arrel...")

        try:

            capes_arrel = (
                arcpy.ListFeatureClasses()
                or []
            )

        except Exception as e:

            print(
                f"[!] Error llistant les capes: {e}"
            )

            capes_arrel = []

        if capes_arrel:

            print("\n  [Arrel de la GDB]")

            for fc in capes_arrel:

                ruta_completa = os.path.join(
                    ruta_gdb,
                    fc
                )

                llista_capes.append(
                    (
                        comptador,
                        f"Arrel -> {fc}",
                        ruta_completa
                    )
                )

                print(
                    f"    [{comptador}] {fc}"
                )

                comptador += 1

        else:

            print(
                "    No hi ha Feature Classes a l'arrel."
            )

        # -------------------------------------------------------------------
        # FEATURE DATASETS
        # -------------------------------------------------------------------

        print("\n[+] Buscant Feature Datasets...")

        try:

            datasets = (
                arcpy.ListDatasets(
                    feature_type="Feature"
                )
                or []
            )

        except Exception as e:

            print(
                f"[!] Error llistant datasets: {e}"
            )

            datasets = []

        if datasets:

            for ds in datasets:

                print(
                    f"\n  [Dataset: {ds}]"
                )

                try:

                    capes_ds = (
                        arcpy.ListFeatureClasses(
                            feature_dataset=ds
                        )
                        or []
                    )

                except Exception as e:

                    print(
                        f"    [!] Error llegint "
                        f"'{ds}': {e}"
                    )

                    continue

                if not capes_ds:

                    print(
                        "    No hi ha Feature Classes."
                    )

                for fc in capes_ds:

                    ruta_completa = os.path.join(
                        ruta_gdb,
                        ds,
                        fc
                    )

                    llista_capes.append(
                        (
                            comptador,
                            f"Dataset: {ds} -> {fc}",
                            ruta_completa
                        )
                    )

                    print(
                        f"    [{comptador}] {fc}"
                    )

                    comptador += 1

        else:

            print(
                "    No hi ha Feature Datasets."
            )

        if not llista_capes:

            print(
                "\n[-] No s'ha trobat cap Feature Class."
            )

            return []

        print(
            f"\n[OK] S'han trobat "
            f"{len(llista_capes)} Feature Class(s)."
        )

        return llista_capes

    except Exception as e:

        print(
            "\n[X] ERROR EXPLORANT LA GDB"
        )

        print(e)

        traceback.print_exc()

        return []


# ===========================================================================
# SELECCIONAR CAPA
# ===========================================================================

def seleccionar_capa(
    ruta_gdb,
    rol_capa
):

    llista_capes = llistar_capes_gdb(
        ruta_gdb
    )

    if not llista_capes:

        return None

    print("\n" + "-" * 75)
    print(
        f"SELECCIÓ DE LA CAPA {rol_capa}"
    )
    print("-" * 75)

    while True:

        try:

            entrada = input(
                f"\nEscriu el NÚMERO de la capa "
                f"{rol_capa}: "
            ).strip()

            if not entrada:

                print(
                    "[-] Has d'escriure un número."
                )

                continue

            opcio = int(entrada)

            capa_triada = next(
                (
                    capa
                    for capa in llista_capes
                    if capa[0] == opcio
                ),
                None
            )

            if capa_triada:

                ruta_capa = capa_triada[2]

                print(
                    "\n[OK] Capa seleccionada:"
                )

                print(
                    f"     {capa_triada[1]}"
                )

                print(
                    f"     {ruta_capa}"
                )

                if not arcpy.Exists(
                    ruta_capa
                ):

                    print(
                        "[-] ArcPy no troba "
                        "la Feature Class."
                    )

                    return None

                return ruta_capa

            print(
                "[-] Número no vàlid."
            )

        except ValueError:

            print(
                "[-] Escriu un número enter vàlid."
            )

        except KeyboardInterrupt:

            print(
                "\n[!] Procés cancel·lat."
            )

            return None


# ===========================================================================
# SELECCIONAR CAMP
# ===========================================================================

def seleccionar_camp(
    capa_original,
    capa_nova
):

    print("\n")
    print("=" * 75)
    print("  SELECCIÓ DEL CAMP A COMPROVAR")
    print("=" * 75)

    print(
        "\nLa Capa 1 és la ORIGINAL."
    )

    print(
        "La Capa 2 és la NOVA/REVISADA."
    )

    print(
        "\nEs mostraran els camps que "
        "existeixen a les dues capes."
    )

    # -----------------------------------------------------------------------
    # OBTENIR CAMPS
    # -----------------------------------------------------------------------

    camps_original = arcpy.ListFields(
        capa_original
    )

    camps_nova = arcpy.ListFields(
        capa_nova
    )

    noms_nova = {
        campo.name.upper()
        for campo in camps_nova
    }

    camps_comuns = []

    for campo in camps_original:

        nom_upper = campo.name.upper()

        # ---------------------------------------------------------------
        # EXCLOURE CAMPS ESPECIALS
        # ---------------------------------------------------------------

        if campo.type.upper() in (
            "OID",
            "GEOMETRY",
            "RASTER",
            "BLOB"
        ):

            continue

        if nom_upper in noms_nova:

            camps_comuns.append(
                campo
            )

    # -----------------------------------------------------------------------
    # COMPROVAR
    # -----------------------------------------------------------------------

    if not camps_comuns:

        raise RuntimeError(
            "\nNo s'ha trobat cap camp comú "
            "entre les dues capes."
        )

    # -----------------------------------------------------------------------
    # MOSTRAR LLISTA
    # -----------------------------------------------------------------------

    print("\n")
    print(
        "CAMPOS DISPONIBLES:"
    )

    print("-" * 75)

    for i, campo in enumerate(
        camps_comuns,
        start=1
    ):

        print(
            f"  [{i}] "
            f"{campo.name}"
            f" | Tipus: {campo.type}"
            f" | Alias: {campo.aliasName}"
        )

    print("-" * 75)

    # -----------------------------------------------------------------------
    # SELECCIÓ
    # -----------------------------------------------------------------------

    while True:

        try:

            entrada = input(
                "\nEscriu el NÚMERO del camp "
                "que vols comprovar: "
            ).strip()

            if not entrada:

                print(
                    "[-] Has d'escriure un número."
                )

                continue

            numero = int(entrada)

            if (
                numero >= 1
                and numero <= len(camps_comuns)
            ):

                campo = camps_comuns[
                    numero - 1
                ]

                print("\n")
                print(
                    "[OK] CAMP SELECCIONAT:"
                )

                print(
                    f"     Nom:   {campo.name}"
                )

                print(
                    f"     Alias: {campo.aliasName}"
                )

                print(
                    f"     Tipus:  {campo.type}"
                )

                return campo.name

            print(
                "[-] Número fora de rang."
            )

        except ValueError:

            print(
                "[-] Escriu un número vàl
```
