# KMZ to shapefile converter

Run it like this:

`kmz_converter.py filename.kmz`

This works if both the KMZ and the kmz_converter.py files are in the current folder.

- It works on KMZ or KML files.
- Creates 2D multipoint, multilinestring and multipolygon shapefiles for each KMZ or KML file. One shapefile for each geometry type present.
- Shapefiles include columns for name, description, and layer name.

Want to run it on multiple KMZs in the same folder? Try a commandline loop like this Windows example:

`for %f in (*.kmz) do kmz_converter.py %f`

Then merge them together in QGIS and QGIS will add a column for filename automatically
(Vector > Data management tools > Merge vector layers).
