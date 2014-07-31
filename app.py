__author__ = 'djvdorp'
from collections import OrderedDict
from progressbar import *

import shapefile
import pyproj
import csv
import logging
import pandas

HECTOPUNTEN_OUTPUT_FIELDS = ['HECTOMTRNG', 'AFSTAND', 'WVK_ID', 'WVK_BEGDAT']
WEGVAKKEN_OUTPUT_FIELDS = ['WVK_ID', 'WVK_BEGDAT', 'JTE_ID_BEG', 'JTE_ID_END', 'WEGBEHSRT', 'WEGNUMMER', 'WEGDEELLTR', 'HECTO_LTTR', 'BAANSUBSRT', 'RPE_CODE', 'ADMRICHTNG', 'RIJRICHTNG', 'STT_NAAM', 'WPSNAAMNEN', 'GME_ID', 'GME_NAAM', 'HNRSTRLNKS', 'HNRSTRRHTS', 'E_HNR_LNKS', 'E_HNR_RHTS', 'L_HNR_LNKS', 'L_HNR_RHTS', 'BEGAFSTAND', 'ENDAFSTAND', 'BEGINKM', 'EINDKM', 'POS_TV_WOL']

MERGED_OUTPUT_FIELDS = ['ID', 'WEGNUMMER', 'HECTOMTRNG', 'LONGITUDE', 'LATITUDE', 'STT_NAAM', 'GME_NAAM', 'WEGBEHSRT', 'RPE_CODE', 'POS_TV_WOL', 'WEGDEELLTR', 'HECTO_LTTR', 'BAANSUBSRT']
MERGED_RENAME_FIELDS_MAPPING = {'ID': 'HP_ID', 'WEGNUMMER': 'WEGNR','HECTOMTRNG': 'HECTONR'}

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

    # 3 = shapefile.POLYLINE = wegvakken
    # 8 = shapefile.MULTIPOINT = hectopunten
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

            # Lists (voor datum) platslaan tot een string
            if isinstance(input_entry, list):
                input_entry = int_array_to_string(input_entry)

            # HECTOMTRNG moet gedeeld worden door 10
            if input_field == 'HECTOMTRNG':
                input_entry = (input_record[key] / 10.)

            result_entry[input_field] = input_entry

        if nr_of_points_in_shape == 1:
            input_x = input_shape.shape.points[0][0]
            input_y = input_shape.shape.points[0][1]

            # Convert input_x, input_y from Rijksdriehoekstelsel_New to WGS84
            x, y = pyproj.transform(input_projection, output_projection, input_x, input_y)

            logging.debug(field_names)
            logging.debug([str(i) for i in input_record])
            logging.debug('Rijksdriehoekstelsel_New ({:-f}, {:-f}) becomes WGS84 ({:-f}, {:-f})'.format(input_x, input_y, x, y))

            result_entry['LONGITUDE'] = x
            result_entry['LATITUDE'] = y
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


def merge_shapefile_csvs(input_hectopunten, input_wegvakken, merge_on_field, fields_to_keep, fields_rename_mapping, output_filename):
    hectopunten_df = pandas.read_csv(input_hectopunten)
    wegvakken_df = pandas.read_csv(input_wegvakken)

    # Join de 2 input files samen, left=hectopunten en right=wegvakken
    merged_df = pandas.merge(hectopunten_df, wegvakken_df, on=merge_on_field)
    # Voeg een ID field toe per regel
    merged_df['ID'] = merged_df.index

    # Bewaar alleen de meegegeven velden om te bewaren
    result_df = merged_df[fields_to_keep]

    # Hernoem columns zodat deze af kunnen wijken van de input columns
    result_df = result_df.rename(columns=fields_rename_mapping)

    # Exporteer dit naar een merged csv
    result_df.to_csv(output_filename, mode='wb', index=False, header=True, quoting=csv.QUOTE_NONNUMERIC)


# Real action here
input_projection_string = "+init=EPSG:28992"  # Dit is Rijksdriehoekstelsel_New vanuit de .prj files, officieel EPSG:28992 Amersfoort / RD New
output_projection_string = "+init=EPSG:4326"  # LatLon with WGS84 datum used by GPS units and Google Earth, officieel EPSG:4326

# Bestanden kunnen worden gevonden op: http://www.jigsaw.nl/nwb/downloads/NWB_01-07-2014.zip
shp_hectopunten = "input/Hectopunten/Hectopunten"
shp_wegvakken = "input/Wegvakken/Wegvakken"

# CSV files van de SHP files
csv_hectopunten = "output/Hectopunten.csv"
csv_wegvakken = "output/Wegvakken.csv"

# CSV output na mergen
csv_merged = "output/merged.csv"

shp_transform_to_different_projection(shp_hectopunten, HECTOPUNTEN_OUTPUT_FIELDS, input_projection_string, output_projection_string, csv_hectopunten)
shp_transform_to_different_projection(shp_wegvakken, WEGVAKKEN_OUTPUT_FIELDS, input_projection_string, output_projection_string, csv_wegvakken)

merge_shapefile_csvs(csv_hectopunten, csv_wegvakken, 'WVK_ID', MERGED_OUTPUT_FIELDS, MERGED_RENAME_FIELDS_MAPPING, csv_merged)