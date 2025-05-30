from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFileDestination,
                       QgsProject,
                       QgsRectangle)
from qgis.utils import iface
import time
import os

# Import reportlab components
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
except ImportError:
    pass  # Will be handled in processAlgorithm


class CreateCityDistrictProfile(QgsProcessingAlgorithm):
    # Processing algorithm to create PDF profiles for city districts in Münster

    # Define parameter names
    DISTRICT_NAME = 'DISTRICT_NAME'
    FEATURE_TYPE = 'FEATURE_TYPE'
    OUTPUT_PDF = 'OUTPUT_PDF'

    def tr(self, string):
        # Returns a translatable string with the self.tr() function.
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        # Create a new instance of the algorithm
        return CreateCityDistrictProfile()

    def name(self):
        # Returns the algorithm name
        return 'create_city_district_profile'

    def displayName(self):
        # Returns the translated algorithm name
        return self.tr('Create City District Profile')

    def group(self):
        # Returns the name of the group this algorithm belongs to
        return self.tr('Münster Analysis Tools')

    def groupId(self):
        # Returns the unique ID of the group this algorithm belongs to
        return 'muenster_analysis'

    def shortHelpString(self):
        # Returns a localised short helper string for the algorithm
        return self.tr("Creates a comprehensive PDF profile for a selected city district in Münster. "
                      "The profile includes district information, statistics, and a map image.")

    def get_district_names(self):
        # Returns an alphabetically sorted list of city district names
        try:
            # Get the city districts layer by name
            project = QgsProject.instance()
            layer = None
            
            # Try to find the layer by name variations
            layer_names = ['Muenster_City_Districts', 'City_Districts', 'Districts']
            for name in layer_names:
                layers = project.mapLayersByName(name)
                if layers:
                    layer = layers[0]
                    break
            
            if not layer:
                return ['No districts layer found']
            
            # Extract district names from the 'Name' field
            district_names = []
            for feature in layer.getFeatures():
                try:
                    name = feature['Name']
                    if name:
                        district_names.append(str(name))
                except:
                    # Try alternative field names if 'Name' doesn't exist
                    for field_name in ['name', 'NAME', 'District', 'DISTRICT']:
                        try:
                            name = feature[field_name]
                            if name:
                                district_names.append(str(name))
                                break
                        except:
                            continue
            
            # Return alphabetically sorted list
            return sorted(district_names)
        
        except Exception as e:
            return [f'Error loading districts: {str(e)}']

    def initAlgorithm(self, config=None):
        # Define the inputs and outputs of the algorithm
        # Get district names for dropdown
        district_names = self.get_district_names()
        
        # District selection parameter
        self.addParameter(
            QgsProcessingParameterEnum(
                self.DISTRICT_NAME,
                self.tr('Select City District'),
                options=district_names,
                defaultValue=0
            )
        )
        
        # Feature type selection (Schools or Swimming Pools)
        self.addParameter(
            QgsProcessingParameterEnum(
                self.FEATURE_TYPE,
                self.tr('Include information about'),
                options=['Schools', 'Swimming Pools'],
                defaultValue=0
            )
        )
        
        # Output PDF file parameter
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_PDF,
                self.tr('Output PDF File'),
                fileFilter='PDF files (*.pdf)'
            )
        )

    def get_district_statistics(self, district_name, feature_type):
        # Calculate statistics for the selected district
        project = QgsProject.instance()
        statistics = {}
        
        try:
            # Get city districts layer
            districts_layer = None
            for name in ['Muenster_City_Districts', 'City_Districts', 'Districts']:
                layers = project.mapLayersByName(name)
                if layers:
                    districts_layer = layers[0]
                    break
            
            if not districts_layer:
                raise Exception("City districts layer not found")
            
            # Find the selected district feature
            district_feature = None
            for feature in districts_layer.getFeatures():
                try:
                    if str(feature['Name']) == district_name:
                        district_feature = feature
                        break
                except:
                    # Try alternative field names
                    for field_name in ['name', 'NAME', 'District', 'DISTRICT']:
                        try:
                            if str(feature[field_name]) == district_name:
                                district_feature = feature
                                break
                        except:
                            continue
                    if district_feature:
                        break
            
            if not district_feature:
                raise Exception(f"District '{district_name}' not found")
            
            # Get district geometry
            district_geom = district_feature.geometry()
            
            # Basic district information
            statistics['name'] = district_name
            try:
                statistics['parent_district'] = str(district_feature['P_District']) if district_feature['P_District'] else 'Unknown'
            except:
                statistics['parent_district'] = 'Unknown'
            
            # Calculate area (convert from square meters to square kilometers)
            area_sqm = district_geom.area()
            statistics['area_km2'] = round(area_sqm / 1000000, 2)
            
            # Count households
            households_count = 0
            house_numbers_layers = project.mapLayersByName('House_Numbers')
            if house_numbers_layers:
                house_layer = house_numbers_layers[0]
                for house_feature in house_layer.getFeatures():
                    if house_feature.geometry().intersects(district_geom):
                        households_count += 1
            statistics['households'] = households_count
            
            # Count parcels
            parcels_count = 0
            parcels_layers = project.mapLayersByName('Muenster_Parcels')
            if not parcels_layers:
                parcels_layers = project.mapLayersByName('Parcels')
            if parcels_layers:
                parcels_layer = parcels_layers[0]
                for parcel_feature in parcels_layer.getFeatures():
                    if parcel_feature.geometry().intersects(district_geom):
                        parcels_count += 1
            statistics['parcels'] = parcels_count
            
            # Count schools or swimming pools based on user selection
            if feature_type == 0:  # Schools
                feature_count = 0
                schools_layers = project.mapLayersByName('Schools')
                if schools_layers:
                    schools_layer = schools_layers[0]
                    for school_feature in schools_layer.getFeatures():
                        if school_feature.geometry().intersects(district_geom):
                            feature_count += 1
                statistics['feature_type'] = 'Schools'
                statistics['feature_count'] = feature_count
            else:  # Swimming Pools
                feature_count = 0
                pools_layers = project.mapLayersByName('public_swimmings_pools')
                if not pools_layers:
                    pools_layers = project.mapLayersByName('Swimming_Pools')
                if pools_layers:
                    pools_layer = pools_layers[0]
                    for pool_feature in pools_layer.getFeatures():
                        if pool_feature.geometry().intersects(district_geom):
                            feature_count += 1
                statistics['feature_type'] = 'Swimming Pools'
                statistics['feature_count'] = feature_count
            
            # Store geometry for map creation
            statistics['geometry'] = district_geom
            
        except Exception as e:
            statistics['error'] = str(e)
        
        return statistics

    def create_map_image(self, district_geometry, output_dir):
        # Create a map image of the selected district
        try:
            # Get map canvas
            canvas = iface.mapCanvas()
            
            # Zoom to district extent with some padding
            extent = district_geometry.boundingBox()
            # Add 10% padding
            width = extent.width() * 0.1
            height = extent.height() * 0.1
            padded_extent = QgsRectangle(
                extent.xMinimum() - width,
                extent.yMinimum() - height,
                extent.xMaximum() + width,
                extent.yMaximum() + height
            )
            
            canvas.setExtent(padded_extent)
            canvas.refresh()
            
            # Wait for refresh
            time.sleep(5)
            
            # Save map image
            map_image_path = os.path.join(output_dir, 'district_map.png')
            canvas.saveAsImage(map_image_path)
            
            return map_image_path
            
        except Exception as e:
            return None

    def create_pdf(self, statistics, output_file):
        # Create the PDF profile document
        try:
            # Create document
            doc = SimpleDocTemplate(output_file, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceAfter=12
            )
            
            # Title
            title = Paragraph(f"City District Profile: {statistics['name']}", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # District Information Section
            story.append(Paragraph("District Information", heading_style))
            
            district_data = [
                ['District Name:', statistics['name']],
                ['Parent District:', statistics['parent_district']],
                ['Area:', f"{statistics['area_km2']} km²"],
                ['Number of Households:', str(statistics['households'])],
                ['Number of Parcels:', str(statistics['parcels'])],
            ]
            
            # Add feature-specific information
            if statistics['feature_count'] > 0:
                district_data.append([f"Number of {statistics['feature_type']}:", str(statistics['feature_count'])])
            else:
                district_data.append([f"Number of {statistics['feature_type']}:", f"No {statistics['feature_type'].lower()} in this district"])
            
            # Create table
            district_table = Table(district_data, colWidths=[2.5*inch, 3*inch])
            district_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(district_table)
            story.append(Spacer(1, 30))
            
            # Map Section
            story.append(Paragraph("District Map", heading_style))
            
            # Try to add map image
            output_dir = os.path.dirname(output_file)
            map_image_path = self.create_map_image(statistics['geometry'], output_dir)
            
            if map_image_path and os.path.exists(map_image_path):
                try:
                    # Add map image to PDF
                    img = Image(map_image_path, width=6*inch, height=4*inch)
                    story.append(img)
                except:
                    story.append(Paragraph("Map image could not be created", styles['Normal']))
            else:
                story.append(Paragraph("Map image could not be created", styles['Normal']))
            
            story.append(Spacer(1, 20))
            
            # Footer
            footer_text = f"Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}"
            footer = Paragraph(footer_text, styles['Normal'])
            story.append(footer)
            
            # Build PDF
            doc.build(story)
            
            return True
            
        except Exception as e:
            raise QgsProcessingException(f"Error creating PDF: {str(e)}")

    def processAlgorithm(self, parameters, context, feedback):
        # Process the algorithm
        try:
            # Check if reportlab is installed
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib import colors
                from reportlab.lib.enums import TA_CENTER, TA_LEFT
            except ImportError:
                raise QgsProcessingException(
                    "ReportLab is not installed. Please install it using:\n"
                    "import pip\n"
                    "pip.main(['install', 'reportlab'])\n"
                    "in the QGIS Python console."
                )
            
            # Get parameters
            district_names = self.get_district_names()
            district_index = self.parameterAsInt(parameters, self.DISTRICT_NAME, context)
            district_name = district_names[district_index]
            
            feature_type = self.parameterAsInt(parameters, self.FEATURE_TYPE, context)
            output_file = self.parameterAsFileOutput(parameters, self.OUTPUT_PDF, context)
            
            feedback.pushInfo(f"Creating profile for district: {district_name}")
            
            # Get district statistics
            feedback.pushInfo("Calculating district statistics...")
            statistics = self.get_district_statistics(district_name, feature_type)
            
            if 'error' in statistics:
                raise QgsProcessingException(f"Error calculating statistics: {statistics['error']}")
            
            # Create PDF
            feedback.pushInfo("Creating PDF profile...")
            success = self.create_pdf(statistics, output_file)
            
            if success:
                feedback.pushInfo(f"PDF profile created successfully: {output_file}")
            
            return {self.OUTPUT_PDF: output_file}
            
        except Exception as e:
            raise QgsProcessingException(f"Error in processAlgorithm: {str(e)}")