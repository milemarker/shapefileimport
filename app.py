__author__ = 'djvdorp'
import shapefile
import pyproj

import csv
from collections import OrderedDict

HECTOPUNTEN_FIELDS = OrderedDict([('HECTOMTRNG', 0), ('AFSTAND', 1), ('WVK_ID', 2), ('WVK_BEGDAT', 3)])


def shp_transform_to_different_projection(input_path, input_fields, src_projection, dest_projection, output_filename):
    r = shapefile.Reader(input_path)
    input_shapes = r.shapeRecords()

    nr_of_shapes_in_file = len(input_shapes)
    print "{} shapes in file '{}' will be transformed".format(nr_of_shapes_in_file, input_path)

    # Show fields to verify input
    field_names = [str(i[0]) for i in r.fields]
    print field_names

    input_projection = pyproj.Proj(src_projection)
    output_projection = pyproj.Proj(dest_projection)

    print "shapeType read: {}".format(r.shapeType)

    # @DaanDebie: welke structuur zou de csv writer van python willen?
    # Zie: https://docs.python.org/2/library/csv.html#writer-objects
    result = []

    for input_shape in input_shapes:
        input_x = input_shape.shape.points[0][0]
        input_y = input_shape.shape.points[0][1]
        input_record = input_shape.record

        # Convert input_x, input_y from Rijksdriehoekstelsel_New to WGS84
        x, y = pyproj.transform(input_projection, output_projection, input_x, input_y)

        #print 'Rijksdriehoekstelsel_New ({:-f}, {:-f}) becomes WGS84 ({:-f}, {:-f})'.format(input_x, input_y, x, y)
        #print field_names
        #print [str(i) for i in input_record]

        # @DaanDebie: in plaats van weer opslaan in een shapefile, wil ik het hier in de csv stoppen, maar dit lijkt me zo wat omslachtig?
        result_entry = OrderedDict()
        for key, value in input_fields.items():
            input_entry = input_record[value]
            if isinstance(input_entry, list):
                input_entry = int_array_to_string(input_entry)
            result_entry[key] = input_entry

            result_entry['longitude'] = x
            result_entry['latitude'] = y
        
        result.append(result_entry)

    # @DaanDebie: hier geef ik, als 2e parameter, los nogmaals aan welke 'fieldnames' ik in de csv wil. Dat moet ook makkelijker kunnen toch?
    # Ze zijn immers ook in de entries van result (result.append() bekend?
    write_dict_data_to_csv_file(result, output_filename)


def int_array_to_string(input_array):
    return "-".join(str(i) for i in input_array)


# @DaanDebie: dit is een hacky mixup van online csv tutorials in een poging om csv writing werkend te krijgen, be warned.
def write_dict_data_to_csv_file(dict_data, csv_file_path):
    csv_file = open(csv_file_path, 'wb')
    writer = csv.writer(csv_file)

    headers = dict_data[0].keys()
    writer.writerow(headers)

    for dat in dict_data:
        line = []
        for field in headers:
            line.append(dat[field])
        writer.writerow(line)

    csv_file.close()


# Real action here
# Bestanden kunnen worden gevonden op: http://www.jigsaw.nl/nwb/downloads/NWB_01-07-2014.zip
input_hectopunten = "01-07-2014/Hectopunten/Hectopunten"
input_wegvakken = "01-07-2014/Wegvakken/Wegvakken"
input_projection_string = "+init=EPSG:28992"  # Dit is Rijksdriehoekstelsel_New vanuit de .prj files, officieel EPSG:28992 Amersfoort / RD New
output_projection_string = "+init=EPSG:4326"  # LatLon with WGS84 datum used by GPS units and Google Earth, officieel EPSG:4326

shp_transform_to_different_projection(input_hectopunten, HECTOPUNTEN_FIELDS, input_projection_string, output_projection_string, "output/Hectopunten.csv")

