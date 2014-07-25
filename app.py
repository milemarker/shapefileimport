__author__ = 'djvdorp'
import shapefile
import pyproj

import csv
from collections import OrderedDict
import logging
from progressbar import Percentage, ProgressBar, Bar, RotatingMarker, ETA

HECTOPUNTEN_OUTPUT_FIELDS = ['HECTOMTRNG', 'AFSTAND', 'WVK_ID', 'WVK_BEGDAT']
WEGVAKKEN_OUTPUT_FIELDS = ['WVK_ID', 'WVK_BEGDAT', 'JTE_ID_BEG', 'JTE_ID_END', 'WEGBEHSRT', 'WEGNUMMER', 'WEGDEELLTR', 'HECTO_LTTR', 'BAANSUBSRT', 'RPE_CODE', 'ADMRICHTNG', 'RIJRICHTNG', 'STT_NAAM', 'WPSNAAMNEN', 'GME_ID', 'GME_NAAM', 'HNRSTRLNKS', 'HNRSTRRHTS', 'E_HNR_LNKS', 'E_HNR_RHTS', 'L_HNR_LNKS', 'L_HNR_RHTS', 'BEGAFSTAND', 'ENDAFSTAND', 'BEGINKM', 'EINDKM', 'POS_TV_WOL']

logging.basicConfig(level=logging.INFO)

widgets = ['Processing: ', Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA()]

def shp_transform_to_different_projection(input_path, input_fields, src_projection, dest_projection, output_filename):
    logging.info("START processing shapefile '{}' to '{}'".format(input_path, output_filename))

    csv_file = open(output_filename, 'wb')
    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

    r = shapefile.Reader(input_path)
    input_shapes = r.shapeRecords()

    nr_of_shapes_in_file = len(input_shapes)
    logging.info("{} shapes in file '{}' will be transformed".format(nr_of_shapes_in_file, input_path))

    field_names = [str(i[0]) for i in r.fields]
    field_names.remove('DeletionFlag')  # of moet dit zijn: del field_names[0]
    logging.info("fieldNames in shapefile: {}".format(field_names))

    input_projection = pyproj.Proj(src_projection)
    output_projection = pyproj.Proj(dest_projection)

    # shapefile.NULL = 0
    # shapefile.POINT = 1
    # shapefile.POLYLINE = 3
    # shapefile.POLYGON = 5
    # shapefile.MULTIPOINT = 8
    # shapefile.POINTZ = 11
    # shapefile.POLYLINEZ = 13
    # shapefile.POLYGONZ = 15
    # shapefile.MULTIPOINTZ = 18
    # shapefile.POINTM = 21
    # shapefile.POLYLINEM = 23
    # shapefile.POLYGONM = 25
    # shapefile.MULTIPOINTM = 28
    # shapefile.MULTIPATCH = 31
    logging.info("shapeType read: {}".format(r.shapeType))

    counter = 0
    pbar = ProgressBar(widgets=widgets, maxval=nr_of_shapes_in_file).start()

    for input_shape in input_shapes:
        nr_of_points_in_shape = len(input_shape.shape.points)

        result_entry = OrderedDict()
        for input_field in input_fields:
            key = (field_names.index(input_field))

            input_record = input_shape.record
            input_entry = input_record[key]
            if isinstance(input_entry, list):
                input_entry = int_array_to_string(input_entry)

            result_entry[input_field] = input_entry

        if nr_of_points_in_shape == 1:
            input_x = input_shape.shape.points[0][0]
            input_y = input_shape.shape.points[0][1]

            # Convert input_x, input_y from Rijksdriehoekstelsel_New to WGS84
            x, y = pyproj.transform(input_projection, output_projection, input_x, input_y)

            logging.debug(field_names)
            logging.debug([str(i) for i in input_record])
            logging.debug('Rijksdriehoekstelsel_New ({:-f}, {:-f}) becomes WGS84 ({:-f}, {:-f})'.format(input_x, input_y, x, y))

            result_entry['longitude'] = x
            result_entry['latitude'] = y
        else:
            logging.debug("number of points for this shape: {}".format(nr_of_points_in_shape))

        headers = result_entry.keys()
        if counter == 0:
            writer.writerow(headers)

        line = []
        for field in headers:
            line.append(result_entry[field])
        writer.writerow(line)

        counter += 1
        pbar.update(counter)

    csv_file.close()
    pbar.finish()
    logging.info("FINISHED processing - saved file '{}'".format(output_filename))


def int_array_to_string(input_array):
    return "-".join(str(i) for i in input_array)


# Real action here
# Bestanden kunnen worden gevonden op: http://www.jigsaw.nl/nwb/downloads/NWB_01-07-2014.zip
input_hectopunten = "01-07-2014/Hectopunten/Hectopunten"
input_wegvakken = "01-07-2014/Wegvakken/Wegvakken"
input_projection_string = "+init=EPSG:28992"  # Dit is Rijksdriehoekstelsel_New vanuit de .prj files, officieel EPSG:28992 Amersfoort / RD New
output_projection_string = "+init=EPSG:4326"  # LatLon with WGS84 datum used by GPS units and Google Earth, officieel EPSG:4326

shp_transform_to_different_projection(input_hectopunten, HECTOPUNTEN_OUTPUT_FIELDS, input_projection_string, output_projection_string, "output/Hectopunten.csv")
shp_transform_to_different_projection(input_wegvakken, WEGVAKKEN_OUTPUT_FIELDS, input_projection_string, output_projection_string, "output/Wegvakken.csv")
