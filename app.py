__author__ = 'djvdorp'
import shapefile
import pyproj

hectopunten_shp = shapefile.Reader("01-07-2014/Hectopunten/Hectopunten")
hectopunten_shapes = hectopunten_shp.shapes()
print len(hectopunten_shapes)

wegvakken_shp = shapefile.Reader("01-07-2014/Wegvakken/Wegvakken")
wegvakken_shapes = wegvakken_shp.shapes()
print len(wegvakken_shapes)

input_projection = pyproj.Proj("+init=EPSG:28992") # Dit is Rijksdriehoekstelsel_New vanuit de .prj files, officieel EPSG:28992 Amersfoort / RD New
output_projection = pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth, officieel EPSG:4326