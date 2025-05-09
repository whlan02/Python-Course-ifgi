# Import modules
from qgis.core import QgsVectorLayer, QgsProject
from qgis.core import *
import os

# Path to the Muenster folder and project
muenster_folder = "D:/study/UniMuenster/Sose2025/PythonInQgisandArcgis/week4/Muenster"
project_path = "D:/study/UniMuenster/Sose2025/PythonInQgisandArcgis/week4/myFirstProject.qgz"

# Create QGIS instance and start new project
project = QgsProject.instance()

# Get all shapefiles from Muenster folder using os.listdir()
shapefile_paths = []
for file in os.listdir(muenster_folder):
    if file.lower().endswith('.shp'):
        # Create complete path
        full_path = os.path.join(muenster_folder, file)
        shapefile_paths.append(full_path)
        print(f"Found shapefile: {full_path}")

# Add each shapefile to the project
for shapefile_path in shapefile_paths:
    # Get original filename without extension using os.path.basename()
    layer_name = os.path.splitext(os.path.basename(shapefile_path))[0]
    
    # Create layer
    layer = QgsVectorLayer(shapefile_path, layer_name, "ogr")
    
    # Check if layer is valid
    if not layer.isValid():
        print(f"Error loading the layer: {layer_name}")
    else:
        # Add layer to project
        project.addMapLayer(layer)
        print(f"Added layer: {layer_name}")

# Save project
project.write(project_path)
print("Project saved successfully!")
