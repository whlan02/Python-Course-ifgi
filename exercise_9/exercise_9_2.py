"""
Exercise 9.2: Cell Phone Reception Coverage Analysis
Task: Use the 'active_assets' feature class to analyze cell phone reception coverage
by creating buffers around assets based on their type.

Buffer distances:
- mast: 300 meters
- mobile_antenna: 50 meters  
- building_antenna: 100 meters

Implementation: Helper field approach
"""

import arcpy
import os


def setup_environment(gdb_path):
    """Set up the ArcPy environment"""
    arcpy.env.workspace = gdb_path
    arcpy.env.overwriteOutput = True
    print(f"Workspace set to: {gdb_path}")


def check_active_assets_exists(gdb_path):
    """Check if the active_assets feature class exists"""
    active_assets_path = os.path.join(gdb_path, "active_assets")
    
    if not arcpy.Exists(active_assets_path):
        print("Error: 'active_assets' feature class not found!")
        print("Please run exercise_9_1.py first to create the active_assets feature class.")
        return False
    
    # Check if it has the required 'type' field
    fields = [field.name.lower() for field in arcpy.ListFields(active_assets_path)]
    if 'type' not in fields:
        print("Error: 'active_assets' feature class does not have a 'type' field!")
        return False
    
    return True


def create_coverage_with_helper_field(gdb_path):
    """
    Create coverage using helper field approach
    """
    print("\n" + "="*60)
    print("CREATING COVERAGE WITH HELPER FIELD APPROACH")
    print("="*60)
    
    active_assets_path = os.path.join(gdb_path, "active_assets")
    coverage_path = os.path.join(gdb_path, "coverage")
    
    try:
        # Step 1: Add a helper field for buffer distance
        print("Step 1: Adding buffer_distance field...")
        
        # Check if field already exists
        existing_fields = [field.name.lower() for field in arcpy.ListFields(active_assets_path)]
        if 'buffer_distance' not in existing_fields:
            arcpy.AddField_management(
                active_assets_path,
                "buffer_distance",
                "DOUBLE",
                field_alias="Buffer Distance (meters)"
            )
            print("  - Added buffer_distance field")
        else:
            print("  - buffer_distance field already exists")
        
        # Step 2: Calculate buffer distances based on type
        print("Step 2: Calculating buffer distances based on type...")
        
        # Define the calculation expression using Python code block
        code_block = """
def get_buffer_distance(asset_type):
    if asset_type == 'mast':
        return 300
    elif asset_type == 'mobile_antenna':
        return 50
    elif asset_type == 'building_antenna':
        return 100
    else:
        return 0  # Default for unknown types
"""
        
        expression = "get_buffer_distance(!type!)"
        
        arcpy.CalculateField_management(
            active_assets_path,
            "buffer_distance",
            expression,
            "PYTHON3",
            code_block
        )
        print("  - Calculated buffer distances")
        
        # Step 3: Create buffers using the helper field
        print("Step 3: Creating buffers using buffer_distance field...")
        
        # Delete existing coverage if it exists
        if arcpy.Exists(coverage_path):
            arcpy.Delete_management(coverage_path)
        
        arcpy.Buffer_analysis(
            active_assets_path,
            coverage_path,
            "buffer_distance",
            "FULL",
            "ROUND",
            "ALL"
        )
        
        # Get count of output features
        result = arcpy.GetCount_management(coverage_path)
        count = int(result[0])
        
        print(f"  - Created 'coverage' feature class with {count} buffer features")
        print("✓ Coverage creation completed successfully!")
        
        return coverage_path
        
    except Exception as e:
        print(f"Error creating coverage: {str(e)}")
        return None


def analyze_coverage_results(gdb_path):
    """
    Analyze and report on the coverage results
    """
    print("\n" + "="*60)
    print("COVERAGE ANALYSIS RESULTS")
    print("="*60)
    
    active_assets_path = os.path.join(gdb_path, "active_assets")
    coverage_path = os.path.join(gdb_path, "coverage")
    
    try:
        # Count original assets by type
        print("Original Assets Summary:")
        asset_types = ['mast', 'mobile_antenna', 'building_antenna']
        
        for asset_type in asset_types:
            where_clause = f"type = '{asset_type}'"
            result = arcpy.GetCount_management(
                arcpy.MakeFeatureLayer_management(active_assets_path, "temp_layer", where_clause)
            )
            count = int(result[0])
            print(f"  - {asset_type}: {count} assets")
        
        # Total coverage area
        if arcpy.Exists(coverage_path):
            print(f"\nCoverage Results:")
            result = arcpy.GetCount_management(coverage_path)
            buffer_count = int(result[0])
            print(f"  - Total buffer polygons created: {buffer_count}")
            
            # Calculate total coverage area
            arcpy.AddField_management(coverage_path, "area_sqm", "DOUBLE")
            arcpy.CalculateGeometryAttributes_management(coverage_path, [["area_sqm", "AREA"]], area_unit="SQUARE_METERS")
            
            # Get statistics
            stats_table = "in_memory/stats"
            arcpy.Statistics_analysis(coverage_path, stats_table, [["area_sqm", "SUM"]])
            
            with arcpy.da.SearchCursor(stats_table, ["SUM_area_sqm"]) as cursor:
                for row in cursor:
                    total_area_sqm = row[0]
                    total_area_km2 = total_area_sqm / 1000000
                    print(f"  - Total coverage area: {total_area_sqm:,.0f} square meters ({total_area_km2:.2f} km²)")
            
            arcpy.Delete_management(stats_table)
        
    except Exception as e:
        print(f"Error in coverage analysis: {str(e)}")


def main():
    """Main function to run the coverage analysis"""
    
    # Path to the geodatabase
    gdb_path = r"D:\study\UniMuenster\Sose2025\PythonInQgisandArcgis\week9\exercise_arcpy_1.gdb"
    
    print("="*60)
    print("CELL PHONE RECEPTION COVERAGE ANALYSIS")
    print("="*60)
    
    # Check if geodatabase exists
    if not arcpy.Exists(gdb_path):
        print(f"Error: Geodatabase not found at {gdb_path}")
        print("Please check the path and ensure the geodatabase exists.")
        return
    
    # Set up environment
    setup_environment(gdb_path)
    
    # Check if active_assets exists
    if not check_active_assets_exists(gdb_path):
        return
    
    try:
        # Create coverage using helper field approach
        coverage_result = create_coverage_with_helper_field(gdb_path)
        
        # Analyze results
        if coverage_result:
            analyze_coverage_results(gdb_path)
        
        print("\n" + "="*60)
        print("PROCESSING COMPLETE")
        print("="*60)
        print("Coverage analysis completed successfully!")
        print(f"Result available in: coverage")
        
    except Exception as e:
        print(f"Script execution failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
