import arcpy
import os
import random
import math


def crear_poligono_azar(cx, cy, radio, num_vertices=6):
    """
    Crea un polígono aproximadamente circular con vértices aleatorios.
    Devuelve una lista de puntos cerrada.
    """

    puntos = []

    angulos = sorted(
        random.uniform(0, 2 * math.pi)
        for _ in range(num_vertices)
    )

    for angulo in angulos:
        r = random.uniform(radio * 0.7, radio)
        x = cx + math.cos(angulo) * r
        y = cy + math.sin(angulo) * r

        puntos.append(arcpy.Point(x, y))

    # Cerrar el polígono
    puntos.append(puntos[0])

    return arcpy.Array(puntos)


def main():

    print("=" * 60)
    print("      SCRIPT DE PRUEBA - GENERADOR DE POLIGONOS")
    print("=" * 60)

    # ---------------------------------------------------------
    # ESCRITORIO
    # ---------------------------------------------------------

    escritorio = os.path.join(
        os.path.expanduser("~"),
        "Desktop"
    )

    carpeta_prueba = os.path.join(
        escritorio,
        "prueba"
    )

    gdb = os.path.join(
        carpeta_prueba,
        "prueba.gdb"
    )

    # ---------------------------------------------------------
    # CREAR CARPETA
    # ---------------------------------------------------------

    if not os.path.exists(carpeta_prueba):
        os.makedirs(carpeta_prueba)

        print()
        print(f"Carpeta creada:")
        print(carpeta_prueba)

    else:
        print()
        print("La carpeta 'prueba' ya existe.")

    # ---------------------------------------------------------
    # CREAR GDB
    # ---------------------------------------------------------

    if not arcpy.Exists(gdb):

        print()
        print("Creando geodatabase...")

        arcpy.management.CreateFileGDB(
            carpeta_prueba,
            "prueba.gdb"
        )

        print("GDB creada correctamente.")

    else:

        print()
        print("La GDB ya existe.")

    # ---------------------------------------------------------
    # FEATURE CLASS
    # ---------------------------------------------------------

    nombre_fc = "poligonos_azar"

    fc = os.path.join(
        gdb,
        nombre_fc
    )

    # Si existe de una ejecución anterior, eliminarla
    if arcpy.Exists(fc):

        print()
        print("Eliminando resultado anterior...")

        arcpy.management.Delete(fc)

    print()
    print("Creando feature class...")

    arcpy.management.CreateFeatureclass(
        gdb,
        nombre_fc,
        "POLYGON",
        spatial_reference=25831
    )

    # ---------------------------------------------------------
    # CAMPOS
    # ---------------------------------------------------------

    arcpy.management.AddField(
        fc,
        "ID",
        "LONG"
    )

    arcpy.management.AddField(
        fc,
        "NOMBRE",
        "TEXT",
        field_length=50
    )

    arcpy.management.AddField(
        fc,
        "AREA_M2",
        "DOUBLE"
    )

    # ---------------------------------------------------------
    # GENERAR POLIGONOS
    # ---------------------------------------------------------

    print()
    print("Generando polígonos aleatorios...")
    print()

    random.seed()

    with arcpy.da.InsertCursor(
        fc,
        ["SHAPE@", "ID", "NOMBRE", "AREA_M2"]
    ) as cursor:

        for i in range(1, 11):

            # Centro aleatorio
            cx = random.uniform(0, 1000)
            cy = random.uniform(0, 1000)

            # Tamaño aleatorio
            radio = random.uniform(20, 100)

            # Crear geometría
            array = crear_poligono_azar(
                cx,
                cy,
                radio,
                random.randint(5, 8)
            )

            polygon = arcpy.Polygon(
                array,
                arcpy.SpatialReference(25831)
            )

            area = polygon.area

            cursor.insertRow(
                [
                    polygon,
                    i,
                    f"Poligono_{i}",
                    area
                ]
            )

            print(
                f"  ✓ Polígono {i:02d} "
                f"| Área: {area:,.2f} m²"
            )

    # ---------------------------------------------------------
    # RESULTADO
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print("      PROCESO FINALIZADO CORRECTAMENTE")
    print("=" * 60)

    print()
    print("Carpeta:")
    print(carpeta_prueba)

    print()
    print("Geodatabase:")
    print(gdb)

    print()
    print("Feature class:")
    print(fc)

    print()
    print("Polígonos creados: 10")

    print()
    print("=" * 60)

    input(
        "\nPulsa ENTER para cerrar esta ventana..."
    )


if __name__ == "__main__":
    main()
