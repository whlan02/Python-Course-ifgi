import arcpy

class ToolValidator(object):
    """
    Validation class for the Find Nearest Bus Stop tool.
    Provides dynamic dropdown population for field names and field values.
    """

    def __init__(self):
        """Initialize the tool validator."""
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        """
        Refine the properties of the tool's parameters.
        """
        # Disable name field and value parameters initially
        if len(self.params) >= 3:
            self.params[2].enabled = False
            if len(self.params) >= 4:
                self.params[3].enabled = False

    def updateParameters(self):
        """
        Modify the values and properties of parameters before internal validation is performed.
        """
        if len(self.params) < 4:
            return

        # Don't process if the name value parameter itself was just altered
        # This prevents clearing the value when user just selected it
        if self.params[3].altered:
            return

        # Handle feature class parameter changes
        if self.params[1].altered and self.params[1].value:
            try:
                feature_class = self.params[1].valueAsText
                
                if arcpy.Exists(feature_class):
                    # Enable name field parameter
                    self.params[2].enabled = True
                    
                    # Get fields from feature class (include all field types)
                    field_names = []
                    fields = arcpy.ListFields(feature_class)
                    for field in fields:
                        # Include all fields except geometry and system fields
                        if field.type not in ['Geometry', 'OID'] and not field.name.lower().startswith('shape'):
                            field_names.append(field.name)
                    
                    # Set up the filter for name field parameter
                    if field_names:
                        self.params[2].filter.type = 'ValueList'
                        self.params[2].filter.list = sorted(field_names)
                        # Only clear name field if it's not in the new list
                        if self.params[2].value and self.params[2].valueAsText not in field_names:
                            self.params[2].value = None
                            # Only reset name value when name field is actually cleared
                            self.params[3].value = None
                            self.params[3].enabled = False
                            self.params[3].filter.list = []
                    else:
                        self.params[2].enabled = False
                        self.params[2].value = None
                        self.params[3].enabled = False
                        self.params[3].value = None
                else:
                    self.params[2].enabled = False
                    self.params[2].value = None
                    self.params[3].enabled = False
                    self.params[3].value = None
            except Exception as e:
                arcpy.AddError(f"Error in feature class parameter: {str(e)}")
                self.params[2].enabled = False
                self.params[3].enabled = False

        # Handle name field parameter changes
        if self.params[2].altered and self.params[2].value and self.params[1].value:
            try:
                feature_class = self.params[1].valueAsText
                field_name = self.params[2].valueAsText
                
                # Add debug message
                arcpy.AddMessage(f"Processing field selection: '{field_name}' from '{feature_class}'")
                
                if arcpy.Exists(feature_class) and field_name:
                    # Store current value to preserve it if possible
                    current_value = self.params[3].valueAsText if self.params[3].value else None
                    
                    # Get unique values from selected field
                    unique_values = set()
                    try:
                        with arcpy.da.SearchCursor(feature_class, [field_name]) as cursor:
                            for row in cursor:
                                if row[0] is not None:
                                    # Convert to string and strip whitespace
                                    value = str(row[0]).strip()
                                    if value:  # Only add non-empty values
                                        unique_values.add(value)
                    except Exception as cursor_error:
                        arcpy.AddError(f"Error reading field values from '{field_name}': {str(cursor_error)}")
                        self.params[3].enabled = False
                        return
                    
                    # Set up the filter for name value parameter
                    if unique_values:
                        value_list = sorted(list(unique_values))
                        self.params[3].enabled = True
                        # Set the filter to ValueList and populate it
                        self.params[3].filter.type = 'ValueList'
                        self.params[3].filter.list = value_list
                        # Only clear existing value if it's not in the new list
                        if current_value and current_value not in value_list:
                            self.params[3].value = None
                        arcpy.AddMessage(f"Found {len(value_list)} unique values in field '{field_name}': {value_list[:5]}...")
                    else:
                        self.params[3].enabled = False
                        self.params[3].value = None
                        self.params[3].filter.list = []
                        arcpy.AddWarning(f"No values found in field '{field_name}'")
                else:
                    self.params[3].enabled = False
                    self.params[3].value = None
            except Exception as e:
                arcpy.AddError(f"Error processing name field parameter: {str(e)}")
                self.params[3].enabled = False
                self.params[3].value = None

        # If name field is cleared, disable name value
        if self.params[2].altered and not self.params[2].value:
            self.params[3].enabled = False
            self.params[3].value = None
            self.params[3].filter.list = []

    def updateMessages(self):
        """
        Modify the messages created by internal validation for each tool parameter.
        """
        if len(self.params) < 4:
            return

        # Clear any previous messages
        for param in self.params:
            param.clearMessage()

        # Validate feature class
        if self.params[1].value:
            try:
                feature_class = self.params[1].valueAsText
                if not arcpy.Exists(feature_class):
                    self.params[1].setErrorMessage(f"Feature class '{feature_class}' does not exist")
                else:
                    desc = arcpy.Describe(feature_class)
                    if desc.dataType not in ['FeatureClass', 'FeatureLayer']:
                        self.params[1].setErrorMessage(f"'{feature_class}' is not a valid feature class or layer")
            except Exception as e:
                self.params[1].setErrorMessage(f"Error validating feature class: {str(e)}")

        # Validate field selection
        if self.params[1].value and self.params[2].value:
            try:
                feature_class = self.params[1].valueAsText
                field_name = self.params[2].valueAsText
                
                if arcpy.Exists(feature_class):
                    field_names = [field.name for field in arcpy.ListFields(feature_class)]
                    if field_name not in field_names:
                        self.params[2].setErrorMessage(f"Field '{field_name}' does not exist in feature class")
            except Exception as e:
                self.params[2].setErrorMessage(f"Error validating field: {str(e)}")

        # Validate value selection
        if all(param.value for param in self.params[1:4]):
            try:
                feature_class = self.params[1].valueAsText
                field_name = self.params[2].valueAsText
                field_value = self.params[3].valueAsText
                
                if arcpy.Exists(feature_class):
                    # Check if the value exists in the field
                    field_delimiter = arcpy.AddFieldDelimiters(feature_class, field_name)
                    where_clause = f"{field_delimiter} = '{field_value}'"
                    
                    count = 0
                    with arcpy.da.SearchCursor(feature_class, [field_name], where_clause) as cursor:
                        count = sum(1 for _ in cursor)
                    
                    if count == 0:
                        self.params[3].setWarningMessage(
                            f"No features found with {field_name} = '{field_value}'"
                        )
            except Exception as e:
                self.params[3].setErrorMessage(f"Error validating value: {str(e)}") 