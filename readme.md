# KMZ to shapefile converter

Converts KML and KMZ files to shapefile. Combines multiple layers into one shapefile with columns including feature name, description, and layer name.

Run it like this:  
`kmz_converter.py filename.kmz`

This works if both the KMZ and the kmz_converter.py files are in the current folder.

- It works on KMZ or KML files.
- Creates 2D multipoint, multilinestring and multipolygon shapefiles for each KMZ or KML file. One shapefile for each geometry type present. Other types may be ignored.
- Shapefiles include columns for name, description, and layer name.
- You should still check the converted shapefiles match the KMZs incase the KMZs are more wacky than anticipated.

Want to run it on multiple KMZs in the same folder? Try a commandline loop like this Windows example:

`for %f in (*.kmz) do kmz_converter.py %f`

Then merge them together in QGIS and QGIS will add a column for filename automatically
(Vector > Data management tools > Merge vector layers).

## Troubleshooting
Most errors are an issue with the GDAL or OGR installation.

#### Windows
*ERROR 4: Unable to open EPSG support file gcs.csv. Try setting the GDAL_DATA environmental variable to point to the directory containing EPSG csv files.*  
Create an environmental variable named `GDAL_DATA` and set `C:\Program Files (x86)\GDAL\gdal-data` as the value.
