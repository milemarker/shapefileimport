__author__ = 'djvdorp'
import shapefile
import pyproj


def shp_transform_to_different_projection(file_name, src_projection, dest_projection, nr_of_shapes_to_process=None):
    r = shapefile.Reader(file_name)
    shapes = r.shapeRecords()

    nr_of_shapes_in_file = len(shapes)
    if not nr_of_shapes_to_process:
        nr_of_shapes_to_process = nr_of_shapes_in_file

    print "{} of the {} shapes in file '{}' will be transformed".format(nr_of_shapes_to_process, nr_of_shapes_in_file, input_filename)

    # Show fields to verify input
    field_names = [str(i[0]) for i in r.fields]
    print field_names

    input_projection = pyproj.Proj(src_projection)
    output_projection = pyproj.Proj(dest_projection)

    print "shapeType read: {}".format(r.shapeType)

    # Create a shapefile writer using the same shape type as our reader
    w = shapefile.Writer(r.shapeType)

    # Because every shape must have a corresponding record it is critical that
    # the number of records equals the number of shapes to create a valid shapefile.
    w.autoBalance = 1

    # Copy over the existing dbf fields
    w.fields = list(r.fields)

    # Copy over the existing dbf records
    w.records.extend(r.records())

    index = 0
    while index <= (nr_of_shapes_to_process - 1):
        for input_point in shapes[index].shape.points:
            input_x = input_point[0]
            input_y = input_point[1]

            # Convert input_x, input_y from Rijksdriehoekstelsel_New to WGS84
            x, y = pyproj.transform(input_projection, output_projection, input_x, input_y)

            print 'Rijksdriehoekstelsel_New ({:-f}, {:-f}) becomes WGS84 ({:-f}, {:-f})'.format(input_x, input_y, x, y)

            # Add the translated point to the new shapefile (output) to save it
            w.point(x, y)
        index += 1

    # Save output file to new shapefile
    w.save("transformed")


# Real action here
input_filename = "01-07-2014/Hectopunten/Hectopunten"  # of "01-07-2014/Hectopunten/Hectopunten"
input_projection_string = "+init=EPSG:28992"  # Dit is Rijksdriehoekstelsel_New vanuit de .prj files, officieel EPSG:28992 Amersfoort / RD New
output_projection_string = "+init=EPSG:4326"  # LatLon with WGS84 datum used by GPS units and Google Earth, officieel EPSG:4326

shp_transform_to_different_projection(input_filename, input_projection_string, output_projection_string, 1)