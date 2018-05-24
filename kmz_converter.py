import sys
import os
try:
    import ogr
    import osr
    import gdalconst
except:
    from osgeo import ogr
    from osgeo import osr
    from osgeo import gdalconst
import code
# code.interact(local=locals())

def kmz_converter():
    # open the input KMZ file
    kmz_file = str(sys.argv[1])
    data_source = open_kmz(kmz_file)

    # create the output shapefiles
    points_shp_name = set_output_filename(kmz_file, 'points')
    lines_shp_name = set_output_filename(kmz_file, 'lines')
    polygons_shp_name = set_output_filename(kmz_file, 'polygons')

    points_datastore = create_output_datastore(points_shp_name)
    points_layer = create_output_layer(points_datastore, ogr.wkbMultiPoint)
    add_fields(points_layer)

    lines_datastore = create_output_datastore(lines_shp_name)
    lines_layer = create_output_layer(lines_datastore, ogr.wkbMultiLineString)
    add_fields(lines_layer)

    polygons_datastore = create_output_datastore(polygons_shp_name)
    polygons_layer = create_output_layer(polygons_datastore, ogr.wkbMultiPolygon)
    add_fields(polygons_layer)

    # loop through the layers
    feature_counter = 0
    points_counter = 0
    lines_counter = 0
    polygons_counter = 0

    layer_count = data_source.GetLayerCount()
    for i in range(0, layer_count):
        layer = data_source.GetLayer(i)
        layer_info = {}
        layer_info['feature_count'] = layer.GetFeatureCount()
        layer_info['name'] = layer.GetName()

        # loop through the features in each layer
        for feature in layer:
            feature_counter += 1
            geom = feature.GetGeometryRef()
            geom_type = geom.GetGeometryName()
            field_names = ['Name', 'descriptio', 'icon', 'snippet']

            if geom_type in ('POINT', 'MULTIPOINT'):
                points_counter += 1
                layer_defn = points_layer.GetLayerDefn()
                out_feature = ogr.Feature(layer_defn)
                out_geom = ogr.ForceToMultiPoint(geom)

            elif geom_type in ('LINESTRING', 'MULTILINESTRING'):
                lines_counter += 1
                layer_defn = lines_layer.GetLayerDefn()
                out_feature = ogr.Feature(layer_defn)
                out_geom = ogr.ForceToMultiLineString(geom)

            elif geom_type in ('POLYGON', 'MULTIPOLYGON'):
                polygons_counter += 1
                layer_defn = lines_layer.GetLayerDefn()
                out_feature = ogr.Feature(layer_defn)
                out_geom = ogr.ForceToMultiPolygon(geom)

            else: continue

            # convert to 2D
            out_geom.FlattenTo2D()

            # set the output feature geometry
            out_feature.SetGeometry(out_geom)

            # set the output feature attributes
            for field_name in field_names:
                try:
                    out_feature.SetField(field_name, feature.GetField(field_name))
                except:
                    pass

            out_feature.SetField('layer_name', layer.GetName())
            out_feature.SetField('id', feature_counter)

            # write the output feature to shapefile
            if geom_type in ('POINT', 'MULTIPOINT'):
                points_layer.CreateFeature(out_feature)
            elif geom_type in ('LINESTRING', 'MULTILINESTRING'):
                lines_layer.CreateFeature(out_feature)
            elif geom_type in ('POLYGON', 'MULTIPOLYGON'):
                polygons_layer.CreateFeature(out_feature)

            # clear the output feature variable
            out_feature = None

        # reset the layer reading in case it needs to be re-read later
        layer.ResetReading()

        print layer_info['name'] , feature_counter

    # print counts
    print '\nSUMMARY COUNTS'
    print "Feature count: %s" % feature_counter
    print "Points count: %s" % points_counter
    print "Lines count: %s" % lines_counter
    print "Polygons count: %s" % polygons_counter

    # cleanup
    points_datastore = None
    points_layer = None
    lines_datastore = None
    lines_layer = None
    polygons_datastore = None
    polygons_layer = None

    # remove empty output shapefiles
    driver = ogr.GetDriverByName('ESRI Shapefile')
    if points_counter == 0:
        driver.DeleteDataSource(points_shp_name)
    if lines_counter == 0:
        driver.DeleteDataSource(lines_shp_name)
    if polygons_counter == 0:
        driver.DeleteDataSource(polygons_shp_name)

def open_kmz(kmz_file):
    driver = ogr.GetDriverByName('LIBKML')
    data_source = driver.Open(kmz_file, gdalconst.GA_ReadOnly)

    if data_source is None:
        print "Failed to open file."
        exit()

    return data_source

def set_output_filename(input_filename, geom_type):
    # set the output filename by appending the geometry type to input filename
    dir, filename = os.path.split(input_filename)
    output_filename = os.path.splitext(filename)[0] + '_' + geom_type + '.shp'
    output_shapefile = os.path.join(dir, output_filename)
    return output_shapefile

def create_output_datastore(shp_name):
    driver = ogr.GetDriverByName('ESRI Shapefile')

    # remove the shapefile if it already exists
    if os.path.exists(shp_name):
        print "Removing previous version of %s" % shp_name
        os.remove(shp_name)

    # create the shapefile
    try:
        output_datastore = driver.CreateDataSource(shp_name)
    except:
        print "Could not create shapefile %s ." % shp_name

    return output_datastore

def create_output_layer(datastore, geom_type):
    # create the output layer with SRS from input
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    new_pts_layer = datastore.CreateLayer('layer1', srs, geom_type)

    # if error creating layer, print message and exit
    if new_pts_layer is None:
        print 'Error creating layer.'
        sys.exit(1)

    return new_pts_layer

def add_fields(layer):
    # add standard KMZ fields to an existing layer
    fields = {
    'Name': 50,
    'description': 128,
    'icon': 10,
    'snippet': 128,
    'layer_name': 50
    }

    field = ogr.FieldDefn('id', ogr.OFTInteger)
    layer.CreateField(field)

    for field_name, field_length in fields.iteritems():
        field = ogr.FieldDefn(field_name, ogr.OFTString)
        field.SetWidth(field_length)
        layer.CreateField(field)

if __name__ == '__main__':
    kmz_converter()
