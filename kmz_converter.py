import sys
import os
import ogr
import osr
import gdalconst
import code

def kmz_converter():
    kmz_file = 'Alpheus.kmz'
    kmz_file = 'doc.kml'

    data_source = open_kmz(kmz_file)

    points_datastore = create_output_datastore('Alpheus_points.shp')
    points_layer = create_output_layer(points_datastore, ogr.wkbMultiPoint)
    add_fields(points_layer)

    lines_datastore = create_output_datastore('Alpheus_lines.shp')
    lines_layer = create_output_layer(lines_datastore, ogr.wkbMultiLineString)
    add_fields(lines_layer)

    polygons_datastore = create_output_datastore('Alpheus_polygons.shp')
    polygons_layer = create_output_layer(polygons_datastore, ogr.wkbMultiPolygon)
    add_fields(polygons_layer)

    # iterate through the layers
    counter = 0
    layer_count = data_source.GetLayerCount()
    for i in range(0, layer_count):
        layer = data_source.GetLayer(i)
        layer_info = {}
        layer_info['feature_count'] = layer.GetFeatureCount()
        layer_info['name'] = layer.GetName()

        for feature in layer:
            counter += 1
            geom = feature.GetGeometryRef()
            geom_type = geom.GetGeometryName()
            field_names = ['Name', 'descriptio', 'icon', 'snippet']

            # code.interact(local=locals())

            if geom_type in ('POINT', 'MULTIPOINT'):
                pts_layer_defn = points_layer.GetLayerDefn()
                out_feature = ogr.Feature(pts_layer_defn)
                out_geom = ogr.ForceToMultiPoint(geom)
                out_feature.SetGeometry(geom)

                for field_name in field_names:
                    out_feature.SetField(field_name, feature.GetField(field_name))

                out_feature.SetField('layer_name', layer.GetName())
                out_feature.SetField('id', counter)

                points_layer.CreateFeature(out_feature)
                out_feature = None

            if geom_type in ('LINESTRING', 'MULTILINESTRING'):
                lines_layer_defn = lines_layer.GetLayerDefn()
                out_feature = ogr.Feature(lines_layer_defn)
                out_geom = ogr.ForceToMultiLineString(geom)
                out_feature.SetGeometry(out_geom)

                for field_name in field_names:
                    try:
                        out_feature.SetField(field_name, feature.GetField(field_name))
                    except:
                        pass

                out_feature.SetField('layer_name', layer.GetName())
                out_feature.SetField('id', counter)

                lines_layer.CreateFeature(out_feature)
                out_feature = None

            if geom_type in ('POLYGON', 'MULTIPOLYGON'):
                polygons_layer_defn = lines_layer.GetLayerDefn()
                out_feature = ogr.Feature(polygons_layer_defn)
                out_geom = ogr.ForceToMultiPolygon(geom)
                out_feature.SetGeometry(geom)

                for field_name in field_names:
                    out_feature.SetField(field_name, feature.GetField(field_name))

                out_feature.SetField('layer_name', layer.GetName())
                out_feature.SetField('id', counter)

                polygons_layer.CreateFeature(out_feature)
                out_feature = None


        layer.ResetReading()

        print layer_info['name'] , counter

    points_datastore = None
    points_layer = None
    lines_datastore = None
    lines_layer = None
    polygons_datastore = None
    polygons_layer = None

# >>> layer_def = layer.GetLayerDefn()
# >>> field_count = layer_def.GetFieldCount()
# >>> layer_def.GetFieldDefn(1).GetNameRef()
# 'description'
# >>> for i in range (0, field_count):
# ...   print layer_def.GetFieldDefn(i).GetNameRef()
# ...
# Name
# description
# timestamp
# begin
# end
# altitudeMode
# tessellate
# extrude
# visibility
# drawOrder
# icon


def open_kmz(kmz_file):
    # driver = ogr.GetDriverByName('LIBKML')
    driver = ogr.GetDriverByName('KML')
    data_source = driver.Open(kmz_file, gdalconst.GA_ReadOnly)

    if data_source is None:
        print "Failed to open file."
        exit()

    return data_source

def create_output_datastore(shp_name):
    # points shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    # points_shp_name = 'alpheus_points.shp'

    # remove the shapefile if it already exists
    if os.path.exists(shp_name):
        print "Removing previous version of %s" % shp_name
        os.remove(shp_name)

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
