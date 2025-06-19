"""
Exercise 9.1: Using arcpy.da cursors
"""

import arcpy
import os


def process_geodatabase(gdb_path):

    
   ## Args:gdb_path (str): Path to the geodatabase
    
    # Set workspace to the geodatabase
    arcpy.env.workspace = gdb_path
    
    # Get list of all feature classes in the geodatabase
    feature_classes = arcpy.ListFeatureClasses()
    
    if not feature_classes:
        print("No feature classes found in the geodatabase.")
        return
    
    # Initialize variables for the new feature class
    active_assets_fc = "active_assets"
    active_assets_path = os.path.join(gdb_path, active_assets_fc)
    
    # Variables to track processing
    point_feature_classes = []
    total_active_features = 0
    first_point_fc = None
    
    print(f"Processing geodatabase: {gdb_path}")
    print(f"Found {len(feature_classes)} feature classes")
    
    # First pass: identify Point-Geometry feature classes and check for 'status' field
    for fc in feature_classes:
        try:
            # Get feature class description
            desc = arcpy.Describe(fc)
            
            # Check if it's a Point geometry type
            if desc.shapeType == "Point":
                print(f"\nFound Point feature class: {fc}")
                
                # Check if 'status' field exists
                fields = [field.name.lower() for field in arcpy.ListFields(fc)]
                if 'status' in fields:
                    point_feature_classes.append(fc)
                    if first_point_fc is None:
                        first_point_fc = fc
                    print(f"  - Has 'status' field: Yes")
                else:
                    print(f"  - Has 'status' field: No (skipping)")
                    
        except Exception as e:
            print(f"Error processing feature class {fc}: {str(e)}")
    
    if not point_feature_classes:
        print("\nNo Point feature classes with 'status' field found.")
        return
    
    # Create the active_assets feature class based on the first point feature class
    try:
        if arcpy.Exists(active_assets_path):
            print(f"\nDeleting existing {active_assets_fc} feature class...")
            arcpy.Delete_management(active_assets_path)
        
        print(f"Creating new feature class: {active_assets_fc}")
        
        # Create new feature class with same spatial reference as first point FC
        sr = arcpy.Describe(first_point_fc).spatialReference
        arcpy.CreateFeatureclass_management(
            gdb_path, 
            active_assets_fc, 
            "POINT", 
            spatial_reference=sr
        )
        
        # Add necessary fields to the new feature class
        # Get fields from the first point feature class as template
        template_fields = arcpy.ListFields(first_point_fc)
        
        for field in template_fields:
            # Skip system fields
            if field.name.lower() not in ['objectid', 'shape', 'shape_length', 'shape_area', 'globalid']:
                try:
                    arcpy.AddField_management(
                        active_assets_path,
                        field.name,
                        field.type,
                        field.precision,
                        field.scale,
                        field.length,
                        field.aliasName
                    )
                except Exception as e:
                    print(f"  Warning: Could not add field {field.name}: {str(e)}")
        
        # Add a source field to track which feature class the feature came from
        arcpy.AddField_management(active_assets_path, "SOURCE_FC", "TEXT", field_length=50)
        
    except Exception as e:
        print(f"Error creating active_assets feature class: {str(e)}")
        return
    
    # Second pass: Process each Point feature class and copy active features
    for fc in point_feature_classes:
        try:
            print(f"\nProcessing feature class: {fc}")
            
            # Get all field names for the current feature class (excluding system fields)
            fc_fields = arcpy.ListFields(fc)
            data_fields = []
            
            for field in fc_fields:
                if field.name.lower() not in ['objectid', 'globalid']:
                    data_fields.append(field.name)
            
            # Add SHAPE@ token for geometry
            search_fields = data_fields + ['SHAPE@']
            
            # Create search cursor with filter for 'active' status
            where_clause = "status = 'active'"
            active_count = 0
            
            with arcpy.da.SearchCursor(fc, search_fields, where_clause) as search_cursor:
                # Get field names for insert cursor (excluding SHAPE@ for now)
                insert_fields = []
                for field_name in data_fields:
                    # Check if field exists in active_assets
                    try:
                        arcpy.ListFields(active_assets_path, field_name)[0]
                        insert_fields.append(field_name)
                    except IndexError:
                        # Field doesn't exist in target, we'll skip it
                        pass
                
                # Add SOURCE_FC and SHAPE@ fields
                insert_fields.extend(['SOURCE_FC', 'SHAPE@'])
                
                # Create insert cursor for active_assets
                with arcpy.da.InsertCursor(active_assets_path, insert_fields) as insert_cursor:
                    
                    for row in search_cursor:
                        try:
                            # Prepare the new row for insertion
                            new_row = []
                            
                            # Map data from search cursor to insert cursor
                            for field_name in insert_fields:
                                if field_name == 'SOURCE_FC':
                                    new_row.append(fc)
                                elif field_name == 'SHAPE@':
                                    # Get geometry from the last item in search row
                                    new_row.append(row[-1])
                                else:
                                    # Find the field index in the search cursor
                                    try:
                                        field_index = data_fields.index(field_name)
                                        new_row.append(row[field_index])
                                    except ValueError:
                                        # Field not found, append None
                                        new_row.append(None)
                            
                            # Insert the row
                            insert_cursor.insertRow(new_row)
                            active_count += 1
                            
                        except Exception as e:
                            print(f"    Error inserting row: {str(e)}")
            
            print(f"  - Active features found and copied: {active_count}")
            total_active_features += active_count
            
        except Exception as e:
            print(f"Error processing feature class {fc}: {str(e)}")
    
    print(f"\n=== Processing Complete ===")
    print(f"Total Point feature classes processed: {len(point_feature_classes)}")
    print(f"Total active features copied: {total_active_features}")
    print(f"New feature class created: {active_assets_fc}")
    
    if total_active_features > 0:
        print(f"Successfully created {active_assets_fc} with {total_active_features} features.")
    else:
        print("No active features were found to copy.")


def main():
    """Main function to run the script"""
    
    # Path to the geodatabase
    gdb_path = r"D:\study\UniMuenster\Sose2025\PythonInQgisandArcgis\week9\exercise_arcpy_1.gdb"
    
    # Check if geodatabase exists
    if not arcpy.Exists(gdb_path):
        print(f"Error: Geodatabase not found at {gdb_path}")
        print("Please check the path and ensure the geodatabase exists.")
        return
    
    try:
        # Process the geodatabase
        process_geodatabase(gdb_path)
        
    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
