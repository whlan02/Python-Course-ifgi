from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsGeometry, QgsProject
import csv
import sys

# increase the csv field size limit
maxInt = sys.maxsize
while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/2)

# Define the path to the CSV file
csv_file_path = "D:/study/UniMuenster/Sose2025/PythonInQgisandArcgis/week6/Data for Session 6/standard_land_value_muenster.csv"

# Create a new in-memory layer
layer = QgsVectorLayer('Polygon?crs=epsg:25832', 'temp_standard_land_value_muenster', 'memory')

# Check if the layer was successfully created
if not layer.isValid():
    print("Layer failed to load!")
else:
    # Add fields to the layer
    provider = layer.dataProvider()
    provider.addAttributes([QgsField('standard_land_value', QVariant.Double),
                            QgsField('type', QVariant.String),
                            QgsField('district', QVariant.String)])
    layer.updateFields()

    # Open the CSV file and read its contents
    with open(csv_file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')  # use ; as delimiter
        next(csvreader)  # Skip the header line

        for row in csvreader:
            # Extract the information from the CSV row
            standard_land_value = float(row[0].replace(',', '.'))
            land_type = row[1]
            district = row[2]
            wkt_geometry = row[3]

            # Create a new feature
            feature = QgsFeature(layer.fields())
            feature.setAttribute('standard_land_value', standard_land_value)
            feature.setAttribute('type', land_type)
            feature.setAttribute('district', district)

            # Set the geometry from the WKT string
            geometry = QgsGeometry.fromWkt(wkt_geometry)
            feature.setGeometry(geometry)

            # Add the feature to the layer
            provider.addFeature(feature)

    # Update the layer's extent
    layer.updateExtents()

    # Add the layer to the map
    QgsProject.instance().addMapLayer(layer)

    print("Layer created and added to the map successfully!")