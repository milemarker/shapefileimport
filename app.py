__author__ = 'djvdorp'
import shapefile
import pyproj

import csv


def shp_transform_to_different_projection(file_name, src_projection, dest_projection):
    r = shapefile.Reader(file_name)
    input_shapes = r.shapeRecords()

    nr_of_shapes_in_file = len(input_shapes)
    print "{} shapes in file '{}' will be transformed".format(nr_of_shapes_in_file, input_filename)

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

    result = []

    for input_shape in input_shapes:
        input_x = input_shape.shape.points[0][0]
        input_y = input_shape.shape.points[0][1]

        # Convert input_x, input_y from Rijksdriehoekstelsel_New to WGS84
        x, y = pyproj.transform(input_projection, output_projection, input_x, input_y)

        print 'Rijksdriehoekstelsel_New ({:-f}, {:-f}) becomes WGS84 ({:-f}, {:-f})'.format(input_x, input_y, x, y)

        # Add the translated point to the new shapefile (output) to save it
        #w.point(x, y)

        result.append({'x': x, 'y': y})

    # Save output file to new shapefile
    #w.save("transformed")
    csv_dict_writer("transformed.csv", ['x', 'y'], result)


def csv_dict_writer(path, fieldnames, data):
    test_file = open(path,'wb')
    csvwriter = csv.DictWriter(test_file, delimiter=',', fieldnames=fieldnames)
    csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
    for row in data:
         csvwriter.writerow(row)
    test_file.close()


# Real action here
input_filename = "01-07-2014/Hectopunten/Hectopunten"  # of "01-07-2014/Hectopunten/Hectopunten"
input_projection_string = "+init=EPSG:28992"  # Dit is Rijksdriehoekstelsel_New vanuit de .prj files, officieel EPSG:28992 Amersfoort / RD New
output_projection_string = "+init=EPSG:4326"  # LatLon with WGS84 datum used by GPS units and Google Earth, officieel EPSG:4326

shp_transform_to_different_projection(input_filename, input_projection_string, output_projection_string)