__author__ = 'djvdorp'
import shapefile
import pyproj

import csv
from collections import OrderedDict
import logging

HECTOPUNTEN_OUTPUT_FIELDS = ['HECTOMTRNG', 'AFSTAND', 'WVK_ID', 'WVK_BEGDAT']
WEGVAKKEN_OUTPUT_FIELDS = ['WVK_ID', 'WVK_BEGDAT', 'JTE_ID_BEG', 'JTE_ID_END', 'WEGBEHSRT', 'WEGNUMMER', 'WEGDEELLTR', 'HECTO_LTTR', 'BAANSUBSRT', 'RPE_CODE', 'ADMRICHTNG', 'RIJRICHTNG', 'STT_NAAM', 'WPSNAAMNEN', 'GME_ID', 'GME_NAAM', 'HNRSTRLNKS', 'HNRSTRRHTS', 'E_HNR_LNKS', 'E_HNR_RHTS', 'L_HNR_LNKS', 'L_HNR_RHTS', 'BEGAFSTAND', 'ENDAFSTAND', 'BEGINKM', 'EINDKM', 'POS_TV_WOL']

logging.basicConfig(level=logging.INFO)

def shp_transform_to_different_projection(input_path, input_fields, src_projection, dest_projection, output_filename):
    logging.info("START processing shapefile '{}' to '{}'".format(input_path, output_filename))
    r = shapefile.Reader(input_path)
    input_shapes = r.shapeRecords()

    nr_of_shapes_in_file = len(input_shapes)
    logging.info("{} shapes in file '{}' will be transformed".format(nr_of_shapes_in_file, input_path))

    field_names = [str(i[0]) for i in r.fields]
    field_names.remove('DeletionFlag')  # of moet dit zijn: del field_names[0]
    logging.info("fieldNames in shapefile: {}".format(field_names))

    input_projection = pyproj.Proj(src_projection)
    output_projection = pyproj.Proj(dest_projection)

    logging.info("shapeType read: {}".format(r.shapeType))

    # @DaanDebie: welke structuur zou de csv writer van python willen?
    # Zie: https://docs.python.org/2/library/csv.html#writer-objects
    result = []

    for input_shape in input_shapes:
        input_x = input_shape.shape.points[0][0]
        input_y = input_shape.shape.points[0][1]
        input_record = input_shape.record

        # Convert input_x, input_y from Rijksdriehoekstelsel_New to WGS84
        x, y = pyproj.transform(input_projection, output_projection, input_x, input_y)

        logging.debug(field_names)
        logging.debug([str(i) for i in input_record])
        logging.debug('Rijksdriehoekstelsel_New ({:-f}, {:-f}) becomes WGS84 ({:-f}, {:-f})'.format(input_x, input_y, x, y))

        # @DaanDebie: in plaats van weer opslaan in een shapefile, wil ik het hier in de csv stoppen, maar dit lijkt me zo wat omslachtig?
        result_entry = OrderedDict()
        for input_field in input_fields:
            key = (field_names.index(input_field))

            input_entry = input_record[key]
            if isinstance(input_entry, list):
                input_entry = int_array_to_string(input_entry)

            result_entry[input_field] = input_entry

        result_entry['longitude'] = x
        result_entry['latitude'] = y

        result.append(result_entry)

    # @DaanDebie: hier geef ik, als 2e parameter, los nogmaals aan welke 'fieldnames' ik in de csv wil. Dat moet ook makkelijker kunnen toch?
    # Ze zijn immers ook in de entries van result (result.append() bekend?
    write_dict_data_to_csv_file(result, output_filename)
    logging.info("FINISHED processing - saved file '{}'".format(output_filename))


def int_array_to_string(input_array):
    return "-".join(str(i) for i in input_array)


# @DaanDebie: dit is een hacky mixup van online csv tutorials in een poging om csv writing werkend te krijgen, be warned.
def write_dict_data_to_csv_file(dict_data, csv_file_path):
    csv_file = open(csv_file_path, 'wb')
    writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)

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

shp_transform_to_different_projection(input_hectopunten, HECTOPUNTEN_OUTPUT_FIELDS, input_projection_string, output_projection_string, "output/Hectopunten.csv")
#shp_transform_to_different_projection(input_wegvakken, WEGVAKKEN_OUTPUT_FIELDS, input_projection_string, output_projection_string, "output/Wegvakken.csv")
