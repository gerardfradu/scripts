# -*- coding: utf-8 -*-
"""
===============================================================
INTERSECT + INCORPORACIÓ DE CAMPS - ArcGIS Pro / ArcPy
===============================================================

Objectiu:
    Agafar els camps de la CAPA 1 i incorporar-los a la CAPA 2
    quan les seves geometries intersecten.

    El resultat és una còpia de la CAPA 2 amb els camps de la
    CAPA 1 incorporats.

Flux:
    1. Seleccionar GDB de la CAPA 1
    2. Seleccionar Feature Class de la CAPA 1
    3. Seleccionar GDB de la CAPA 2
    4. Seleccionar Feature Class de la CAPA 2
    5. Seleccionar GDB de sortida
    6. Escollir si el resultat va a un Feature Dataset o a l'arrel
    7. Indicar nom de la capa de resultat
    8. Executar Spatial Join amb INTERSECT
    9. Guardar el resultat

La CAPA 2 és la capa "base":
    - Manté les seves geometries
    - Manté els seus registres
    - Rep els camps de la CAPA 1

No modifica cap de les capes originals.
===============================================================
"""

import arcpy
import os
import sys
import tkinter as tk
from tkinter import filedialog


# =============================================================
# CONFIGURACIÓ
# =============================================================

arcpy.env.overwriteOutput = True


# =============================================================
# FUNCIONS GENERALS
# =============================================================

def seleccionar_gdb(titol):
    """
    Obre un explorador de Windows per seleccionar una GDB.
    """

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    carpeta = filedialog.askdirectory(
        title=titol
    )

    root.destroy()

    if not carpeta:
        raise RuntimeError("No s'ha seleccionat cap GDB.")

    if not carpeta.lower().endswith(".gdb"):
        raise RuntimeError(
            "La carpeta seleccionada no sembla una Geodatabase (.gdb)."
        )

    return carpeta


def seleccionar_fitxer(titol, extensions):
    """
    Obre un explorador de fitxers.
    """

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    fitxer = filedialog.askopenfilename(
        title=titol,
        filetypes=extensions
    )

    root.destroy()

    if not fitxer:
        raise RuntimeError("No s'ha seleccionat cap fitxer.")

    return fitxer


def llistar_feature_classes(gdb):
    """
    Detecta Feature Classes tant a l'arrel de la GDB
    com dins dels Feature Datasets.

    Retorna una llista amb:
        número
        nom
        ruta
        dataset
    """

    elements = []

    # ---------------------------------------------------------
    # Feature Classes a l'arrel
    # ---------------------------------------------------------

    arcpy.env.workspace = gdb

    fcs_arrel = arcpy.ListFeatureClasses()

    if fcs_arrel:
        for fc in fcs_arrel:
            ruta = os.path.join(gdb, fc)

            elements.append({
                "nom": fc,
                "ruta": ruta,
                "dataset": None
            })

    # ---------------------------------------------------------
    # Feature Datasets
    # ---------------------------------------------------------

    datasets = arcpy.ListDatasets(
        feature_type="feature"
    )

    if datasets:

        for dataset in datasets:

            ruta_dataset = os.path.join(
                gdb,
                dataset
            )

            fcs_dataset = arcpy.ListFeatureClasses(
                feature_dataset=dataset
            )

            if fcs_dataset:

                for fc in fcs_dataset:

                    ruta = os.path.join(
                        ruta_dataset,
                        fc
                    )

                    elements.append({
                        "nom": fc,
                        "ruta": ruta,
                        "dataset": dataset
                    })

    return elements


def seleccionar_feature_class(gdb, numero_capa):
    """
    Mostra totes les Feature Classes de la GDB
    i permet seleccionar-ne una pel número.
    """

    capes = llistar_feature_classes(gdb)

    if not capes:
        raise RuntimeError(
            f"No s'han trobat Feature Classes a:\n{gdb}"
        )

    print()
    print("=" * 70)
    print(f"CAPES DISPONIBLES - {numero_capa}")
    print("=" * 70)

    # ---------------------------------------------------------
    # Agrupar visualment per Dataset / Arrel
    # ---------------------------------------------------------

    print()
    print("ARREL DE LA GDB:")

    for i, capa in enumerate(capes, start=1):

        if capa["dataset"] is None:
            print(
                f"   [{i}] {capa['nom']}"
            )

    print()

    # Mostrar datasets
    datasets_mostrats = []

    for capa in capes:

        dataset = capa["dataset"]

        if dataset is not None and dataset not in datasets_mostrats:

            datasets_mostrats.append(dataset)

            print(f"FEATURE DATASET: {dataset}")

            for i, capa2 in enumerate(capes, start=1):

                if capa2["dataset"] == dataset:

                    print(
                        f"   [{i}] {capa2['nom']}"
                    )

            print()

    # ---------------------------------------------------------
    # Selecció
    # ---------------------------------------------------------

    while True:

        try:

            resposta = input(
                f"Selecciona el número de la {numero_capa}: "
            ).strip()

            numero = int(resposta)

            if 1 <= numero <= len(capes):

                seleccionada = capes[numero - 1]

                print()
                print(
                    f"✓ Seleccionada: {seleccionada['nom']}"
                )

                if seleccionada["dataset"]:
                    print(
                        f"  Feature Dataset: "
                        f"{seleccionada['dataset']}"
                    )

                print(
                    f"  Ruta: {seleccionada['ruta']}"
                )

                return seleccionada

            print(
                "ERROR: El número no correspon a cap cap."
            )

        except ValueError:

            print(
                "ERROR: Escriu un número."
            )


