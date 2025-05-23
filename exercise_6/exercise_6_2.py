from qgis.core import QgsVectorLayer, QgsField, QgsProject, QgsExpression, QgsFeatureRequest
from qgis.PyQt.QtCore import QVariant

# Define the paths to the shapefiles
pools_layer_path = "D:/study/UniMuenster/Sose2025/PythonInQgisandArcgis/week6/Data for Session 6/public_swimming_pools.shp"
districts_layer_path = "D:/study/UniMuenster/Sose2025/PythonInQgisandArcgis/week6/Muenster/Muenster_City_Districts.shp"

# Load the swimming pools layer
pools_layer = QgsVectorLayer(pools_layer_path, "public_swimming_pools", "ogr")
if not pools_layer.isValid():
    print("Swimming pools layer failed to load!")
    exit()

# Load the city districts layer
districts_layer = QgsVectorLayer(districts_layer_path, "city_districts", "ogr")
if not districts_layer.isValid():
    print("City districts layer failed to load!")
    exit()

# Start editing the swimming pools layer
pools_layer.startEditing()

# Modify the 'Type' column
for feature in pools_layer.getFeatures():
    type_value = feature['Type']
    if type_value == 'H':
        feature['Type'] = 'Hallenbad'
    elif type_value == 'F':
        feature['Type'] = 'Freibad'
    pools_layer.updateFeature(feature)

# Add a new column 'district'
pools_layer.dataProvider().addAttributes([QgsField('district', QVariant.String, len=50)])
pools_layer.updateFields()

# Identify the city district for each pool and update the 'district' column
for pool_feature in pools_layer.getFeatures():
    pool_geometry = pool_feature.geometry()
    request = QgsFeatureRequest().setFilterRect(pool_geometry.boundingBox())
    for district_feature in districts_layer.getFeatures(request):
        if pool_geometry.within(district_feature.geometry()):
            pool_feature['district'] = district_feature['name']  # Assuming the district name is in the 'name' field
            pools_layer.updateFeature(pool_feature)
            break

# Commit the changes
pools_layer.commitChanges()

# Add the modified layer to the map
QgsProject.instance().addMapLayer(pools_layer)

print("Swimming pools layer updated and added to the map successfully!")