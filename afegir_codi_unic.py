import os
import sys
import tkinter as tk
from tkinter import filedialog
import arcpy

def selecciona_gdb(titol="Selecciona una Geodatabase (.gdb)"):
    """Obre una finestra dialog de Tkinter per triar una Geodatabase (.gdb)."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)  # Força la finestra a aparèixer al davant
    gdb_path = filedialog.askdirectory(title=titol)
    root.destroy()
    
    if not gdb_path or not gdb_path.endswith(".gdb"):
        print("❌ Selecció cancel·lada o la carpeta triada no és una .gdb vàlida.")
        return None
    return gdb_path

def llistar_capes_gdb(gdb_path):
    """Llista totes les Feature Classes de la GDB (arrel i Feature Datasets)."""
    arcpy.env.workspace = gdb_path
    llista_capes = []  # Estructura: (Descripció d'origen, Feature Dataset o None, Nom FC, Camí complet)
    
    # 1. Capes a l'arrel de la GDB
    fcs_arrel = arcpy.ListFeatureClasses() or []
    for fc in fcs_arrel:
        cami = os.path.join(gdb_path, fc)
        llista_capes.append(("Arrel GDB", None, fc, cami))
        
    # 2. Capes dins de Feature Datasets
    fds = arcpy.ListDatasets(feature_type="Feature") or []
    for ds in fds:
        fcs_ds = arcpy.ListFeatureClasses(feature_dataset=ds) or []
        for fc in fcs_ds:
            cami = os.path.join(gdb_path, ds, fc)
            llista_capes.append((f"Dataset: {ds}", ds, fc, cami))
            
    return llista_capes

def llistar_feature_datasets(gdb_path):
    """Llista tots els Feature Datasets presents en una GDB."""
    arcpy.env.workspace = gdb_path
    return arcpy.ListDatasets(feature_type="Feature") or []

def executar_script():
    try:
        # =====================================================================
        # PAS 1: SELECCIÓ DE LA CAPA D'ENTRADA (DINÀMICA PER A CADA SHAPE/FC)
        # =====================================================================
        print("\n=== 📌 PAS 1: SELECCIÓ DE LA CAPA D'ENTRADA ===")
        print("S'obrirà una finestra per triar la Geodatabase (.gdb) d'origen...")
        gdb_entrada = selecciona_gdb("Selecciona la GDB d'origen")
        
        if not gdb_entrada:
            print("Operació avortada per l'usuari.")
            return

        capes = llistar_capes_gdb(gdb_entrada)
        if not capes:
            print("❌ No s'han trobat Feature Classes a la GDB seleccionada.")
            return

        print("\nCapes trobades a la GDB:")
        for idx, (origen, ds, fc, cami) in enumerate(capes, start=1):
            print(f"  [{idx}] {origen} -> {fc}")

        # Demanar el número de la capa a l'usuari
        mida = len(capes)
        opcio = 0
        while opcio < 1 or opcio > mida:
            try:
                opcio = int(input(f"\nEscriu el número de la capa amb la qual vols treballar (1-{mida}): "))
            except ValueError:
                print("❌ Si us plau, introdueix un número enter vàlid.")

        capa_seleccionada = capes[opcio - 1]
        nom_capa_in = capa_seleccionada[2]
        cami_capa_in = capa_seleccionada[3]
        print(f"✔ Capa seleccionada: {nom_capa_in}")

        # =====================================================================
        # PAS 2: DEFINICIÓ DE LA SORTIDA (GDB, FEATURE DATASET I NOM)
        # =====================================================================
        print("\n=== 📌 PAS 2: DEFINICIÓ DE LA SORTIDA ===")
        print("On vols desar la nova capa de resultat?")
        print("  [1] Utilitzar la MATEIXA GDB d'entrada")
        print("  [2] Seleccionar una ALTRA GDB de sortida")
        
        opcio_gdb = ""
        while opcio_gdb not in ["1", "2"]:
            opcio_gdb = input("Tria una opció (1 o 2): ").strip()

        if opcio_gdb == "1":
            gdb_sortida = gdb_entrada
        else:
            gdb_sortida = selecciona_gdb("Selecciona la GDB de sortida")
            if not gdb_sortida:
                print("Operació avortada.")
                return

        # Triar entre Arrel o Feature Dataset
        print("\nVols desar el resultat dins d'un Feature Dataset o a l'arrel?")
        print("  [1] A l'arrel de la GDB")
        print("  [2] Dins d'un Feature Dataset")
        
        opcio_ds = ""
        while opcio_ds not in ["1", "2"]:
            opcio_ds = input("Tria una opció (1 o 2): ").strip()

        ds_target = None
        if opcio_ds == "2":
            datasets_existents = llistar_feature_datasets(gdb_sortida)
            if datasets_existents:
                print("\nFeature Datasets disponibles a la GDB de sortida:")
                for idx, ds in enumerate(datasets_existents, start=1):
                    print(f"  [{idx}] {ds}")
                
                opcio_ds_num = 0
                mida_ds = len(datasets_existents)
                while opcio_ds_num < 1 or opcio_ds_num > mida_ds:
                    try:
                        opcio_ds_num = int(input(f"Tria el número del Feature Dataset (1-{mida_ds}): "))
                    except ValueError:
                        print("❌ Introdueix un número vàlid.")
                
                ds_target = datasets_existents[opcio_ds_num - 1]
            else:
                print("⚠️ No s'han trobat Feature Datasets a la GDB de sortida. Es desarà a l'arrel.")

        # Demanar nom de la nova Feature Class
        nom_capa_out = input("\nEscriu el nom per a la nova Feature Class de resultat: ").strip()
        while not nom_capa_out:
            nom_capa_out = input("El nom no pot estar buit. Reintrodueix-lo: ").strip()

        # Construcció del camí de sortida
        if ds_target:
            cami_capa_out = os.path.join(gdb_sortida, ds_target, nom_capa_out)
        else:
            cami_capa_out = os.path.join(gdb_sortida, nom_capa_out)

        # =====================================================================
        # PAS 3: EXECUCIÓ DEL GEOPROCÉS I CREACIÓ DEL CAMP ÚNIC
        # =====================================================================
        print("\n=== 📌 PAS 3: EXECUCIÓ DEL GEOPROCÉS ===")
        arcpy.env.overwriteOutput = True

        # 1. Copiar la capa original a la destinació
        print(f"Exportant/copiant entitats a: {cami_capa_out} ...")
        arcpy.management.CopyFeatures(cami_capa_in, cami_capa_out)
        print("✔ Capa copiada correctament.")

        # 2. Afegir el camp 'codig_unic'
        nom_camp = "codig_unic"
        print(f"Afegint el camp '{nom_camp}' (Tipus LONG)...")
        
        camps_existents = [f.name for f in arcpy.ListFields(cami_capa_out)]
        if nom_camp not in camps_existents:
            arcpy.management.AddField(
                in_table=cami_capa_out,
                field_name=nom_camp,
                field_type="LONG",
                field_alias="Codi Únic Map Series"
            )
            print(f"✔ Camp '{nom_camp}' creat amb èxit.")
        else:
            print(f"ℹ El camp '{nom_camp}' ja existia a la capa. Es recalcularan els valors.")

        # 3. Assignar un codi únic seqüencial (1..N) a cada polígon
        print("Assignant un codi únic a cada polígon/entitat...")
        
        comptador = 0
        with arcpy.da.UpdateCursor(cami_capa_out, [nom_camp]) as cursor:
            for row in cursor:
                comptador += 1
                row[0] = comptador
                cursor.updateRow(row)

        print("\n" + "="*60)
        print(f"🎉 PROCÉS FINALITZAT AMB ÈXIT!")
        print(f"✔ S'ha assignat el camp '{nom_camp}' a un total de {comptador} entitats.")
        print(f"📍 Ubicació del resultat: {cami_capa_out}")
        print("="*60)
        print("\n💡 Ara ja pots fer servir la capa creada i seleccionar el camp 'codig_unic' com a 'Index Layer Field' a les opcions de Map Series a ArcGIS Pro.")

    except arcpy.ExecuteError:
        print("\n❌ ERROR D'ARCPY DURANT L'EXECUCIÓ:")
        print(arcpy.GetMessages(2))
    except Exception as e:
        print(f"\n❌ ERROR INESPERAT DE PYTHON: {str(e)}")

if __name__ == "__main__":
    executar_script()