def seleccionar_gdb_sortida(gdb_entrada_1, gdb_entrada_2):
    """
    Permet utilitzar una de les GDB d'entrada
    o seleccionar una GDB diferent.
    """

    print()
    print("=" * 70)
    print("GEODATABASE DE SORTIDA")
    print("=" * 70)

    print()
    print("[1] Utilitzar la GDB de la CAPA 1")
    print("[2] Utilitzar la GDB de la CAPA 2")
    print("[3] Seleccionar una altra GDB")

    while True:

        opcio = input(
            "\nSelecciona una opció [1-3]: "
        ).strip()

        if opcio == "1":
            return gdb_entrada_1

        elif opcio == "2":
            return gdb_entrada_2

        elif opcio == "3":
            return seleccionar_gdb(
                "Selecciona la GDB de SORTIDA"
            )

        else:
            print("Opció no vàlida.")


def seleccionar_dataset_sortida(gdb):
    """
    Permet seleccionar un Feature Dataset existent
    o l'arrel de la GDB.
    """

    arcpy.env.workspace = gdb

    datasets = arcpy.ListDatasets(
        feature_type="feature"
    )

    print()
    print("=" * 70)
    print("UBICACIÓ DEL RESULTAT")
    print("=" * 70)

    print()
    print("[0] Arrel de la GDB")

    if datasets:

        for i, dataset in enumerate(datasets, start=1):
            print(
                f"[{i}] {dataset}"
            )

    print()

    while True:

        resposta = input(
            "Selecciona on desar el resultat: "
        ).strip()

        try:

            numero = int(resposta)

            if numero == 0:

                return gdb

            if datasets and 1 <= numero <= len(datasets):

                dataset = datasets[numero - 1]

                return os.path.join(
                    gdb,
                    dataset
                )

            print("Número no vàlid.")

        except ValueError:

            print(
                "ERROR: Escriu un número."
            )


def demanar_nom_resultat():
    """
    Demana el nom de la Feature Class de sortida.
    """

    while True:

        nom = input(
            "\nNom de la nova Feature Class: "
        ).strip()

        if not nom:

            print(
                "El nom no pot estar buit."
            )
            continue

        # Evitar caràcters especialment problemàtics
        caracters_invalids = [
            "\\", "/", ":", "*", "?",
            '"', "<", ">", "|"
        ]

        if any(
            caracter in nom
            for caracter in caracters_invalids
        ):

            print(
                "El nom conté caràcters no vàlids."
            )
            continue

        return nom


# =============================================================
# EXECUCIÓ PRINCIPAL
# =============================================================

