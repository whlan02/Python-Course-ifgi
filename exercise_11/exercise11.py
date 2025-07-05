import arcpy
import time

# Set the workspace environment 
arcpy.env.workspace = r"arcpy2.gdb"

def find_nearest_bus_stop():
    """
    Find the nearest bus stop to an input point feature class.
    With user-configurable feature class, field filtering, and progress indication.
    """
    try:
        # Initialize progress indicator
        arcpy.SetProgressor("step", "Initializing analysis...", 0, 6, 1)
        time.sleep(2)  # 2 second delay for observation
        
        # Get the input parameters from the tool
        input_point_fc = arcpy.GetParameterAsText(0)  # Input point feature class
        bus_stops_fc = arcpy.GetParameterAsText(1)    # Bus stops feature class
        name_field = arcpy.GetParameterAsText(2)      # Name field for filtering
        name_value = arcpy.GetParameterAsText(3)      # Specific name value to filter by

        # Step 1: Validate input parameters
        arcpy.SetProgressorLabel("Validating input parameters...")
        arcpy.SetProgressorPosition(1)
        time.sleep(2)
        
        # Check if input feature class exists
        if not arcpy.Exists(input_point_fc):
            arcpy.AddError(f"Input feature class {input_point_fc} does not exist!")
            return

        # Check if bus stops feature class exists
        if not arcpy.Exists(bus_stops_fc):
            arcpy.AddError(f"Bus stops feature class {bus_stops_fc} does not exist!")
            return

        # Validate that the name field exists in the feature class
        field_names = [field.name for field in arcpy.ListFields(bus_stops_fc)]
        if name_field not in field_names:
            arcpy.AddError(f"Field '{name_field}' does not exist in {bus_stops_fc}!")
            return

        arcpy.AddMessage(f"Using feature class: {bus_stops_fc}")
        arcpy.AddMessage(f"Filtering by field: {name_field} = '{name_value}'")

        # Step 2: Create filtered layer
        arcpy.SetProgressorLabel("Creating filtered layer...")
        arcpy.SetProgressorPosition(2)
        time.sleep(2)
        
        # Create a layer with the specified filter
        filtered_layer = "filtered_stops_layer"
        where_clause = f"{name_field} = '{name_value}'"
        
        # Make feature layer with the filter applied
        arcpy.MakeFeatureLayer_management(
            in_features=bus_stops_fc,
            out_layer=filtered_layer,
            where_clause=where_clause
        )
        
        # Check if any features match the filter
        result = arcpy.GetCount_management(filtered_layer)
        feature_count = int(result.getOutput(0))
        
        if feature_count == 0:
            arcpy.AddError(f"No features found with {name_field} = '{name_value}'")
            return
            
        arcpy.AddMessage(f"Found {feature_count} feature(s) matching the filter criteria")

        # Step 3: Prepare for Near analysis
        arcpy.SetProgressorLabel("Preparing Near analysis...")
        arcpy.SetProgressorPosition(3)
        time.sleep(2)

        # Step 4: Run the Near analysis
        arcpy.SetProgressorLabel("Running Near analysis...")
        arcpy.SetProgressorPosition(4)
        time.sleep(2)
        
        arcpy.AddMessage("Finding nearest bus stop...")
        # Note: The Near tool adds fields to the input feature class
        arcpy.Near_analysis(
            in_features=input_point_fc,
            near_features=filtered_layer,  # Use the filtered layer instead of the full feature class
            search_radius="#",  # No search radius limit
            location="NO_LOCATION",
            angle="NO_ANGLE",
            method="GEODESIC"
        )

        # Step 5: Extract results
        arcpy.SetProgressorLabel("Extracting analysis results...")
        arcpy.SetProgressorPosition(5)
        time.sleep(2)
        
        # Use arcpy.da.SearchCursor to extract the distance and ObjectID
        # Get the distance and nearest bus stop ID from the input feature
        with arcpy.da.SearchCursor(input_point_fc, ["NEAR_DIST", "NEAR_FID"]) as cursor:
            for row in cursor:
                near_distance = row[0]
                near_fid = row[1]
                break  # We only need the first row since we're working with a single point

        # Check if a near feature was found
        if near_fid == -1:
            arcpy.AddError("No nearby features found within the search criteria")
            return

        # Use a SearchCursor on the original feature class to get the name
        # Get the bus stop name using the NEAR_FID
        with arcpy.da.SearchCursor(bus_stops_fc, [name_field], f"OBJECTID = {near_fid}") as cursor:
            for row in cursor:
                bus_stop_name = row[0]
                break

        # Step 6: Display results
        arcpy.SetProgressorLabel("Displaying results...")
        arcpy.SetProgressorPosition(6)
        time.sleep(2)

        # Output the results to the Geoprocessing Window using arcpy.AddMessage
        arcpy.AddMessage(f"\n" + "="*50)
        arcpy.AddMessage(f"NEAREST BUS STOP ANALYSIS RESULTS")
        arcpy.AddMessage(f"="*50)
        arcpy.AddMessage(f"Nearest stop: {bus_stop_name}")
        arcpy.AddMessage(f"Distance: {near_distance:.2f} meters")
        arcpy.AddMessage(f"Filter used: {name_field} = '{name_value}'")
        arcpy.AddMessage(f"="*50)

        # Clean up the temporary layer
        arcpy.Delete_management(filtered_layer)
        
        # Reset the progressor
        arcpy.ResetProgressor()

    except Exception as e:
        arcpy.AddError(f"An error occurred: {str(e)}")
        arcpy.ResetProgressor()

# Call the function
find_nearest_bus_stop()