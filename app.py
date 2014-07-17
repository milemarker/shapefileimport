__author__ = 'djvdorp'
import shapefile
import pyproj

hectopunten_shp = shapefile.Reader("01-07-2014/Hectopunten/Hectopunten")
hectopunten_shapes = hectopunten_shp.shapes()
#print len(hectopunten_shapes)

#wegvakken_shp = shapefile.Reader("01-07-2014/Wegvakken/Wegvakken")
#wegvakken_shapes = wegvakken_shp.shapes()
#print len(wegvakken_shapes)

input_projection = pyproj.Proj("+init=EPSG:28992") # Dit is Rijksdriehoekstelsel_New vanuit de .prj files, officieel EPSG:28992 Amersfoort / RD New
output_projection = pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth, officieel EPSG:4326

index = 0
while index < 100:
    for input_point in hectopunten_shapes[index].points:
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
    index += 1