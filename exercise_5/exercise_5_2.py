from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
from qgis.core import QgsVectorLayer, QgsFeatureRequest, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsPointXY, QgsGeometry
from qgis.utils import iface

# Get the currently loaded layer by name
city_districts_layer = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]

# Create the QInputDialog for coordinate input
parent = iface.mainWindow()
sCoords, bOk = QInputDialog.getText(parent, "Coordinates", "Enter coordinates as latitude, longitude", text="51.96066,7.62476")

# Check user interaction
if bOk:
    # User entered coordinates
    try:
        # Parse the input coordinates
        lat, lon = map(float, sCoords.split(','))

        # Define the CRS for WGS84 and ETRS89 32N
        crsWGS84 = QgsCoordinateReferenceSystem(4326)  # WGS 84
        crsETRS89_32N = QgsCoordinateReferenceSystem(25832)  # ETRS89 / UTM zone 32N

        # Create a coordinate transform
        transformation = QgsCoordinateTransform(crsWGS84, crsETRS89_32N, QgsProject.instance())

        # Transform the input coordinates to ETRS89 32N
        pointWGS84 = QgsPointXY(lon, lat)
        pointETRS89_32N = transformation.transform(pointWGS84)

        # Create a point geometry
        point_geometry = QgsGeometry.fromPointXY(pointETRS89_32N)

        # Check if the point falls within any city district using spatial relationship
        found_district = False
        for feature in city_districts_layer.getFeatures():
            if feature.geometry().contains(point_geometry):
                district_name = feature['Name']
                QMessageBox.information(parent, "Geoguesser Result", f"The coordinates fall within the district: {district_name}")
                found_district = True
                break

        if not found_district:
            # Point is not within any city district
            QMessageBox.information(parent, "Geoguesser Result", "The coordinates do not fall within any city district.")

    except ValueError:
        # Handle invalid input
        QMessageBox.warning(parent, "Geoguesser Error", "Invalid input format. Please enter coordinates as latitude,longitude.")
else:
    # User cancelled the process
    QMessageBox.warning(parent, "Geoguesser", "User cancelled")