def main():

    print()
    print("=" * 70)
    print("   INTERSECT - INCORPORACIÓ DE CAMPS")
    print("=" * 70)
    print()
    print(
        "La CAPA 1 aportarà els seus camps."
    )
    print(
        "La CAPA 2 serà la capa base del resultat."
    )
    print(
        "Només es modificaran les dades del resultat."
    )
    print()

    try:

        # =====================================================
        # 1. CAPA 1
        # =====================================================

        print()
        print("=" * 70)
        print("PAS 1 - SELECCIÓ DE LA CAPA 1")
        print("=" * 70)

        print()
        print(
            "La CAPA 1 és la capa de la qual "
            "volem incorporar els camps."
        )

        gdb_1 = seleccionar_gdb(
            "Selecciona la GDB de la CAPA 1"
        )

        capa_1 = seleccionar_feature_class(
            gdb_1,
            "CAPA 1"
        )

        ruta_capa_1 = capa_1["ruta"]

        # =====================================================
        # 2. CAPA 2
        # =====================================================

        print()
        print("=" * 70)
        print("PAS 2 - SELECCIÓ DE LA CAPA 2")
        print("=" * 70)

        print()
        print(
            "La CAPA 2 serà la capa base del resultat."
        )
        print(
            "La seva geometria i registres es conservaran."
        )

        gdb_2 = seleccionar_gdb(
            "Selecciona la GDB de la CAPA 2"
        )

        capa_2 = seleccionar_feature_class(
            gdb_2,
            "CAPA 2"
        )

        ruta_capa_2 = capa_2["ruta"]

        # =====================================================
        # INFORMACIÓ
        # =====================================================

        print()
        print("=" * 70)
        print("RESUM DE LA OPERACIÓ")
        print("=" * 70)

        print()
        print("CAPA 1 - CAMPS QUE S'INCORPORARAN:")
        print(f"   {ruta_capa_1}")

        print()
        print("CAPA 2 - CAPA BASE:")
        print(f"   {ruta_capa_2}")

        print()
        print("RELACIÓ ESPACIAL:")
        print("   INTERSECT")

        # =====================================================
        # 3. GDB DE SORTIDA
        # =====================================================

        gdb_sortida = seleccionar_gdb_sortida(
            gdb_1,
            gdb_2
        )

        print()
        print(
            f"GDB de sortida seleccionada:\n{gdb_sortida}"
        )

        # =====================================================
        # 4. FEATURE DATASET / ARREL
        # =====================================================

        ubicacio_sortida = seleccionar_dataset_sortida(
            gdb_sortida
        )

        # =====================================================
        # 5. NOM RESULTAT
        # =====================================================

        nom_resultat = demanar_nom_resultat()

        ruta_sortida = os.path.join(
            ubicacio_sortida,
            nom_resultat
        )

        # =====================================================
        # COMPROVAR SI EXISTEIX
        # =====================================================

        if arcpy.Exists(ruta_sortida):

            print()
            print(
                "AVÍS: Ja existeix una Feature Class amb "
                "aquest nom."
            )

            while True:

                resposta = input(
                    "Vols substituir-la? [S/N]: "
                ).strip().lower()

                if resposta in ["s", "si", "sí"]:

                    arcpy.management.Delete(
                        ruta_sortida
                    )

                    break

                elif resposta in ["n", "no"]:

                    print(
                        "Operació cancel·lada."
                    )

                    return

                else:

                    print(
                        "Respon S o N."
                    )

        # =====================================================
        # 6. EXECUCIÓ DEL SPATIAL JOIN
        # =====================================================

        print()
        print("=" * 70)
        print("EXECUTANT OPERACIÓ")
        print("=" * 70)

        print()
        print("Operació: Spatial Join")
        print("Relació espacial: INTERSECT")
        print()
        print("Capa target:")
        print(f"   {ruta_capa_2}")
        print()
        print("Capa join:")
        print(f"   {ruta_capa_1}")
        print()
        print("Resultat:")
        print(f"   {ruta_sortida}")
        print()

        arcpy.AddMessage(
            "Executant Spatial Join..."
        )

        # -----------------------------------------------------
        # Spatial Join
        #
        # TARGET = CAPA 2
        # JOIN   = CAPA 1
        #
        # KEEP_ALL:
        #   Manté totes les entitats de la CAPA 2.
        #
        # JOIN_ONE_TO_ONE:
        #   Una entitat de la CAPA 2 genera una sola entitat
        #   al resultat.
        #
        # INTERSECT:
        #   Només es relacionen geometries que intersecten.
        # -----------------------------------------------------

        resultat = arcpy.analysis.SpatialJoin(
            target_features=ruta_capa_2,
            join_features=ruta_capa_1,
            out_feature_class=ruta_sortida,
            join_operation="JOIN_ONE_TO_ONE",
            join_type="KEEP_ALL",
            match_option="INTERSECT"
        )

        # =====================================================
        # 7. COMPROVACIÓ
        # =====================================================

        print()
        print("=" * 70)
        print("OPERACIÓ COMPLETADA")
        print("=" * 70)

        print()
        print("✓ Resultat creat correctament.")
        print()
        print(f"Ruta:")
        print(f"   {resultat}")

        # -----------------------------------------------------
        # Nombre d'entitats
        # -----------------------------------------------------

        try:

            resultat_count = int(
                arcpy.management.GetCount(
                    resultat
                )[0]
            )

            capa_2_count = int(
                arcpy.management.GetCount(
                    ruta_capa_2
                )[0]
            )

            print()
            print(
                f"Entitats CAPA 2 original: "
                f"{capa_2_count}"
            )

            print(
                f"Entitats resultat: "
                f"{resultat_count}"
            )

        except Exception:

            pass

        print()
        print("=" * 70)
        print("FI")
        print("=" * 70)

    except arcpy.ExecuteError:

        print()
        print("=" * 70)
        print("ERROR D'ARCPY")
        print("=" * 70)
        print()

        missatge = arcpy.GetMessages(2)

        print(missatge)

        print()
        print(
            "Revisa el missatge anterior per identificar "
            "el problema."
        )

    except Exception as e:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print()

        print(
            f"Tipus d'error: {type(e).__name__}"
        )

        print(
            f"Missatge: {e}"
        )

        print()
        print(
            "L'operació no s'ha pogut completar."
        )


# =============================================================
# INICI
# =============================================================

if __name__ == "__main__":
    main()