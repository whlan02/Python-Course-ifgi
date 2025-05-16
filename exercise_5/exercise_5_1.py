from qgis.PyQt.QtWidgets import QInputDialog, QMessageBox
from qgis.core import QgsVectorLayer, QgsFeatureRequest, QgsDistanceArea, QgsProject

# Get the currently loaded layers by name
city_districts_layer = QgsProject.instance().mapLayersByName("Muenster_City_Districts")[0]
schools_layer = QgsProject.instance().mapLayersByName("Schools")[0]

# Get the list of district names
districts_names = [feature['Name'] for feature in city_districts_layer.getFeatures()]
districts_names.sort()  # Sort alphabetically

# Create the QInputDialog for district selection
parent = iface.mainWindow()
sDistrict, bOk = QInputDialog.getItem(parent, "District Names", "Select District:", districts_names)

# Check user interaction
if bOk:
    # User selected a district
    selected_district = sDistrict
    # Find the district feature
    district_request = QgsFeatureRequest().setFilterExpression(f'"Name" = \'{selected_district}\'')
    district_feature = next(city_districts_layer.getFeatures(district_request))
    
    # Find schools within the selected district using precise spatial check
    schools_within_district = []
    district_geometry = district_feature.geometry()
    for school in schools_layer.getFeatures():
        if district_geometry.contains(school.geometry()):
            schools_within_district.append(school)
    
    # Calculate distances to the centroid of the district
    district_centroid = district_feature.geometry().centroid().asPoint()
    da = QgsDistanceArea()
    da.setEllipsoid("ETRS89")  # use ETRS89 
    
    # Prepare the list of school names, types, and distances
    school_info_with_distances = []
    for school in schools_within_district:
        school_name = school['Name']
        school_type = school['SchoolType']
        school_point = school.geometry().centroid().asPoint()
        distance = da.measureLine(district_centroid, school_point) / 1000  # Convert to kilometers
        distance_rounded = round(distance, 2)
        school_info_with_distances.append(f"{school_name},{school_type} - Distance to district centrum: {distance_rounded} km")
    
    # Display the results in a QMessageBox
    school_info_text_with_distances = "\n".join(school_info_with_distances)
    QMessageBox.information(parent, f"Schools in {selected_district}", school_info_text_with_distances)
    
    # Select the matching schools and zoom to them
    school_ids = [school.id() for school in schools_within_district]
    schools_layer.selectByIds(school_ids, QgsVectorLayer.SetSelection)
    iface.mapCanvas().zoomToSelected(schools_layer)
else:
    # User cancelled the process
    QMessageBox.warning(parent, "Schools", "User cancelled")