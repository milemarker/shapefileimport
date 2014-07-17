__author__ = 'djvdorp'
import shapefile
import pyproj

file_name = "01-07-2014/Hectopunten/Hectopunten"

hectopunten_input_reader = shapefile.Reader(file_name)
hectopunten_input_shapeRecords = hectopunten_input_reader.shapeRecords()
#print len(hectopunten_shapes)

# Show hectopunten fields to verify input
hectopunten_fields = hectopunten_input_reader.fields
print hectopunten_fields



#wegvakken_shp = shapefile.Reader("01-07-2014/Wegvakken/Wegvakken")
#wegvakken_shapes = wegvakken_shp.shapes()
#print len(wegvakken_shapes)



input_projection = pyproj.Proj("+init=EPSG:28992") # Dit is Rijksdriehoekstelsel_New vanuit de .prj files, officieel EPSG:28992 Amersfoort / RD New
output_projection = pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth, officieel EPSG:4326

# Create a shapefile writer using the same shape type as our reader
hectopunten_output_writer = shapefile.Writer(hectopunten_input_reader.shapeType)
# Copy over the existing dbf fields
hectopunten_output_writer.fields = list(hectopunten_input_reader.fields)
# Copy over the existing dbf records
hectopunten_output_writer.records.extend(hectopunten_input_reader.records())

index = 0
while index < 100:
    for input_point in hectopunten_input_shapeRecords[index].shape.points:
        input_x = input_point[0]
        input_y = input_point[1]

        print "===================="
        print "--- INPUT (Rijksdriehoekstelsel_New): ---"
        print '({:-f}, {:-f})'.format(input_x, input_y)

        # Convert input_x, input_y from Rijksdriehoekstelsel_New to WGS84
        x, y = pyproj.transform(input_projection, output_projection, input_x, input_y)

        print "--- OUTPUT (WGS84): ---"
        print '({:-f}, {:-f})'.format(x, y)
        print "====================\n"

        # Add the translated point to the new shapefile (output) to save it
        hectopunten_output_writer.point(x, y)
    index += 1

# Save output file to new shapefile
hectopunten_output_writer.save()