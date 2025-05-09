from qgis.core import QgsProject
import csv  # Import the CSV module for handling CSV file operations

# Set the layer name for the schools layer
layer_name = 'Schools'
layer = QgsProject.instance().mapLayersByName(layer_name)[0]  # Retrieve the layer by name

# Specify the output CSV file path (adjust this path to your needs)
output_csv_path = 'D:/study/UniMuenster/Sose2025/PythonInQgisandArcgis/week4/SchoolReport.csv'

# Open the CSV file for writing with specified encoding and newline handling
with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=';')  # Create a CSV writer object with a semicolon delimiter
    
    # Write the header row to the CSV file
    csv_writer.writerow(['Name', 'X', 'Y'])
    
    # Iterate over selected features in the layer
    for feature in layer.selectedFeatures():
        school_name = feature['Name']  # Get the school name from the feature
        geom = feature.geometry()  # Get the geometry of the feature
        x_coord = geom.asPoint().x()  # Extract the X coordinate from the geometry
        y_coord = geom.asPoint().y()  # Extract the Y coordinate from the geometry
        
        # Write the school data (name and coordinates) to the CSV file
        csv_writer.writerow([school_name, x_coord, y_coord])

# Print a confirmation message indicating the data has been written
print(f"School data has been written to {output_csv_path}")