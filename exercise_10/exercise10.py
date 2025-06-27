import arcpy

# Set the workspace environment (you might want to make this dynamic or set it within the tool properties later)
arcpy.env.workspace = r"arcpy2.gdb"

def find_nearest_bus_stop():
    """
    Find the nearest bus stop to an input point feature class.

    Args:
        None (input received from ArcGIS Pro tool parameter)

    Returns:
        None: Prints results to the Geoprocessing Window
    """
    try:
        # Get the input point feature class from the tool's first parameter
        input_point_fc = arcpy.GetParameterAsText(0)

        # Check if input feature class exists (this check might be redundant if Feature Set handles it, but good practice)
        if not arcpy.Exists(input_point_fc):
            arcpy.AddError(f"Input feature class {input_point_fc} does not exist!")
            return

        # Define the bus stops feature class (hardcoded as per requirements)
        bus_stops_fc = "stops_ms_mitte"

        if not arcpy.Exists(bus_stops_fc):
            arcpy.AddError(f"Bus stops feature class {bus_stops_fc} does not exist!")
            return

        # Run the Near analysis
        arcpy.AddMessage("Finding nearest bus stop...")
        # Note: The Near tool adds fields to the input feature class [cite: 13]
        arcpy.Near_analysis(
            in_features=input_point_fc,
            near_features=bus_stops_fc,
            search_radius="#",  # No search radius limit
            location="NO_LOCATION",
            angle="NO_ANGLE",
            method="GEODESIC"
        )

        # Use arcpy.da.SearchCursor to extract the distance and ObjectID [cite: 14]
        # Get the distance and nearest bus stop ID from the input feature
        with arcpy.da.SearchCursor(input_point_fc, ["NEAR_DIST", "NEAR_FID"]) as cursor:
            for row in cursor:
                near_distance = row[0]
                near_fid = row[1]
                break  # We only need the first row since we're working with a single point

        # Use a SearchCursor on 'stops_ms_mitte' with a where clause to get the name [cite: 15]
        # Get the bus stop name using the NEAR_FID
        with arcpy.da.SearchCursor(bus_stops_fc, ["NAME"], f"OBJECTID = {near_fid}") as cursor:
            for row in cursor:
                bus_stop_name = row[0]
                break

        # Output the results to the Geoprocessing Window using arcpy.AddMessage [cite: 6]
        arcpy.AddMessage(f"\nNearest bus stop found:")
        arcpy.AddMessage(f"Bus Stop Name: {bus_stop_name}")
        arcpy.AddMessage(f"Distance: {near_distance:.2f} meters")

    except Exception as e:
        arcpy.AddError(f"An error occurred: {str(e)}")

# Call the function
find_nearest_bus_stop()