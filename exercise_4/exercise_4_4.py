from qgis.core import *  
import processing  # Import the processing module for geospatial analysis

# Retrieve the layers from the current project
districts_layer = QgsProject.instance().mapLayersByName('Muenster_City_Districts')[0]  # Get the districts layer
schools_layer = QgsProject.instance().mapLayersByName('Schools')[0]  # Get the schools layer

# Define parameters for the processing algorithm
params = {
    'POLYGONS': districts_layer,  # Input polygons (districts)
    'POINTS': schools_layer,  # Input points (schools)
    'FIELD': 'SCHOOLS_COUNT',  # Field to store the count of schools
    'OUTPUT': 'memory:'  # Output layer will be stored in memory
}

# Run the processing algorithm to count points in polygons
result = processing.run("qgis:countpointsinpolygon", params)  # Execute the algorithm
output_layer = result['OUTPUT']  # Get the output layer from the result

# Print the results of the school count per district
for feature in output_layer.getFeatures():  # Iterate over each feature in the output layer
    district_name = feature['Name']  # Get the name of the district
    school_count = feature['SCHOOLS_COUNT']  # Get the count of schools in the district
    print(f"{district_name}: {school_count:.1f}")  # Print the district name and school count formatted to one decimal