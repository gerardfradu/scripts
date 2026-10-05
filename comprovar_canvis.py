```python
# -*- coding: utf-8 -*-
"""
COMPARADOR DE GEOMETRIES I CAMPS EN ARCGIS PRO (ArcPy)

CRITERI DE COMPARACIÓ:

    CANVIAT = "No"
        -> La geometria de l'ORIGINAL existeix exactament igual
           a la capa NOVA/REVISADA
        I
        -> El camp seleccionat té el mateix valor a l'ORIGINAL
           i a la NOVA/REVISADA.

    CANVIAT = "Si"
        -> La geometria no existeix exactament igual a la capa
           NOVA/REVISADA
        O
        -> El valor del camp seleccionat ha canviat.

El script:
1. Selecciona la GDB ORIGINAL.
2. Selecciona la Feature Class ORIGINAL.
3. Selecciona la GDB NOVA/REVISADA.
4. Selecciona la Feature Class NOVA/REVISADA.
5. Permet seleccionar quin camp es vol comprovar.
6. Defineix la GDB/capa de sortida.
7. Copia la capa ORIGINAL.
8. Afegeix el camp CANVIAT.
9. Compara cada geometria ORIGINAL amb les geometries NOVES.
10. Quan troba la mateixa geometria, compara també el camp seleccionat.
11. Marca:
       "No" = geometria i camp iguals.
       "Si" = geometria o camp diferents.
12. Afegeix el resultat al mapa actiu d'ArcGIS Pro, si és possible.
"""

import os
import sys
import traceback
import tkinter as tk
from tkinter import filedialog

import arcpy


# ===========================================================================
# CONFIGURACIÓ DE LA FINESTRA DE SELECCIÓ
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

def seleccionar_gdb(titol="Selecciona una Geodatabase (.gdb)"):
    """Obre un cercador de Windows i permet seleccionar una GDB."""

    print("\n" + "=" * 75)
    print(titol)
    print("=" * 75)

    ruta_gdb = filedialog.askdirectory(title=titol)

    if not ruta_gdb:
        print("[-] No s'ha seleccionat cap GDB.")
        return None

    ruta_gdb = os.path.normpath(ruta_gdb)

    if not ruta_gdb.lower().endswith(".gdb"):
        print("[-] La carpeta seleccionada no és una Geodatabase (.gdb).")
        print(f"    Ruta: {ruta_gdb}")
        return None

    if not arcpy.Exists(ruta_gdb):
        print("[-] ArcPy no troba la GDB seleccionada.")
        print(f"    Ruta: {ruta_gdb}")
        return None

    print("[OK] GDB seleccionada:")
    print(f"     {ruta_gdb}")

    return ruta_gdb


# ===========================================================================
# LLISTAR CAPES D'UNA GDB
# ===========================================================================

def llistar_capes_gdb(ruta_gdb):
    """
    Llista les Feature Classes:
    - a l'arrel de la GDB
    - dins dels Feature Datasets
    """

    print("\n" + "-" * 75)
    print(f"EXPLORANT GDB: {os.path.basename(ruta_gdb)}")
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
            capes_arrel = arcpy.ListFeatureClasses() or []
        except Exception as e:
            print(f"[!] Error llistant les capes de l'arrel: {e}")
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

                print(f"    [{comptador}] {fc}")

                comptador += 1

        else:
            print("    No hi ha Feature Classes a l'arrel.")

        # -------------------------------------------------------------------
        # FEATURE DATASETS
        # -------------------------------------------------------------------

        print("\n[+] Buscant Feature Datasets...")

        try:
            datasets = arcpy.ListDatasets(
                feature_type="Feature"
            ) or []
        except Exception as e:
            print(f"[!] Error llistant Feature Datasets: {e}")
            datasets = []

        if datasets:

            for ds in datasets:

                print(f"\n  [Dataset: {ds}]")

                try:
                    capes_ds = arcpy.ListFeatureClasses(
                        feature_dataset=ds
                    ) or []
                except Exception as e:
                    print(
                        f"    [!] Error llegint el Dataset "
                        f"'{ds}': {e}"
                    )
                    continue

                if not capes_ds:
                    print("    No hi ha Feature Classes.")

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

                    print(f"    [{comptador}] {fc}")

                    comptador += 1

        else:
            print("    No hi ha Feature Datasets.")

        # -------------------------------------------------------------------
        # COMPROVACIÓ FINAL
        # -------------------------------------------------------------------

        if not llista_capes:

            print("\n[-] No s'ha trobat cap Feature Class.")
            return []

        print(
            f"\n[OK] S'han trobat "
            f"{len(llista_capes)} Feature Class(s)."
        )

        return llista_capes

    except Exception as e:

        print("\n[X] ERROR EXPLORANT LA GDB")
        print(f"    {e}")
        traceback.print_exc()

        return []


# ===========================================================================
# SELECCIONAR CAPA
# ===========================================================================

def seleccionar_capa(ruta_gdb, rol_capa):
    """Mostra les capes disponibles i permet seleccionar-ne una."""

    llista_capes = llistar_capes_gdb(ruta_gdb)

    if not llista_capes:
        return None

    print("\n" + "-" * 75)
    print(f"SELECCIÓ DE LA CAPA {rol_capa}")
    print("-" * 75)

    while True:

        try:

            entrada = input(
                f"\nEscriu el NÚMERO de la capa {rol_capa}: "
            ).strip()

            if not entrada:
                print("[-] Has d'escriure un número.")
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

                print("\n[OK] Capa seleccionada:")
                print(f"     {capa_triada[1]}")
                print(f"     {ruta_capa}")

                if not arcpy.Exists(ruta_capa):
                    print(
                        "[-] ArcPy no troba la Feature Class seleccionada."
                    )
                    return None

                return ruta_capa

            print("[-] Número no vàlid. Torna-ho a provar.")

        except ValueError:
            print("[-] Escriu un número enter vàlid.")

        except KeyboardInterrupt:
            print("\n[!] Procés cancel·lat per l'usuari.")
            return None


# ===========================================================================
# SELECCIONAR CAMP A COMPROVAR
# ===========================================================================

def seleccionar_camp(capa_original, capa_nova):
    """
    Mostra els camps de la capa ORIGINAL i permet seleccionar
    quin camp es vol comprovar també a la capa NOVA.

    Només es mostren camps que existeixen a les dues capes.
    """

    print("\n")
    print("=" * 75)
    print("  SELECCIÓ DEL CAMP A COMPROVAR")
    print("=" * 75)

    print(
        "\nEs mostrarà una llista dels camps disponibles "
        "a la capa ORIGINAL."
    )

    print(
        "Només es podran seleccionar camps que també "
        "existeixin a la capa NOVA/REVISADA."
    )

    camps_original = arcpy.ListFields(capa_original)
    camps_nova = arcpy.ListFields(capa_nova)

    noms_camps_nova = {
        camp.name.upper()
        for camp in camps_nova
    }

    camps_comuns = []

    for camp in camps_original:

        # ---------------------------------------------------------------
        # No mostrem ObjectID ni Shape
        # ---------------------------------------------------------------

        if camp.type.upper() in (
            "OID",
            "GEOMETRY",
            "RASTER",
            "BLOB"
        ):
            continue

        if camp.name.upper() in noms_camps_nova:

            camps_comuns.append(camp)

    if not camps_comuns:

        raise RuntimeError(
            "No hi ha cap camp comú entre la capa ORIGINAL "
            "i la capa NOVA que es pugui comprovar."
        )

    print("\nCAMPOS DISPONIBLES:")
    print("-" * 75)

    for idx, camp in enumerate(camps_comuns, start=1):

        print(
            f"  [{idx}] "
            f"{camp.name}"
            f"    | Tipus: {camp.type}"
            f"    | Alias: {camp.aliasName}"
        )

    print("-" * 75)

    while True:

        try:

            entrada = input(
                "\nEscriu el NÚMERO del camp que vols comprovar: "
            ).strip()

            if not entrada:
                print("[-] Has d'escriure un número.")
                continue

            opcio = int(entrada)

            if 1 <= opcio <= len(camps_comuns):

                camp_seleccionat = camps_comuns[opcio - 1]

                print("\n[OK] Camp seleccionat:")
                print(f"     Nom:   {camp_seleccionat.name}")
                print(f"     Alias: {camp_seleccionat.aliasName}")
                print(f"     Tipus:  {camp_seleccionat.type}")

                return camp_seleccionat.name

            print("[-] Número no vàlid.")

        except ValueError:

            print("[-] Escriu un número enter vàlid.")

        except KeyboardInterrupt:

            print("\n[!] Procés cancel·lat per l'usuari.")
            return None


# ===========================================================================
# DEFINIR SORTIDA
# ===========================================================================

def definir_destinacio_sortida(gdb_origen_default):
    """Defineix GDB, Feature Dataset i nom de la capa de resultat."""

    print("\n" + "=" * 75)
    print("DEFINICIÓ DE LA CAPA DE SORTIDA")
    print("=" * 75)

    # -----------------------------------------------------------------------
    # GDB DE SORTIDA
    # -----------------------------------------------------------------------

    print("\n1. Utilitzar la mateixa GDB d'origen")
    print("2. Seleccionar una altra GDB de sortida")

    opcio_gdb = input(
        "Tria una opció (1 o 2) [Per defecte: 1]: "
    ).strip()

    if opcio_gdb == "2":

        gdb_sortida = seleccionar_gdb(
            "Selecciona la Geodatabase de SORTIDA (.gdb)"
        )

        if not gdb_sortida:
            return None, None

    else:

        gdb_sortida = gdb_origen_default

    arcpy.env.workspace = gdb_sortida

    # -----------------------------------------------------------------------
    # FEATURE DATASET
    # -----------------------------------------------------------------------

    print("\nOn vols desar el resultat?")
    print("1. A l'arrel de la GDB")
    print("2. Dins d'un Feature Dataset existent")

    opcio_ds = input(
        "Tria una opció (1 o 2) [Per defecte: 1]: "
    ).strip()

    ds_desti = None

    if opcio_ds == "2":

        try:
            datasets = arcpy.ListDatasets(
                feature_type="Feature"
            ) or []
        except Exception as e:
            print(f"[!] Error obtenint Feature Datasets: {e}")
            datasets = []

        if datasets:

            print("\nFeature Datasets disponibles:")

            for idx, ds in enumerate(datasets, start=1):
                print(f"  [{idx}] {ds}")

            while True:

                try:

                    num_ds = int(
                        input(
                            "Selecciona el número del Feature Dataset: "
                        ).strip()
                    )

                    if 1 <= num_ds <= len(datasets):

                        ds_desti = datasets[num_ds - 1]
                        break

                    print("[-] Opció fora de rang.")

                except ValueError:
                    print("[-] Escriu un número vàlid.")

        else:

            print(
                "[!] No hi ha Feature Datasets. "
                "Es desarà a l'arrel."
            )

    # -----------------------------------------------------------------------
    # NOM DE LA CAPA
    # -----------------------------------------------------------------------

    while True:

        nom_nova_capa = input(
            "\nEscriu el NOM de la nova Feature Class de resultat: "
        ).strip()

        if not nom_nova_capa:

            print("[-] El nom no pot estar buit.")
            continue

        try:

            nom_nova_capa = arcpy.ValidateTableName(
                nom_nova_capa,
                gdb_sortida
            )

        except Exception as e:

            print(f"[!] Error validant el nom: {e}")
            return None, None

        break

    # -----------------------------------------------------------------------
    # RUTA FINAL
    # -----------------------------------------------------------------------

    if ds_desti:

        ruta_sortida = os.path.join(
            gdb_sortida,
            ds_desti,
            nom_nova_capa
        )

    else:

        ruta_sortida = os.path.join(
            gdb_sortida,
            nom_nova_capa
        )

    print("\n[OK] Sortida configurada:")
    print(f"     GDB:      {gdb_sortida}")
    print(
        f"     Dataset:  "
        f"{ds_desti if ds_desti else '(arrel)'}"
    )
    print(f"     Capa:     {nom_nova_capa}")
    print(f"     Ruta:     {ruta_sortida}")

    return gdb_sortida, ruta_sortida


# ===========================================================================
# COMPROVAR CAPES
# ===========================================================================

def comprovar_capes(capa_original, capa_nova):
    """Comprova que les dues capes existeixen."""

    print("\n" + "-" * 75)
    print("COMPROVANT LES CAPES")
    print("-" * 75)

    if not capa_original:
        raise RuntimeError(
            "No s'ha seleccionat la capa ORIGINAL."
        )

    if not capa_nova:
        raise RuntimeError(
            "No s'ha seleccionat la capa NOVA."
        )

    if not arcpy.Exists(capa_original):
        raise RuntimeError(
            f"No existeix la capa ORIGINAL:\n{capa_original}"
        )

    if not arcpy.Exists(capa_nova):
        raise RuntimeError(
            f"No existeix la capa NOVA:\n{capa_nova}"
        )

    desc_original = arcpy.Describe(capa_original)
    desc_nova = arcpy.Describe(capa_nova)

    print("[OK] Capa ORIGINAL:")
    print(f"     {capa_original}")

    print("[OK] Capa NOVA:")
    print(f"     {capa_nova}")

    print("\n[+] Tipus geomètric:")
    print(
        f"    Original: "
        f"{getattr(desc_original, 'shapeType', 'N/D')}"
    )
    print(
        f"    Nova:    "
        f"{getattr(desc_nova, 'shapeType', 'N/D')}"
    )

    sr_original = getattr(
        desc_original,
        "spatialReference",
        None
    )

    sr_nova = getattr(
        desc_nova,
        "spatialReference",
        None
    )

    print("\n[+] Sistema de coordenades:")

    if sr_original:

        print(
            f"    Original: "
            f"{sr_original.name} "
            f"(WKID {sr_original.factoryCode})"
        )

    if sr_nova:

        print(
            f"    Nova:    "
            f"{sr_nova.name} "
            f"(WKID {sr_nova.factoryCode})"
        )

    print("\n[OK] Comprovació finalitzada.")


# ===========================================================================
# MAIN
# ===========================================================================

def main():

    try:

        print("\n")
        print("=" * 75)
        print("  COMPARADOR DE GEOMETRIES I CAMPS EN ARCGIS PRO")
        print("=" * 75)

        # ===================================================================
        # PAS 1 - GDB ORIGINAL
        # ===================================================================

        print("\n>>> PAS 1: SELECCIÓ DE LA GDB ORIGINAL")

        gdb_original = seleccionar_gdb(
            "Selecciona la GDB de la CAPA ORIGINAL"
        )

        if not gdb_original:
            return

        # ===================================================================
        # PAS 2 - CAPA ORIGINAL
        # ===================================================================

        print("\n>>> PAS 2: SELECCIÓ DE LA CAPA ORIGINAL")

        capa_original = seleccionar_capa(
            gdb_original,
            "ORIGINAL"
        )

        if not capa_original:
            return

        print(
            "\n[OK] CAPA ORIGINAL SELECCIONADA CORRECTAMENT."
        )

        # ===================================================================
        # PAS 3 - GDB NOVA
        # ===================================================================

        print(
            "\n>>> PAS 3: ARA S'OBRIRÀ EL SELECTOR "
            "DE LA GDB NOVA/REVISADA"
        )

        gdb_nova = seleccionar_gdb(
            "Selecciona la GDB de la CAPA NOVA/REVISADA"
        )

        if not gdb_nova:
            return

        # ===================================================================
        # PAS 4 - CAPA NOVA
        # ===================================================================

        print("\n>>> PAS 4: SELECCIÓ DE LA CAPA NOVA/REVISADA")

        capa_nova = seleccionar_capa(
            gdb_nova,
            "NOVA/REVISADA"
        )

        if not capa_nova:
            return

        print(
            "\n[OK] CAPA NOVA/REVISADA SELECCIONADA CORRECTAMENT."
        )

        # ===================================================================
        # PAS 5 - COMPROVACIONS
        # ===================================================================

        comprovar_capes(
            capa_original,
            capa_nova
        )

        # ===================================================================
        # PAS 6 - SELECCIONAR CAMP
        # ===================================================================

        print(
            "\n>>> PAS 5: SELECCIÓ DEL CAMP A COMPROVAR"
        )

        camp_comprovar = seleccionar_camp(
            capa_original,
            capa_nova
        )

        if not camp_comprovar:
            return

        # ===================================================================
        # PAS 7 - DEFINIR SORTIDA
        # ===================================================================

        print("\n>>> PAS 6: DEFINICIÓ DE LA SORTIDA")

        gdb_sortida, ruta_capa_sortida = (
            definir_destinacio_sortida(
                gdb_original
            )
        )

        if not gdb_sortida or not ruta_capa_sortida:
            return

        # ===================================================================
        # PAS 8 - COPIAR CAPA ORIGINAL
        # ===================================================================

        print("\n")
        print("=" * 75)
        print("  EXECUTANT LA COMPARACIÓ")
        print("=" * 75)

        arcpy.env.overwriteOutput = True

        print("\n[1/5] Copiant la capa ORIGINAL...")

        arcpy.management.CopyFeatures(
            capa_original,
            ruta_capa_sortida
        )

        print("[OK] Capa original copiada.")

        # ===================================================================
        # PAS 9 - CREAR CAMP CANVIAT
        # ===================================================================

        print("\n[2/5] Preparant el camp CANVIAT...")

        camp_nom = "CANVIAT"

        camps_existents = [
            f.name.upper()
            for f in arcpy.ListFields(ruta_capa_sortida)
        ]

        if camp_nom.upper() not in camps_existents:

            arcpy.management.AddField(
                in_table=ruta_capa_sortida,
                field_name=camp_nom,
                field_type="TEXT",
                field_length=10,
                field_alias="S'ha modificat?"
            )

            print("[OK] Camp CANVIAT creat.")

        else:

            print(
                "[!] El camp CANVIAT ja existeix. "
                "S'utilitzarà el camp existent."
            )

        # ===================================================================
        # PAS 10 - CARREGAR GEOMETRIES I CAMPS NOUS
        # ===================================================================

        print(
            "\n[3/5] Carregant les geometries i el camp "
            f"'{camp_comprovar}' de la capa NOVA..."
        )

        geometries_noves = []

        with arcpy.da.SearchCursor(
            capa_nova,
            ["SHAPE@", camp_comprovar]
        ) as cursor_nova:

            for row in cursor_nova:

                geom_nova = row[0]
                valor_nou = row[1]

                if geom_nova is not None:

                    geometries_noves.append(
                        (
                            geom_nova,
                            valor_nou
                        )
                    )

        print(
            f"[OK] S'han carregat "
            f"{len(geometries_noves)} geometries."
        )

        # ===================================================================
        # PAS 11 - COMPARACIÓ
        # ===================================================================

        print(
            "\n[4/5] Comparant cada geometria ORIGINAL "
            "amb la capa NOVA..."
        )

        print(
            f"      També es comprovarà el camp: "
            f"'{camp_comprovar}'"
        )

        total_poligons = 0

        poligons_sense_canvi = 0
        poligons_canviats = 0

        canvis_geometria = 0
        canvis_camp = 0

        with arcpy.da.UpdateCursor(
            ruta_capa_sortida,
            ["SHAPE@", camp_comprovar, camp_nom]
        ) as cursor_update:

            for row in cursor_update:

                total_poligons += 1

                if total_poligons % 1000 == 0:

                    print(
                        f"    Polígons processats: "
                        f"{total_poligons}"
                    )

                geom_original = row[0]
                valor_original = row[1]

                existeix_igual = False
                camp_igual = False

                # -----------------------------------------------------------
                # BUSCAR LA GEOMETRIA IGUAL
                # -----------------------------------------------------------

                if geom_original is not None:

                    for geom_nova, valor_nou in geometries_noves:

                        try:

                            if geom_original.equals(
                                geom_nova
                            ):

                                existeix_igual = True

                                # ------------------------------------------------
                                # COMPARAR EL CAMP
                                # ------------------------------------------------

                                if valor_original == valor_nou:

                                    camp_igual = True

                                else:

                                    camp_igual = False

                                break

                        except Exception:
                            continue

                # -----------------------------------------------------------
                # RESULTAT
                #
                # GEOMETRIA IGUAL + CAMP IGUAL
                #       -> NO
                #
                # GEOMETRIA DIFERENT
                #       -> SI
                #
                # GEOMETRIA IGUAL + CAMP DIFERENT
                #       -> SI
                # -----------------------------------------------------------

                if existeix_igual and camp_igual:

                    row[2] = "No"

                    poligons_sense_canvi += 1

                else:

                    row[2] = "Si"

                    poligons_canviats += 1

                    # -------------------------------------------------------
                    # Estadístiques del tipus de canvi
                    # -------------------------------------------------------

                    if not existeix_igual:

                        canvis_geometria += 1

                    elif not camp_igual:

                        canvis_camp += 1

                cursor_update.updateRow(row)

        # ===================================================================
        # RESULTATS
        # ===================================================================

        print("\n")
        print("=" * 75)
        print("  RESULTAT DEL PROCESSAMENT")
        print("=" * 75)

        print(
            f"  - Total polígons analitzats: "
            f"{total_poligons}"
        )

        print(
            f"  - Polígons sense canvis ('No'): "
            f"{poligons_sense_canvi}"
        )

        print(
            f"  - Polígons canviats ('Si'): "
            f"{poligons_canviats}"
        )

        print("\n  TIPUS DE CANVI:")

        print(
            f"  - Canvi de geometria: "
            f"{canvis_geometria}"
        )

        print(
            f"  - Canvi únicament del camp "
            f"'{camp_comprovar}': "
            f"{canvis_camp}"
        )

        print(
            f"\n  - Camp comprovat: "
            f"{camp_comprovar}"
        )

        print(
            f"\n  - Capa resultat:"
            f"\n    {ruta_capa_sortida}"
        )

        # ===================================================================
        # AFEGIR AL MAPA ACTIU
        # ===================================================================

        print(
            "\n>>> Intentant afegir la capa "
            "resultat al mapa actiu..."
        )

        try:

            aprx = arcpy.mp.ArcGISProject("CURRENT")
            mapa_actiu = aprx.activeMap

            if mapa_actiu:

                mapa_actiu.addDataFromPath(
                    ruta_capa_sortida
                )

                print(
                    f"[OK] Capa afegida al mapa: "
                    f"{mapa_actiu.name}"
                )

            else:

                print(
                    "[!] No hi ha cap mapa actiu."
                )

        except Exception as e_mapa:

            print(
                "[!] No s'ha pogut afegir "
                "automàticament al mapa actiu."
            )

            print(f"    Motiu: {e_mapa}")

        # ===================================================================
        # FINAL
        # ===================================================================

        print("\n")
        print("=" * 75)
        print("  PROCÉS FINALITZAT CORRECTAMENT")
        print("=" * 75)

    except arcpy.ExecuteError:

        print("\n")
        print("=" * 75)
        print("  ERROR D'ARCPY")
        print("=" * 75)

        print(arcpy.GetMessages(2))
        traceback.print_exc()

    except KeyboardInterrupt:

        print("\n[!] Procés cancel·lat per l'usuari.")

    except Exception as e:

        print("\n")
        print("=" * 75)
        print("  ERROR GENERAL DE PYTHON")
        print("=" * 75)

        print(f"Error: {e}")
        print("\nDetalls:")
        traceback.print_exc()

    finally:

        try:
            root.destroy()
        except Exception:
            pass


# ===========================================================================
# EXECUCIÓ
# ===========================================================================

if __name__ == "__main__":
    main()
```
