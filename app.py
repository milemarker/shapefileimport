__author__ = 'djvdorp'
import shapefile

hectopunten_shp = shapefile.Reader("01-07-2014/Hectopunten/Hectopunten")
hectopunten_shapes = hectopunten_shp.shapes()
print len(hectopunten_shapes)

wegvakken_shp = shapefile.Reader("01-07-2014/Wegvakken/Wegvakken")
wegvakken_shapes = wegvakken_shp.shapes()
print len(wegvakken_shapes)
